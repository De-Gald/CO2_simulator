import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.collections import PolyCollection

from utils import get_vertices, get_colors


def plot_formation(
    formation: str,
    use_trapping=False
) -> None:
    vertices_formation = get_vertices(formation, 'faces', 'vertices')
    colors_formation = get_colors(formation)

    fig, ax = plt.subplots()

    face_colors = [cm.viridis(x) for x in colors_formation / 1150]

    collection = PolyCollection(
        vertices_formation,
        facecolors=face_colors,
        edgecolors='k',
        linewidths=0.1,
        alpha=0.9
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

    ax.autoscale_view()

    plt.show()


if __name__ == '__main__':
    plot_formation('utsirafm', use_trapping=True)
