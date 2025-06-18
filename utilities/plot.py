# Shared plotting functions

from matplotlib.lines import Line2D
import numpy as np
import matplotlib.colors as colors


# Add a line of latitude to an axes
def add_latline(ax, latitude, start, end):
    latl = (latitude + 90) / 180
    ax.add_line(
        Line2D(
            [start.timestamp(), end.timestamp()],
            [latl, latl],
            linewidth=0.75,
            color=(0.2, 0.2, 0.2, 1),
            zorder=200,
        )
    )


# Get the locatgion for a colorbar from a plot axes
def get_colorbar_location(ax):
    """
    Get the location for a colorbar based on the axes limits.
    """
    x0, y0, w, h = ax.get_position().bounds
    return [0.925, y0 + h / 20, 0.05, h * 0.9]


# Add a textured grey background to an axes
def texture_background(ax, s=(2000, 600)):
    nd2 = np.random.rand(s[1], s[0])
    clrs = []
    for shade in np.linspace(0.42 + 0.01, 0.36 + 0.01):
        clrs.append((shade, shade, shade, 1))
    yg = np.linspace(ax.get_ylim()[0], ax.get_ylim()[1], s[1])
    xg = np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], s[0])
    img = ax.pcolormesh(
        xg,
        yg,
        nd2,
        cmap=colors.ListedColormap(clrs),
        alpha=1.0,
        shading="gouraud",
        zorder=10,
    )
    return img
