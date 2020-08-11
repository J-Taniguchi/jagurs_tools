# import pprint
from glob import glob
import argparse
# import sys
import os
from datetime import timedelta

import joblib
import numpy as np
from tqdm import tqdm
import h5py
import matplotlib.pyplot as plt

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from utils.utils import read_tsun_par, read_gridfile
# pp = pprint.PrettyPrinter(width=120)

parser = argparse.ArgumentParser(description="Program to visualise bathy/disp/wave height.")

parser.add_argument("-i", "--input_file", help="grid files to visualise. You can use glob format.", required=True)
parser.add_argument("-o", "--output_dir", help="output directory. If it does not exist, it will be made automatically.", required=True)
parser.add_argument(
    "--dt",
    help="Unit is second. If specified, timestamp will be writen as title of the figure, instead of file name.",
    type=float,
    default=None)
parser.add_argument("--max_val", help="max value of color bar.", type=float, default=None)
parser.add_argument("--dpi", help="dpi of output figure.", type=int, default=200)
parser.add_argument("-y", "--yes_to_all", help="yes to all", action="store_true")
parser.add_argument("--disp", help="if you want to visualise displacement, use this flag.(visualise previous sum)", action="store_true")
parser.add_argument("-n", "--n_jobs", help="number of jobs.", type=int, default=1)

args = parser.parse_args()
input_file_list = glob(args.input_file)
output_dir = args.output_dir
dt = args.dt
max_val = args.max_val
dpi = args.dpi
yes_to_all = args.yes_to_all
n_jobs = args.n_jobs
disp = args.disp

input_file_list.sort()

print("input_file: ", input_file_list)
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

if max_val is None:
    print("checking max_val")
    max_val = 0
    for input_file in tqdm(input_file_list):
        print("input_file: ", input_file)
        with h5py.File(input_file, "r") as f:
            z = f["z"][:]
        max_val = max([max_val, np.nanmax(z), -np.nanmin(z)])
print("max_val: ", max_val)


def write_fig(i):
    input_file = input_file_list[i]
    with h5py.File(input_file, "r") as f:
        x = f["x"][:]
        y = f["y"][:]
        z = f["z"][:]
    fname_prefix = ".".join(os.path.basename(input_file).split(".")[0:-1])
    fname = os.path.join(output_dir, fname_prefix + ".png")
    fig, ax = plt.subplots()
    c = ax.pcolor(x, y, z, shading="auto", cmap="seismic", vmin=-max_val, vmax=max_val)
    if dt is None:
        ax.set_title(fname_prefix)
    else:
        td = timedelta(seconds=dt * i)
        ax.set_title(str(td))
    fig.colorbar(c, ax=ax)
    fig.tight_layout()
    plt.savefig(fname, dpi=dpi)
    plt.close()


if disp is False:
    joblib.Parallel(
        n_jobs=n_jobs,
        verbose=10,
        backend="loky")(joblib.delayed(write_fig)(
            i) for i in range(len(input_file_list)))
else:
    if dt is not None:
        td = timedelta(seconds=0)

    for input_file in tqdm(input_file_list):
        with h5py.File(input_file, "r") as f:
            x = f["x"][:]
            y = f["y"][:]
            z = f["z"][:]
        fname_prefix = ".".join(os.path.basename(input_file).split(".")[0:-1])
        fname = os.path.join(output_dir, fname_prefix + ".png")
        fig, ax = plt.subplots()
        c = ax.pcolor(x, y, z, shading="auto", cmap="seismic", vmin=-max_val, vmax=max_val)
        if dt is None:
            ax.set_title(fname_prefix)
        else:
            td = td + timedelta(seconds=dt)
            ax.set_title(str(td))
        fig.colorbar(c, ax=ax)
        fig.tight_layout()
        plt.savefig(fname, dpi=dpi)
        plt.close()


exit()
