from typing import Optional

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import numpy as np
import threading
from reinforcement_learning.nn_policy import run_nn_policy

from plotting.plot_formation_web import plot_formation_web
from plotting.plot_trapping_distribution_web import plot_trapping_distribution
from simulation.explore_simulation import explore_simulation

FORMATIONS = [
    'Brentgrp', 'Brynefm', 'Fensfjordfm', 'Gassumfm',
    'Johansenfm', 'Krossfjordfm', 'Pliocenesand',
    'Sandnesfm', 'Skadefm', 'Sognefjordfm', 'Statfjordfm',
    'Ulafm', 'Utsirafm', 'Stofm', 'Nordmelafm', 'Tubaenfm',
    'Bjarmelandfm', 'Arefm', 'Qarnfm', 'Ilefm', 'Tiljefm'
]

OPTIONS = [
    {'label': formation, 'value': formation}
    for formation in FORMATIONS
]
DEFAULT_FORMATION = FORMATIONS[13]
COLORS = ['primary', 'secondary']
FIRST_ELEMENT = 'DELETE THIS ELEMENT TO STOP EXECUTION OF THE FUNCTION'

app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])
app.title = 'CO2 storage simulator'
server = app.server

previous_figure = {}
figure = {}

run_smart_well_location = 0
run_basic_well_location = 0

stop_smart_well_location = []

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3(
                            'CO2 storage simulator',
                        ),
                        html.Span(
                            'Choose a formation from the list below:'
                        ),
                        dcc.Dropdown(
                            id='formation_dropdown',
                            options=OPTIONS,
                            value=DEFAULT_FORMATION,
                            style={
                                'width': '175px',
                            }
                        ),
                    ],
                ),
                dbc.Col(
                    [
                        html.H5('Running options'),
                        dbc.Button(
                            'Simulation',
                            id='simulation',
                            color=COLORS[0],
                            n_clicks_timestamp='0',
                        ),
                        dbc.Button(
                            'Smart well location',
                            id='smart_well_location',
                            color=COLORS[1],
                            n_clicks_timestamp='0',
                        ),
                        dbc.Button(
                            'Basic well location',
                            id='basic_well_location',
                            color=COLORS[1],
                            n_clicks_timestamp='0',
                        ),
                    ],
                    width=4
                )
            ],
            justify='between',
            align='end'
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Spinner(
                        dcc.Graph(
                            id='display',
                            style={'height': '80vh'}
                        ),
                        color='primary',
                    ),
                    width=8,
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H5('Initial parameters'),
                                html.P('Injection rate:'),
                                dcc.Slider(
                                    id='injection_rate',
                                    min=1,
                                    max=10,
                                    step=1,
                                    value=10,
                                ),
                                dbc.Row([
                                    dbc.Col(
                                        [
                                            dbc.Label('Injection period', size='md'),
                                            dcc.Input(
                                                id='injection_period',
                                                value=50,
                                                type='number'
                                            ),
                                            dbc.Label('Injection time steps', size='md'),
                                            dcc.Input(
                                                id='injection_time_steps',
                                                value=5,
                                                type='number'
                                            ),
                                            dbc.Label('Migration period', size='md'),
                                            dcc.Input(
                                                id='migration_period',
                                                value=100,
                                                type='number'
                                            ),
                                            dbc.Label('Migration time steps', size='md'),
                                            dcc.Input(
                                                id='migration_time_steps',
                                                value=5,
                                                type='number'
                                            ),
                                            dcc.Checklist(
                                                id='checklist_params',
                                                options=[
                                                    {'label': 'Use dissolution', 'value': 'use_dissolution'},
                                                ],
                                            ),
                                        ],
                                        width=6
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label('Seafloor depth', size='md'),
                                            dcc.Input(
                                                id='seafloor_depth',
                                                value=100,
                                                type='number'
                                            ),
                                            dbc.Label('Seafloor temperature', size='md'),
                                            dcc.Input(
                                                id='seafloor_temperature',
                                                value=7,
                                                type='number'
                                            ),
                                            dbc.Label('Water residual', size='md'),
                                            dcc.Input(
                                                id='water_residual',
                                                value=0.11,
                                                type='number'
                                            ),
                                            dbc.Label('CO2 residual', size='md'),
                                            dcc.Input(
                                                id='co2_residual',
                                                value=0.21,
                                                type='number'
                                            ),
                                        ],
                                        width=6
                                    ),
                                ]),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H5('Trapping inventory'),
                                dbc.Spinner(
                                    [
                                        dcc.Graph(id='output_graph'),
                                    ],
                                    color='primary'
                                )
                            ]
                        ),
                        html.Div(
                            [
                                dcc.Interval(
                                    id='figure_updater',
                                    interval=3 * 1000,
                                    n_intervals=0,
                                    disabled=True
                                ),
                                dcc.Interval(
                                    id='text_updater',
                                    interval=3 * 1000,
                                    n_intervals=0,
                                    disabled=True
                                ),
                                dcc.Store(id='local_figure', storage_type='session'),
                                dcc.Store(id='local_text', storage_type='session')
                            ]
                        )
                    ],
                    width=4,
                ),
            ],
        ),
        html.Hr(),
    ],
    fluid=True,
)


