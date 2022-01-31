from typing import Dict, List, Optional, Tuple

import numpy as np
import matlab.engine
from matplotlib import pyplot as plt

from gui import FORMATIONS, plot_formation
from reinforcement_learning.dynamic_plotting import plot_well_locations
from simulation.explore_simulation import explore_simulation
from utils import get_vertices

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


def run_basic_policy(
    formation: str
) -> [List[int], List[Tuple[int]]]:
    masses = {}
    paths = []
    rewards_different_inits = []

    eng = get_matlab_engine()

    plot_formation(formation)
    plt.show()

    vertices = get_vertices(formation, 'faces', 'vertices')
    random_centroids = get_random_centroids(vertices, CENTROIDS_COUNT)

    for episode_count, centroid in enumerate(random_centroids):
        print(f'Random initialization {episode_count}')
        x, y = centroid
        rewards_step = []
        path = []

        for step in range(NUMBER_OF_WELLS):
            print(f'Step {step}')
            current_masses = explore_simulation(
                _get_list_of_5_locations(CELL_INCREMENT, masses, x, y),
                eng=eng)
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
            plot_well_locations(formation, paths, rewards_different_inits)
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
    x: int,
    y: int
) -> List[Optional[Tuple[int]]]:
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
    run_basic_policy(FORMATIONS[11])
