import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def write_fig(x,
              y,
              z,
              fname,
              bathy=None,
              write_contour=False,
              dt=None,
              aspect=None,
              title=None,
              max_val=None,
              dpi=200
              ):
    fig, ax = plt.subplots()
    if bathy is not None:
        if write_contour:
            levels = np.arange(0, bathy.min() - 10, -10)[::-1]
        else:
            levels = [0.0]
        ax.contour(x, y, bathy, levels=levels, colors="black", linewidths=0.08)

    c = ax.pcolormesh(x, y, z, shading="auto", cmap="seismic", vmin=-max_val, vmax=max_val)

    ax.set_title(title)
    fig.colorbar(c, ax=ax)
    ax.set_aspect(aspect)
    fig.tight_layout()
    plt.savefig(fname, dpi=dpi, bbox_inches="tight")
    plt.close()
