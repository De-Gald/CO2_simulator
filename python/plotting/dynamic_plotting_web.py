from python.simulation.gui import FORMATIONS
from python.plotting.plot_formation_web import plot_formation_web
import plotly.graph_objects as go


def plot_well_locations_web(
    formation: str,
    well_locs=None,
    rewards=None,
    figure_callback=None
) -> None:
    fig = plot_formation_web(formation)
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
        fig.add_trace(
            go.Scatter(
                x=well_x,
                y=well_y,
                line={'width': 0},
                marker={
                    'color': 'red',
                    'size': rewards_flatten,
                    'symbol': 'circle'
                },
                showlegend=False
            ),
        )

        labels_num = list(map(rewards_flatten.__getitem__, wells_for_annotation))
        labels_str = list(map(str, labels_num))
        well_x_annotated = list(map(well_x.__getitem__, wells_for_annotation))
        well_y_annotated = list(map(well_y.__getitem__, wells_for_annotation))
        fig.add_trace(go.Scatter(
            x=well_x_annotated,
            y=well_y_annotated,
            mode="markers+text",
            text=labels_str,
            textposition="top right",
            showlegend=False
        ))
    if figure_callback:
        figure_callback(fig.to_dict())


if __name__ == '__main__':
    plot_well_locations_web(FORMATIONS[13])
