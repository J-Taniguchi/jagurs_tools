#!/home/taniguchi-j/miniconda3/envs/jagurs_tools/bin/python
# import pprint
# from glob import glob
import argparse
# import sys
import os
from datetime import timedelta

import joblib
import numpy as np
import netCDF4

from src.vis import write_fig


def main():
    data_types = [
        "initial_displacement",
        "wave_height",
        "max_height",
        "max_velocity_x",
        "max_velocity_y",
        "velocity_x",
        "velocity_y",
        "break_phase_x",
        "break_phase_y",
    ]

    non_sequence_data_types = [
        "max_height",
        "max_velocity_x",
        "max_velocity_y"
    ]

    parser = argparse.ArgumentParser(description="Program to visualise bathy/disp/wave height.")

    parser.add_argument("-i", "--input_file", help="nc files to visualise.", required=True)
    parser.add_argument("-d", "--dataset", help="which datasset to discraibe", required=True, choices=data_types)
    parser.add_argument("-o", "--output_dir", help="output directory. If it does not exist, it will be made automatically.", required=True)
    parser.add_argument(
        "--dt",
        help="Unit is second. If specified, timestamp will be writen as title of the figure, instead of file name.",
        type=float,
        default=None)
    parser.add_argument("--max_val", help="max value of color bar.", type=float, default=None)
    parser.add_argument("--dpi", help="dpi of output figure.", type=int, default=200)
    parser.add_argument("-y", "--yes_to_all", help="yes to all", action="store_true")
    parser.add_argument("-n", "--n_jobs", help="number of jobs.", type=int, default=1)
    parser.add_argument("-b", "--bathy", help="bathy grd file. If specified, write 0m line.", type=str, default=None)
    parser.add_argument("--aspect", help="aspect ratio of the figure.", type=float, default=1)
    parser.add_argument("--contour", help="flag for write contour of terrain", action="store_true")

    args = parser.parse_args()
    input_file = args.input_file
    dataset = args.dataset
    output_dir = args.output_dir
    dt = args.dt
    max_val = args.max_val
    dpi = args.dpi
    yes_to_all = args.yes_to_all
    n_jobs = args.n_jobs
    bathy_file = args.bathy
    aspect = args.aspect
    write_contour = args.contour

    if dataset in non_sequence_data_types:
        pass
    else:
        output_dir = os.path.join(output_dir, dataset)

    if dataset == "initial_displacement":
        is_disp = True
    else:
        is_disp = False

    print("input_file: ", input_file)
    print("dataset: ", dataset)
    print("output_dir: ", output_dir)
    print("dt: ", dt)

    if os.path.exists(output_dir):
        if yes_to_all is False:
            print("output dir: {} is exists. Is it OK to overwrite? [Y/n]".format(output_dir))
            y_or_n = input()
            if y_or_n == "Y":
                pass
            else:
                print("program end.")
                exit(0)
    os.makedirs(output_dir, exist_ok=True)

    with netCDF4.Dataset(input_file, "r") as f:
        x = f.variables["lon"][:]
        y = f.variables["lat"][:]
        z = f.variables[dataset][:]

    if max_val is None:
        print("checking max_val")
        max_val = 0
        if is_disp:
            z[np.isnan(z)] = 0.0
            z = z.sum(axis=0)
            max_val = max([max_val, np.abs(np.nanmax(z)), np.abs(np.nanmin(z))])
        else:
            max_val = max([max_val, np.abs(np.nanmax(z)), np.abs(np.nanmin(z))])
    print("max_val: ", max_val)

    if bathy_file is None:
        bathy = None
    else:
        with netCDF4.Dataset(bathy_file, "r") as f:
            bathy = f.variables["z"][:]
        bathy = bathy.reshape((len(y), len(x)))
        bathy = np.flipud(bathy)

    with netCDF4.Dataset(input_file, "r") as f:
        x = f.variables["lon"][:]
        y = f.variables["lat"][:]
        z = f.variables[dataset][:]

    if dataset in non_sequence_data_types:
        domain = ".".join(os.path.basename(input_file).split(".")[0:-1])
        fname = os.path.join(output_dir, "{}_maxh.png".format(domain))
        write_fig(
            x,
            y,
            z,
            fname,
            bathy=bathy,
            write_contour=write_contour,
            dt=None,
            aspect=aspect,
            title=dataset,
            max_val=max_val,
            dpi=dpi
        )
    else:
        # make job dict list
        job_list = []
        for i in range(z.shape[0]):
            fname_prefix = "{:08}".format(i)
            now_fname = os.path.join(output_dir, fname_prefix + ".png")
            if is_disp:
                now_z = z[:i + 1, :, :].sum(axis=0)
            else:
                now_z = z[i, :, :]

            if dt is None:
                now_title = fname_prefix
            else:
                td = timedelta(seconds=dt * i)
                now_title = str(td)

            now_job = dict()
            now_job["x"] = x
            now_job["y"] = y
            now_job["z"] = now_z
            now_job["fname"] = now_fname
            now_job["bathy"] = bathy
            now_job["write_contour"] = write_contour
            now_job["dt"] = dt
            now_job["aspect"] = aspect
            now_job["title"] = now_title
            now_job["max_val"] = max_val
            now_job["dpi"] = dpi

            job_list.append(now_job)

        joblib.Parallel(
            n_jobs=n_jobs,
            verbose=10,
            # backend="loky")(joblib.delayed(write_fig)(
            backend="multiprocessing")(joblib.delayed(write_fig)(
                **job) for job in job_list)


if __name__ == "__main__":
    main()
