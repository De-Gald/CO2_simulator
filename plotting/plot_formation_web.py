from typing import Optional

import plotly.graph_objects as go
from matplotlib import cm
from matplotlib.colors import to_rgb

from utils import get_colors, get_vertices

COLOUR_INTENSITY = 0.85


def plot_formation_web(
    formation: str,
    marker: Optional[tuple[float, float]] = None,
    use_trapping=False
) -> go.Figure:
    fig = go.Figure(
        layout={
            'autosize': True,
            'yaxis': {
                'visible': False,
            },
            'xaxis': {
                'visible': False,
            }
        }
    )

    vertices_formation = get_vertices(formation, 'faces', 'vertices').tolist()
    vertices_trapping = get_vertices(formation, 'faces_trapping', 'vertices_trapping')
    _colors_formation = get_colors(formation)
    colors_formation = _colors_formation / COLOUR_INTENSITY / _colors_formation.max()

    color_tuples = [
        to_rgb(cm.viridis(color))
        for color in colors_formation
    ]

    xs_formation, ys_formation = _convert_vertices_to_x_y_arrays(vertices_formation)

    i = 0
    for x, y in zip(xs_formation, ys_formation):
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                fill='toself',
                fillcolor=f'rgb{color_tuples[i]}',
                line={'width': 0},
                marker={
                    'opacity': 0,
                },
                showlegend=False,
                name=f'Cell {i}',
            ),
        )
        i += 1

    if use_trapping:
        xs_trapping, ys_trapping = _convert_vertices_to_x_y_arrays(vertices_trapping)

        i = 0
        for x, y in zip(xs_trapping, ys_trapping):
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    line={'width': 1.5},
                    marker={
                        'opacity': 0,
                        'color': 'red'
                    },
                    showlegend=False,
                    name=f'Trapping boundary',
                ),
            )
            i += 1

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
    )

    if marker:
        fig.add_trace(
            go.Scatter(
                x=[marker[0]],
                y=[marker[1]],
                marker={
                    'color': 'red',
                    'size': 13,
                    'symbol': 'cross',
                },
                showlegend=False,
            )
        )

    return fig


def _convert_vertices_to_x_y_arrays(
    vertices
) -> [list[list[any]], list[list[any]]]:
    xs = []
    ys = []
    for figure in vertices:
        figure_x = []
        figure_y = []
        for vertex in figure:
            figure_x.append(vertex[0])
            figure_y.append(vertex[1])
        xs.append(figure_x)
        ys.append(figure_y)
    return xs, ys
