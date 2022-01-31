import matlab.engine
import numpy as np

from typing import Dict, List, Tuple
from pydantic import BaseModel

from simulation.plot_trapping_distribution import plot_trapping_distribution

YEAR = 3600 * 24 * 365.2425


class InitialParameters(BaseModel):
    formation: str = 'Utsirafm'
    rho_cref: float = 760.0
    grid_coarsening: float = 4.0
    seafloor_depth: float = 100.0
    seafloor_temp: float = 7.0
    temp_gradient: float = 35.6
    water_density: float = 1000.0
    dis_max: float = 53.0 / rho_cref
    max_num_wells: float = 1.0
    default_rate: float = 1.0
    max_rate: float = 10.0
    water_compr_val: float = 4.3e-10
    pv_mult: float = 1e-10
    water_residual: float = 0.11
    co2_residual: float = 0.21
    inj_time: float = 50.0 * YEAR
    inj_steps: float = 5.0
    mig_time: float = 100.0 * YEAR
    mig_steps: float = 5.0
    well_radius: float = 0.3
    c: float = 0.1
    outside_distance: float = 100
    use_dissolution: bool = False
    use_trapping: bool = False
    use_cap_fringe: bool = False
    well_position: Tuple[int] = []


def explore_simulation(
    xy: List[any],
    formation='utsirafm',
    eng=None,
    **kwargs
) -> Dict[Tuple[float, float], np.array]:
    if not eng:
        eng = matlab.engine.start_matlab()
        eng.addpath(eng.genpath('/Users/vladislavde-gald/PycharmProjects/CO2_simulator'))

    kwargs.update({'formation': formation})
    initial_parameters = InitialParameters(**kwargs)
    xy = list(filter(None.__ne__, xy))

    masses = {}

    for idx, well_pos in enumerate(xy):
        initial_parameters.well_position = well_pos
        eng.workspace['initial_parameters'] = initial_parameters.dict()
        masses_new, t, sol, w = eng.eval(
            'get_simulation_results(initial_parameters);', nargout=4
        )
        masses.update({
            xy[idx]: masses_new
        })

        masses_np, t_np = _convert_to_np_arrays(masses_new, t)
        plot_trapping_distribution(masses_np, t_np)

    return masses


def _convert_to_np_arrays(
    masses,
    t
) -> (np.array, np.array):
    t_np = np.array(t)
    _masses_np = np.array(masses)
    masses_np = _masses_np.reshape((len(_masses_np), len(_masses_np[0, 0])))
    return masses_np, t_np


if __name__ == '__main__':
    explore_simulation([(487000.0, 6721000.0)])
