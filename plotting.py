import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.collections import PolyCollection

from utils import get_vertices, get_colors

COLOUR_INTENSITY = 0.85

FORMATIONS = [
    'brentgrp', 'brynefm', 'fensfjordfm', 'gassumfm',
    'johansenfm', 'krossfjordfm', 'pliocenesand',
    'sandnesfm', 'skadefm', 'sognefjordfm', 'statfjordfm',
    'ulafm', 'utsirafm', 'stofm', 'nordmelafm', 'tubaenfm',
    'bjarmelandfm', 'arefm', 'garnfm', 'ilefm', 'tiljefm']


def plot_formation(
    formation_name: str,
    use_trapping=False
) -> None:
    vertices_formation = get_vertices(formation_name, 'faces', 'vertices')
    colors_formation = get_colors(formation_name)

    fig, ax = plt.subplots()

    face_colors = [cm.viridis(x) for x in
                   colors_formation / COLOUR_INTENSITY / colors_formation.max()]

    collection = PolyCollection(
        vertices_formation,
        facecolors=face_colors,
        edgecolors='k',
        linewidths=0.05,
        alpha=0.9
    )

    ax.add_collection(collection)

    if use_trapping:
        vertices_trapping = get_vertices(formation_name, 'faces_trapping', 'vertices_trapping')
        trapping_collection = PolyCollection(
            vertices_trapping,
            edgecolors='r',
            linewidths=0.5,
        )
        ax.add_collection(trapping_collection)

    ax.autoscale_view()

    plt.show()


if __name__ == '__main__':
    for formation in FORMATIONS:
        plot_formation(formation, use_trapping=True)
