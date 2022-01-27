import numpy as np
from numpy import genfromtxt


def get_vertices(
    formation: str,
    faces_file: str,
    vertices_file: str
) -> np.array:
    faces = genfromtxt(f'formations/{formation}/{faces_file}.csv', delimiter=',')
    _vertices = genfromtxt(f'formations/{formation}/{vertices_file}.csv', delimiter=',')

    vertices = np.delete(_vertices, [2], 1)

    vertices_new = np.zeros((len(faces), len(faces[0]), 2))

    for i, face in enumerate(faces):
        for j, vertex in enumerate(face):
            vertices_new[i, j, 0] = vertices[int(vertex - 1), 0]
            vertices_new[i, j, 1] = vertices[int(vertex - 1), 1]

    return vertices_new


def get_colors(formation: str) -> np.array:
    return genfromtxt(f'formations/{formation}/colours.csv', delimiter=',')
