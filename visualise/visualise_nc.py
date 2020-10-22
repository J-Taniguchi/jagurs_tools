#!/home/taniguchi-j/miniconda3/envs/jagurs_tools/python
# import pprint
from glob import glob
import argparse
# import sys
import os
from datetime import timedelta

import joblib
import numpy as np
from tqdm import tqdm
import netCDF4
import matplotlib.pyplot as plt

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from utils.utils import read_tsun_par, read_gridfile
# pp = pprint.PrettyPrinter(width=120)

parser = argparse.ArgumentParser(description="Program to visualise bathy/disp/wave height.")

parser.add_argument("-i", "--input_file", help="nc files to visualise.", required=True)
parser.add_argument("-d", "--dataset", help="which datasset to discraibe", required=True, choices=["bathy", "disp", "wave_height"])
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

args = parser.parse_args()
input_file = args.input_file
dataset = args.dataset
output_dir = args.output_dir
dt = args.dt
max_val = args.max_val
dpi = args.dpi
yes_to_all = args.yes_to_all
n_jobs = args.n_jobs
bathy = args.bathy

if dataset == "disp":
    disp = True
else:
    disp = False

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
    if disp:
        z[np.isnan(z)] = 0.0
        z = z.sum(axis=0)
        max_val = max([max_val, np.abs(np.nanmax(z)), np.abs(np.nanmin(z))])
    else:
        max_val = max([max_val, np.abs(np.nanmax(z)), np.abs(np.nanmin(z))])
print("max_val: ", max_val)


if bathy is not None:
    with netCDF4.Dataset(bathy, "r") as f:
        b = f.variables["z"][:]
    b = b.reshape((len(y), len(x)))
    b = np.flipud(b)


def write_fig(i):
    fname_prefix = ".".join(os.path.basename(input_file).split(".")[0:-1]) + "_{:08}".format(i)
    fname = os.path.join(output_dir, fname_prefix + ".png")
    fig, ax = plt.subplots()
    if disp:
        c = ax.pcolor(x, y, z[:i + 1, :, :].sum(axis=0), shading="auto", cmap="seismic", vmin=-max_val, vmax=max_val)
    else:
        c = ax.pcolor(x, y, z[i, :, :], shading="auto", cmap="seismic", vmin=-max_val, vmax=max_val)

    if bathy is not None:
        ax.contour(x, y, b, levels=[0.0], colors="black", alpha=0.8, linewidths=0.5)

    if dt is None:
        ax.set_title(fname_prefix)
    else:
        td = timedelta(seconds=dt * i)
        ax.set_title(str(td))
    fig.colorbar(c, ax=ax)
    fig.tight_layout()
    plt.savefig(fname, dpi=dpi)
    plt.close()


with netCDF4.Dataset(input_file, "r") as f:
    x = f.variables["lon"][:]
    y = f.variables["lat"][:]
    z = f.variables[dataset][:]

joblib.Parallel(
    n_jobs=n_jobs,
    verbose=10,
    backend="loky")(joblib.delayed(write_fig)(
        i) for i in range(z.shape[0]))


exit()
