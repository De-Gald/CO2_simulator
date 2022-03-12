import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.collections import PolyCollection

from python.utils import get_vertices, get_colors

COLOUR_INTENSITY = 0.85


def plot_formation(
    formation: str,
    gui=None,
    set_callbacks=False,
    callback_func=None,
    show_well=False,
    use_trapping=False
) -> [plt.Figure, plt.axis]:
    vertices_formation = get_vertices(formation, 'faces', 'vertices')
    colors_formation = get_colors(formation)

    fig, ax = plt.subplots()
    fig.set_dpi(93)

    face_colors = [
        cm.viridis(x) for x in
        colors_formation / COLOUR_INTENSITY / colors_formation.max()
    ]

    collection = PolyCollection(
        vertices_formation,
        facecolors=face_colors,
        edgecolors='k',
        linewidths=0.05,
        alpha=0.9,
        picker=10
    )

    ax.add_collection(collection)

    if use_trapping:
        vertices_trapping = get_vertices(formation, 'faces_trapping', 'vertices_trapping')
        trapping_collection = PolyCollection(
            vertices_trapping,
            edgecolors='r',
            linewidths=0.5,
        )
        ax.add_collection(trapping_collection)

    if show_well:
        ax.scatter(gui.well_x, gui.well_y, c='k', marker='x')
        ax.annotate('Well', (gui.well_x, gui.well_y), textcoords="offset points", xytext=(0, 3))

    if set_callbacks:
        fig.canvas.callbacks.connect(
            'pick_event',
            lambda event: callback_func(event, gui, formation)
        )

    ax.autoscale_view()

    return fig, ax
