import pygmt
import numpy as np
a = np.ones((3,10))
print(a)

s = pygmt.clib.Session()
grd = s.virtualfile_from_matrix(a)
print(grd)
s.write_data(output="test.grd", data=grd)