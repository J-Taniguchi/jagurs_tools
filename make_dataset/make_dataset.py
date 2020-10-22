import os
import pygmt
import numpy as np

out_dir = "./datasets1"
os.makedirs(out_dir, exist_ok=True)

out_grid_name = os.path.join(out_dir, "bathy.grd=cf")
out_disp_name = os.path.join(out_dir, "disp.grd=cf")
out_bank_name = os.path.join(out_dir, "bank.txt")
wod_name = os.path.join(out_dir, "wod.grd=cf")

# =========================================================================================
bathy = np.ones((100, 100))
bathy[:4, 50:] = -10.0
bathy[-4:, 50:] = -10.0
bathy[:, -4:] = -10.0

bathy = np.ascontiguousarray(bathy, np.float32)
xmin = 1
xmax = 100
ymin = 1
ymax = 100

wesn = [
    xmin,
    xmax,
    ymin,
    ymax,
    bathy.min(),
    bathy.max()
]

with pygmt.clib.Session() as ses:
    ptr = ses.create_data("GMT_IS_MATRIX", "GMT_IS_SURFACE", "GMT_CONTAINER_ONLY", dim=[100, 100], inc=[1, 1], ranges=[1, 100, 1, 100])
    ses.put_matrix(ptr, bathy)
    ses.write_data("GMT_IS_MATRIX", "GMT_IS_SURFACE", "GMT_IS_OUTPUT", wesn, output=out_grid_name, data=ptr)

# =========================================================================================
wod = np.ones((100, 100))
wod[:, 50:] = -1

wod = np.ascontiguousarray(wod, np.float32)
xmin = 1
xmax = 100
ymin = 1
ymax = 100

wesn = [
    xmin,
    xmax,
    ymin,
    ymax,
    wod.min(),
    wod.max()
]

with pygmt.clib.Session() as ses:
    ptr = ses.create_data("GMT_IS_MATRIX", "GMT_IS_SURFACE", "GMT_CONTAINER_ONLY", dim=[100, 100], inc=[1, 1], ranges=[1, 100, 1, 100])
    ses.put_matrix(ptr, wod)
    ses.write_data("GMT_IS_MATRIX", "GMT_IS_SURFACE", "GMT_IS_OUTPUT", wesn, output=wod_name, data=ptr)


# =========================================================================================
disp = np.zeros((100, 100))
disp[:, 20:31] = 2

disp = np.ascontiguousarray(disp, np.float32)
xmin = 1
xmax = 100
ymin = 1
ymax = 100

wesn = [
    xmin,
    xmax,
    ymin,
    ymax,
    disp.min(),
    disp.max()
]

with pygmt.clib.Session() as ses:
    ptr = ses.create_data("GMT_IS_MATRIX", "GMT_IS_SURFACE", "GMT_CONTAINER_ONLY", dim=[100, 100], inc=[1, 1], ranges=[1, 100, 1, 100])
    ses.put_matrix(ptr, disp)
    ses.write_data("GMT_IS_MATRIX", "GMT_IS_SURFACE", "GMT_IS_OUTPUT", wesn, output=out_disp_name, data=ptr)


bank_height = 0.5
direction = 1
bank = []
x = 50
for y in range(1, 101):
    bank.append([y, x, direction, bank_height])
bank = np.array(bank)
np.savetxt(out_bank_name, bank, delimiter=",")