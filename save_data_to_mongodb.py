from numpy import genfromtxt
import json
import os

from python.simulation.gui import FORMATIONS


def get_csv_file(formation, file):
    return genfromtxt(
        f'python/formations/{formation}/{file}.csv',
        delimiter=','
    )


formations_json_array = []
formations_data_json_array = []
for i, formation in enumerate(FORMATIONS):
    depths_array = get_csv_file(formation, 'colours').tolist()
    faces_array = get_csv_file(formation, 'faces').tolist()
    faces_trapping_array = get_csv_file(formation, 'faces_trapping').tolist()
    vertices_array = get_csv_file(formation, 'vertices').tolist()

    formations_data_json_array.append({
        'formation_id': i,
        'coarsening': 4,
        'depths': depths_array,
        'faces': faces_array,
        'faces_trapping': faces_trapping_array,
        'vertices': vertices_array
    })

    formations_json_array.append({
        '_id': i,
        'formation': formation
    })

with open('formations_data.json', 'w') as f:
    json.dump(formations_data_json_array, f)

with open('formations.json', 'w') as f:
    json.dump(formations_json_array, f)

os.system('mongoimport --jsonArray -d co2sim -c formations_data formations_data.json')
os.system('mongoimport --jsonArray -d co2sim -c formations formations.json')
