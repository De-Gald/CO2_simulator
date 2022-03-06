import matlab.engine
import numpy as np

from pydantic import BaseModel

from plotting.plot_trapping_distribution import plot_trapping_distribution

YEAR = 3600 * 24 * 365.2425
KILOGRAM = 1000
MEGA = KILOGRAM * 10 ** 6


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
    well_position: tuple[float, float] = None


def explore_simulation(
    well_pos: tuple[float, float],
    formation='utsirafm',
    show_plot=False,
    eng=None,
    **kwargs
) -> (np.array, np.array):
    if not eng:
        eng = matlab.engine.start_matlab()
        eng.addpath(eng.genpath('/Users/vladislavde-gald/PycharmProjects/CO2_simulator'))
        eng.evalc("warning('off', 'all');")

    kwargs.update({'formation': formation})
    initial_parameters = InitialParameters(**kwargs)

    initial_parameters.well_position = well_pos
    eng.workspace['initial_parameters'] = initial_parameters.dict()
    masses_new, t, sol, w = eng.eval(
        'get_simulation_results(initial_parameters);', nargout=4
    )

    _masses_np, t_np = _convert_to_np_arrays(masses_new, t)
    masses_np = _convert_masses_to_mega(_masses_np)
    plot_trapping_distribution(masses_np, t_np, show_plot=show_plot)

    return masses_np, t_np


def _convert_masses_to_mega(
    masses: np.array
) -> np.array:
    masses_mega = masses / MEGA

    masses_mega_transposed = masses_mega.transpose()
    _masses_mega_transposed = np.delete(masses_mega_transposed, [0, 5], 0)
    return np.around(_masses_mega_transposed).astype(int)


def _convert_to_np_arrays(
    masses: np.array,
    t: np.array
) -> (np.array, np.array):
    t_np = np.array(t)
    _masses_np = np.array(masses)
    masses_np = _masses_np.reshape((len(_masses_np), len(_masses_np[0, 0])))
    return masses_np, t_np


if __name__ == '__main__':
    explore_simulation((487000.0, 6721000.0), show_plot=True)