@app.callback(
    [
        Output('output_graph', 'figure'),
        Output('figure_updater', 'disabled'),
        Output('smart_well_location', 'color'),
        Output('basic_well_location', 'color')
    ],
    [
        Input('simulation', 'n_clicks_timestamp'),
        Input('smart_well_location', 'n_clicks_timestamp'),
        Input('basic_well_location', 'n_clicks_timestamp')
    ],
    [
        State('injection_rate', 'value'),
        State('injection_period', 'value'),
        State('injection_time_steps', 'value'),
        State('migration_period', 'value'),
        State('migration_time_steps', 'value'),
        State('seafloor_depth', 'value'),
        State('seafloor_temperature', 'value'),
        State('water_residual', 'value'),
        State('co2_residual', 'value')
    ],
)
def run_simulation(
    simulation: float,
    smart_well_location: float,
    basic_well_location: float,
    injection_rate: int,
    injection_period: int,
    injection_time_steps: int,
    migration_period: int,
    migration_time_steps: int,
    seafloor_depth: float,
    seafloor_temperature: float,
    water_residual: float,
    co2_residual: float
) -> [go.Figure, bool]:
    button_pressed = np.argmax(
        np.array(
            [
                0,
                float(simulation),
                float(smart_well_location),
                float(basic_well_location)
            ]
        )
    )

    if button_pressed == 1:
        masses, time = explore_simulation((487000.0, 6721000.0))
        output = plot_trapping_distribution(masses, time)
        return (
            output,
            dash.no_update,
            dash.no_update,
            dash.no_update
        )
    elif button_pressed == 2:
        global run_smart_well_location
        run_smart_well_location = bool((run_smart_well_location + 1) % 2)
        global stop_smart_well_location
        if run_smart_well_location:
            stop_smart_well_location.append(FIRST_ELEMENT)
            smart_well_location_thread = threading.Thread(
                target=run_nn_policy,
                name='smart_well_location',
                kwargs={
                    'formation': DEFAULT_FORMATION,
                    'figure_callback': set_figure_callback,
                    'stop_smart_well_location': stop_smart_well_location
                }
            )
            smart_well_location_thread.start()
        else:
            stop_smart_well_location.pop()
        return (
            dash.no_update,
            not run_smart_well_location,
            COLORS[not run_smart_well_location],
            dash.no_update
        )
    elif button_pressed == 3:
        global run_basic_well_location
        run_basic_well_location = bool((run_basic_well_location + 1) % 2)
        return (
            dash.no_update,
            not run_basic_well_location,
            dash.no_update,
            COLORS[not run_basic_well_location]
        )
    else:
        raise PreventUpdate


@app.callback(
    Output('display', 'figure'),
    [
        Input('display', 'clickData'),
        Input('formation_dropdown', 'value'),
        Input('local_figure', 'data')
    ],
)
def _plot_formation_with_well(
    click_data: Optional[dict[str, list[dict[str, float]]]],
    formation: str,
    figure_dict: dict[str, any]
) -> [go.Figure, bool]:
    if figure_dict:
        return go.Figure(**figure_dict)

    marker = None
    if click_data:
        x = click_data['points'][0]['x']
        y = click_data['points'][0]['y']
        marker = (x, y)

    return plot_formation_web(formation, marker=marker)


@app.callback(
    Output('local_figure', 'data'),
    Input('figure_updater', 'n_intervals')
)
def dynamic_figure_update(
    n_intervals: int
) -> dict[str, any]:
    global previous_figure
    if figure != previous_figure:
        previous_figure = figure
        return figure
    else:
        return dash.no_update


def reset_figure_callback() -> None:
    global previous_figure
    global figure
    previous_figure = {}
    figure = {}


def set_figure_callback(
    fig: dict[str, any]
) -> None:
    global figure
    figure = fig


if __name__ == '__main__':
    app.run_server(debug=False)
