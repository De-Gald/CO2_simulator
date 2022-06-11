import matplotlib.pyplot as plt
from python.desktop.gui import FORMATIONS, plot_formation

WELL_LOCS = [[(909200.42896692, 7961347.201625), (909200.42896692, 7963347.201625), (911200.42896692, 7963347.201625),
              (911200.42896692, 7965347.201625), (911200.42896692, 7967347.201625), (911200.42896692, 7965347.201625),
              (911200.42896692, 7963347.201625), (913200.42896692, 7963347.201625), (913200.42896692, 7965347.201625),
              (913200.42896692, 7967347.201625)]]
REWARDS = [[13, 27, 42, 44, 29, 44, 42, 57, 57, 49]]


def plot_well_locations(
    formation: str,
    well_locs=None,
    rewards=None
) -> None:
    _, ax = plot_formation(formation, use_trapping=True)
    well_x = []
    well_y = []
    wells_for_annotation = []

    if well_locs:
        count = -1
        for centroid_group in well_locs:
            wells_for_annotation.append(count)
            for well_loc in centroid_group:
                count += 1
                x, y = well_loc
                well_x.append(x)
                well_y.append(y)
    if rewards:
        rewards_flatten = [
            reward_step if reward_step > 0 else 0
            for rewards_centroid in rewards
            for reward_step in rewards_centroid
        ]
        ax.scatter(well_x, well_y, c='r', s=rewards_flatten)

        for i in wells_for_annotation:
            label = str(rewards_flatten[i])
            ax.annotate(
                label,
                (well_x[i], well_y[i]),
                textcoords="offset points",
                xytext=(0, 8)
            )
    plt.show()


if __name__ == '__main__':
    plot_well_locations(FORMATIONS[13], well_locs=WELL_LOCS, rewards=REWARDS)
