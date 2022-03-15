import numpy as np
from pymongo import MongoClient


class MongoDBClient:
    def __init__(
        self,
        db: str
    ) -> None:
        self.client = MongoClient('mongodb://mongodb:27017')
        self.db = self.client[db]

    def get_vertices(
        self,
        formation: str,
        faces_type: str
    ) -> np.array:

        formation_id = self.db.formations.find_one({'formation': formation})['_id']
        formation_data = self.db.formations_data.find_one({'formation_id': formation_id})

        _vertices = formation_data['vertices']
        faces = formation_data[faces_type]

        vertices = np.delete(_vertices, [2], 1)

        vertices_new = np.zeros((len(faces), len(faces[0]), 2))

        for i, face in enumerate(faces):
            for j, vertex in enumerate(face):
                vertices_new[i, j, 0] = vertices[int(vertex - 1), 0]
                vertices_new[i, j, 1] = vertices[int(vertex - 1), 1]

        return vertices_new

    def get_colors(
        self,
        formation: str,
        color_type: str
    ) -> np.array:
        formation_id = self.db.formations.find_one({'formation': formation})['_id']
        formation_data = self.db.formations_data.find_one({'formation_id': formation_id})

        return np.array(formation_data[color_type])
