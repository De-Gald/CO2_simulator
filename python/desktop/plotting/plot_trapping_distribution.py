import numpy as np
import matplotlib.pyplot as plt

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
YEAR = 365 * DAY

LABELS = [
    'Structural residual',
    'Residual',
    'Residual in plume',
    'Structural plume',
    'Free plume',
    'Exited'
]


def plot_trapping_distribution(
    masses_np: np.array,
    t_np: np.array,
    show_plot=False
) -> None:
    try:
        t_years = t_np // YEAR
    except TypeError:
        print('Only numpy arrays are allowed!!!')
        raise

    if show_plot:
        color_map = ['#2BBD00', '#97A5FF', '#9FFF59', '#FFF51D', '#FE9B49', '#D90000']

        plt.close('all')
        try:
            plt.stackplot(t_years, masses_np, colors=color_map)
            plt.autoscale(enable=True, axis='both', tight=True)
            plt.xlabel('Years since simulation start', fontsize=11)
            plt.legend(LABELS, loc='upper left')
            plt.ylabel('Mass (MT)', fontsize=11)
            plt.show()
        except ValueError:
            print("Arrays are incompatible!!!")
            raise
