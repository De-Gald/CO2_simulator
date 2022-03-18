from typing import Optional, Tuple, Dict, List

import plotly.graph_objects as go
from matplotlib import cm
from matplotlib.colors import to_rgb

from python.db_client.mongo_client import MongoDBClient

COLOUR_INTENSITY = 0.85


def plot_formation_web(
    formation: str,
    mongo_client: MongoDBClient,
    marker: Optional[Tuple[float, float]] = None,
    use_trapping=False,
    current_figure: Optional[Dict[str, any]] = None
) -> go.Figure:
    if current_figure:
        fig = go.Figure(**current_figure)
    else:
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

        vertices_formation = mongo_client.get_vertices(formation, 'faces').tolist()
        _colors_formation = mongo_client.get_colors(formation, 'depths')
        colors_formation = _colors_formation / COLOUR_INTENSITY / _colors_formation.max()

        color_tuples = [
            to_rgb(cm.viridis(color))
            for color in colors_formation
        ]

        xs_formation, ys_formation = _convert_vertices_to_x_y_arrays(vertices_formation)

        colorscale = [
            [0, f'rgb{to_rgb(cm.viridis(min(colors_formation)))}'],
            [0.5, f'rgb{to_rgb(cm.viridis(sum(colors_formation) / len(colors_formation)))}'],
            [1, f'rgb{to_rgb(cm.viridis(max(colors_formation)))}']
        ]

        i = 0
        marker_without_colorbar = {'opacity': 0}
        for x, y in zip(xs_formation, ys_formation):
            if i == 0:
                marker_with_colorbar = {
                    'colorscale': colorscale,
                    'colorbar': {'title': 'Depth'},
                    'color': _colors_formation,
                    'opacity': 0
                }
                _add_trace(fig, x, y, i, marker_with_colorbar, color_tuples[i])
            _add_trace(fig, x, y, i, marker_without_colorbar, color_tuples[i])
            i += 1

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

        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0)
        )

    if use_trapping:
        vertices_trapping = mongo_client.get_vertices(formation, 'faces_trapping')
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

    return fig


def _add_trace(
    figure: go.Figure,
    x: List[float],
    y: List[float],
    i: int,
    marker: Dict[str, any],
    fillcolor: Tuple[int, int, int]
) -> None:
    figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            fill='toself',
            fillcolor=f'rgb{fillcolor}',
            line={'width': 0},
            marker=marker,
            showlegend=False,
            name=f'Cell {i}'
        ),
    )


def _convert_vertices_to_x_y_arrays(
    vertices
) -> [List[List[any]], List[List[any]]]:
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
