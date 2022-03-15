from typing import Dict, List, Optional, Tuple, Callable

import numpy as np
import matlab.engine

from python.db_client.mongo_client import MongoDBClient
from python.web.plotting.dynamic_plotting_web import plot_well_locations_web
from python.web.simulation.explore_simulation import explore_simulation

FORMATIONS = [
    'Arefm', 'Bjarmelandfm', 'Brentgrp', 'Brynefm', 'Fensfjordfm', 'Garnfm', 'Gassumfm', 'Ilefm',
    'Johansenfm', 'Krossfjordfm', 'Nordmelafm', 'Pliocenesand', 'Sandnesfm', 'Skadefm', 'Sognefjordfm',
    'Statfjordfm', 'Stofm', 'Tiljefm', 'Tubaenfm', 'Ulafm', 'Utsirafm'
]

STRUCTURAL_RESIDUAL = 0
RESIDUAL = 1
RESIDUAL_IN_PLUME = 2
STRUCTURAL_PLUME = 3
FREE_PLUME = 4
EXITED = 5

STEP_NUMBER = 10

CELLS_STEPS = 1
CELL_INCREMENT = 2000 * CELLS_STEPS
CENTROIDS_COUNT = 5
NUMBER_OF_WELLS = 5

WELL_INDEX = 0


def basic_policy(
    masses_dict: Dict[Tuple[float, float], np.array]
) -> List[int]:
    rewards = get_rewards(masses_dict)
    possible_locations = _get_possible_locations(masses_dict, rewards)

    random_index = np.random.choice(len(possible_locations), 1)[0]
    return possible_locations[random_index]


def run_basic_policy_web(
    formation_graph_callback: Optional[Callable] = None,
    trapping_graph_callback: Optional[Callable] = None,
    stop_basic_well_location: Optional[list[any]] = None,
    **simulation_parameters
) -> [List[int], List[Tuple[int]]]:
    masses = {}
    paths = []
    rewards_different_inits = []

    eng = get_matlab_engine()
    formation = simulation_parameters['formation']

    mongo_client = MongoDBClient('co2sim')
    vertices = mongo_client.get_vertices(formation, 'faces')
    random_centroids = get_random_centroids(vertices, CENTROIDS_COUNT)

    for episode_count, centroid in enumerate(random_centroids):
        print(f'Random initialization {episode_count}')
        x, y = centroid
        rewards_step = []
        path = []

        for step in range(NUMBER_OF_WELLS):
            print(f'Step {step}')
            _list_of_5_locations = _get_list_of_5_locations(CELL_INCREMENT, masses, x, y)
            list_of_5_locations = list(filter(None, _list_of_5_locations))
            current_masses = {}
            for location in list_of_5_locations:
                _masses, time = explore_simulation(
                    location,
                    eng=eng,
                    **simulation_parameters
                )
                current_masses.update(
                    {
                        location: _masses
                    }
                )

                if trapping_graph_callback:
                    trapping_graph_callback(_masses, time)

                if stop_basic_well_location:
                    return

            masses.update(current_masses)

            rewards = get_rewards(current_masses)
            if len(rewards) > 0:
                print(rewards)
            else:
                break

            if (
                len(rewards_step) >= 1
                and rewards[WELL_INDEX] == rewards_step[-1]
                or all([el < 0 for el in rewards])
            ):
                break

            rewards_step.append(rewards[0])
            path.append((x, y))

            masses_copy = masses.copy()

            del masses_copy[(x, y)]
            x, y = basic_policy(masses_copy)

        if rewards_step:
            rewards_different_inits.append(rewards_step)
        if path:
            paths.append(path)
            plot_well_locations_web(
                formation,
                paths,
                rewards_different_inits,
                figure_callback=formation_graph_callback
            )
    return rewards_different_inits, paths


def get_random_centroids(
    vertices: np.array,
    centroids_count: int
) -> List[matlab.double]:
    random_indices = np.random.choice(len(vertices), centroids_count, replace=False)
    random_centroids = [vertices[idx].mean(axis=0).tolist() for idx in random_indices]
    return random_centroids


def get_matlab_engine() -> matlab.engine:
    eng = matlab.engine.start_matlab()
    eng.addpath(eng.genpath('/Users/vladislavde-gald/PycharmProjects/CO2_simulator'))
    eng.evalc("warning('off', 'all');")

    return eng


def get_rewards(
    masses_dict: Dict[Tuple[float, float], np.array]
) -> np.array:
    masses_vals = list(masses_dict.values())
    masses_sr = [masses_val[STRUCTURAL_RESIDUAL, STEP_NUMBER] for masses_val in masses_vals]
    masses_leaked = [masses_val[EXITED, STEP_NUMBER] for masses_val in masses_vals]
    rewards = np.subtract(masses_sr, masses_leaked)
    return rewards


def _get_list_of_5_locations(
    cell_increment: int,
    masses: Dict[str, np.array],
    x: float,
    y: float
) -> List[Optional[Tuple[float, float]]]:
    return [
        (x, y)
        if (x, y) not in masses.keys() else None,
        (x, y + cell_increment)
        if (x, y + cell_increment) not in masses.keys() else None,
        (x, y - cell_increment)
        if (x, y - cell_increment) not in masses.keys() else None,
        (x + cell_increment, y)
        if (x + cell_increment, y) not in masses.keys() else None,
        (x - cell_increment, y)
        if (x - cell_increment, y) not in masses.keys() else None,
    ]


def _get_possible_locations(
    masses_dict: Dict[Tuple[float, float], np.array],
    rewards: np.array
) -> List[List[int]]:
    _idxs_max = np.argwhere(rewards == np.amax(rewards))
    idxs_max = [el[0] for el in _idxs_max]
    locations = np.array(list(masses_dict.keys()))
    return locations[idxs_max].tolist()


if __name__ == '__main__':
    run_basic_policy_web(FORMATIONS[13])
