import pprint
import sys
import os

import h5py
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.utils import read_tsun_par, read_gridfile

pp = pprint.PrettyPrinter(width=120)

result_dir = "../result_sample"

gridfile_path = os.path.join(result_dir, "gridfile.dat")
tsun_par_path = os.path.join(result_dir, "tsun.par")

tsun_par = read_tsun_par(tsun_par_path)
gridfile = read_gridfile(gridfile_path)
print("=====tsun.par=====")
pp.pprint(tsun_par)
print("=====gridfile.dat=====")
pp.pprint(gridfile)

for ID in gridfile["ID"]:
    print(ID)
    with h5py.File(os.path.join(result_dir, "{}.nc".format(ID)), "r") as f:
        print(f.keys())
        lat = f["lat"][:]
        lon = f["lon"][:]
        max_height = f["max_height"][:]
        wave_height = f["wave_height"][:] # [T,Y,X]
        initial_displacement = f["initial_displacement"][:]
        time = f["time"][:]

    for i in range(initial_displacement.shape[0]):
        now_disp = initial_displacement[0, :, :]
        fig, ax = plt.subplots()
        ax.pcolor(now_disp)
        plt.savefig("test.png")
        plt.close()
        exit()

    pp.pprint(initial_displacement.shape)
    pp.pprint(lat.shape)