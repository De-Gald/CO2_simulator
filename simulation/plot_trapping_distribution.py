import numpy as np
import matplotlib.pyplot as plt

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
YEAR = 365 * DAY

KILOGRAM = 1000
MEGA = KILOGRAM * 10 ** 6


def plot_trapping_distribution(
    masses_np: np.array,
    t_np: np.array
) -> np.array:
    try:
        masses_mega = masses_np / MEGA
    except TypeError:
        print('Only numpy arrays are allowed!!!')
        raise

    masses_mega_transposed = masses_mega.transpose()
    _masses_mega_transposed = np.delete(masses_mega_transposed, [0, 5], 0)
    masses_mega_transposed = np.around(_masses_mega_transposed).astype(int)

    t_years = t_np // YEAR

    labels = [
        'Structural residual',
        'Residual',
        'Residual in plume',
        'Structural plume',
        'Free plume',
        'Exited'
    ]

    color_map = ['#2BBD00', '#97A5FF', '#9FFF59', '#FFF51D', '#FE9B49', '#D90000']

    plt.close('all')
    try:
        plt.stackplot(t_years, masses_mega_transposed, colors=color_map)
        plt.autoscale(enable=True, axis='both', tight=True)
        plt.xlabel('Years since simulation start', fontsize=11)
        plt.legend(labels, loc='upper left')
        plt.ylabel('Mass (MT)', fontsize=11)
        plt.show()
    except ValueError:
        print("Arrays are incompatible!!!")
        raise

    return masses_mega_transposed
