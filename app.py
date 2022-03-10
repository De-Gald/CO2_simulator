from typing import Optional
from copy import deepcopy

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import numpy as np
import threading
import pandas as pd

from plotting.plot_trapping_distribution import LABELS
from reinforcement_learning.basic_policy_web import run_basic_policy_web
from reinforcement_learning.nn_policy_web import run_nn_policy_web

from plotting.plot_formation_web import plot_formation_web
from plotting.plot_trapping_distribution_web import plot_trapping_distribution
from simulation.explore_simulation import explore_simulation, YEAR
from simulation.gui import FORMATIONS

OPTIONS = [
    {'label': formation, 'value': formation}
    for formation in FORMATIONS
]
DEFAULT_FORMATION = FORMATIONS[13]
COLORS = ['primary', 'secondary']

app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])
app.title = 'CO2 storage simulator'
server = app.server

previous_formation_graph = {}
formation_graph = {}

previous_trapping_masses = np.array([])
trapping_masses = np.array([])
trapping_time = np.array([])

run_smart_well_location = 0
run_basic_well_location = 0

stop_smart_well_location = [True]
stop_basic_well_location = [True]

count = 0
initial_call = True

current_well_loc = (0, 0)

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
                            color='info',
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
                            id='formation_graph',
                            style={'height': '80vh'},
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
                                    value=1,
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label('Injection period', size='md'),
                                                dcc.Input(
                                                    id='injection_period',
                                                    value=10,
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
                                                    value=10,
                                                    type='number'
                                                ),
                                                dbc.Label('Migration time steps', size='md'),
                                                dcc.Input(
                                                    id='migration_time_steps',
                                                    value=5,
                                                    type='number'
                                                ),
                                                dcc.Checklist(
                                                    id='traps_checkbox',
                                                    options={
                                                        'traps': 'Show traps',
                                                    }
                                                )
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
                                                dcc.Checklist(
                                                    id='download_checkbox',
                                                    options={
                                                        'download': 'Download results',
                                                    }
                                                )
                                            ],
                                            width=6
                                        ),
                                    ]
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H5('Trapping inventory'),
                                dbc.Spinner(
                                    dcc.Graph(id='trapping_graph'),
                                    color='primary'
                                )
                            ]
                        ),
                        html.Div(
                            [
                                dcc.Interval(
                                    id='formation_updater',
                                    interval=3 * 1000,
                                    n_intervals=0,
                                    disabled=True
                                ),
                                dcc.Interval(
                                    id='trapping_graph_updater',
                                    interval=5 * 1000,
                                    n_intervals=0,
                                    disabled=True
                                ),
                                dcc.Store(id='local_formation'),
                                dcc.Store(id='local_trapping'),
                                dcc.Download(id='download_simulation_results')
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
        Output('trapping_graph', 'figure'),
        Output('download_simulation_results', 'data'),
        Output('formation_updater', 'disabled'),
        Output('trapping_graph_updater', 'disabled'),
        Output('simulation', 'n_clicks_timestamp'),
        Output('smart_well_location', 'color'),
        Output('smart_well_location', 'n_clicks_timestamp'),
        Output('basic_well_location', 'color'),
        Output('basic_well_location', 'n_clicks_timestamp'),
        Output('local_trapping', 'clear_data')
    ],
    [
        Input('simulation', 'n_clicks_timestamp'),
        Input('smart_well_location', 'n_clicks_timestamp'),
        Input('basic_well_location', 'n_clicks_timestamp'),
        Input('local_trapping', 'data')
    ],
    [
        State('formation_dropdown', 'value'),
        State('injection_rate', 'value'),
        State('injection_period', 'value'),
        State('injection_time_steps', 'value'),
        State('migration_period', 'value'),
        State('migration_time_steps', 'value'),
        State('seafloor_depth', 'value'),
        State('seafloor_temperature', 'value'),
        State('water_residual', 'value'),
        State('co2_residual', 'value'),
        State('download_checkbox', 'value')
    ],
    prevent_initial_call=True
)
def run_simulation(
    simulation: float,
    smart_well_location: float,
    basic_well_location: float,
    figure_dict: dict[str, any],
    formation: str,
    injection_rate: int,
    injection_period: int,
    injection_time_steps: int,
    migration_period: int,
    migration_time_steps: int,
    seafloor_depth: float,
    seafloor_temperature: float,
    water_residual: float,
    co2_residual: float,
    download_checkbox: list[str]
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
        masses, time = explore_simulation(
            current_well_loc,
            formation=formation,
            default_rate=injection_rate,
            inj_time=injection_period * YEAR,
            inj_steps=injection_time_steps,
            mig_time=migration_period * YEAR,
            mig_steps=migration_time_steps,
            seafloor_depth=seafloor_depth,
            seafloor_temp=seafloor_temperature,
            water_residual=water_residual,
            co2_residual=co2_residual
        )
        output = plot_trapping_distribution(masses, time)

        download = dash.no_update
        if download_checkbox:
            df = pd.DataFrame(masses, columns=time // YEAR, index=LABELS)
            download = dcc.send_data_frame(df.to_csv, "masses.csv")

        return (
            output,
            download,
            dash.no_update,
            dash.no_update,
            0,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    elif button_pressed == 2:
        global run_smart_well_location
        global stop_smart_well_location

        run_smart_well_location = bool((run_smart_well_location + 1) % 2)

        if run_smart_well_location:
            trapping_graph = dash.no_update
            local_trapping = False

            reset_formation_graph()
            reset_trapping_graph()
            stop_smart_well_location.pop()

            smart_well_location_thread = threading.Thread(
                target=run_nn_policy_web,
                name='smart_well_location',
                kwargs={
                    'formation': formation,
                    'formation_graph_callback': set_formation_graph_callback,
                    'trapping_graph_callback': set_trapping_graph_callback,
                    'stop_smart_well_location': stop_smart_well_location,
                    'default_rate': injection_rate,
                    'inj_time': injection_period * YEAR,
                    'inj_steps': injection_time_steps,
                    'mig_time': migration_period * YEAR,
                    'mig_steps': migration_time_steps,
                    'seafloor_depth': seafloor_depth,
                    'seafloor_temp': seafloor_temperature,
                    'water_residual': water_residual,
                    'co2_residual': co2_residual
                }
            )
            smart_well_location_thread.start()
        else:
            stop_smart_well_location.append(True)
            reset_formation_graph()
            reset_trapping_graph()
            trapping_graph = 'Empty graph'
            local_trapping = True

        return (
            trapping_graph,
            dash.no_update,
            not run_smart_well_location,
            not run_smart_well_location,
            dash.no_update,
            COLORS[not run_smart_well_location],
            0,
            dash.no_update,
            dash.no_update,
            local_trapping
        )

    elif button_pressed == 3:
        global run_basic_well_location
        global stop_basic_well_location

        run_basic_well_location = bool((run_basic_well_location + 1) % 2)

        if run_basic_well_location:
            trapping_graph = dash.no_update
            local_trapping = False

            reset_formation_graph()
            reset_trapping_graph()
            stop_basic_well_location.pop()

            basic_well_location_thread = threading.Thread(
                target=run_basic_policy_web,
                name='basic_well_location',
                kwargs={
                    'formation': formation,
                    'formation_graph_callback': set_formation_graph_callback,
                    'trapping_graph_callback': set_trapping_graph_callback,
                    'stop_basic_well_location': stop_basic_well_location,
                    'default_rate': injection_rate,
                    'inj_time': injection_period * YEAR,
                    'inj_steps': injection_time_steps,
                    'mig_time': migration_period * YEAR,
                    'mig_steps': migration_time_steps,
                    'seafloor_depth': seafloor_depth,
                    'seafloor_temp': seafloor_temperature,
                    'water_residual': water_residual,
                    'co2_residual': co2_residual
                }
            )
            basic_well_location_thread.start()
        else:
            stop_basic_well_location.append(True)
            reset_formation_graph()
            reset_trapping_graph()
            trapping_graph = 'Empty graph'
            local_trapping = True

        return (
            trapping_graph,
            dash.no_update,
            not run_basic_well_location,
            not run_basic_well_location,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            COLORS[not run_basic_well_location],
            0,
            local_trapping
        )

    if figure_dict:
        return (
            go.Figure(**figure_dict),
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update
        )
    else:
        raise PreventUpdate


@app.callback(
    Output('formation_graph', 'figure'),
    [
        Input('formation_graph', 'clickData'),
        Input('formation_dropdown', 'value'),
        Input('local_formation', 'data'),
        Input('traps_checkbox', 'value')
    ],
    State('formation_graph', 'figure')
)
def _plot_formation_with_well(
    click_data: Optional[dict[str, list[dict[str, float]]]],
    formation: str,
    figure_dict: dict[str, any],
    traps: list[str],
    current_figure: dict[str, any]
) -> [go.Figure, bool]:
    ctx = dash.callback_context
    triggered_input = ctx.triggered

    use_trapping = True if traps else False

    global previous_formation_graph

    if triggered_input[0]['prop_id'] == 'local_formation.data' and figure_dict:
        return go.Figure(**figure_dict)

    elif triggered_input[0]['prop_id'] == 'formation_dropdown.value':
        previous_formation_graph = plot_formation_web(formation).to_dict()
        return plot_formation_web(formation, use_trapping=use_trapping)

    elif triggered_input[0]['prop_id'] == 'formation_graph.clickData':
        x = click_data['points'][0]['x']
        y = click_data['points'][0]['y']
        marker = (x, y)

        global current_well_loc
        current_well_loc = marker

        previous_formation_graph = plot_formation_web(formation, marker=marker).to_dict()
        return plot_formation_web(formation, marker=marker, use_trapping=use_trapping)

    elif triggered_input[0]['prop_id'] == 'traps_checkbox.value':
        if use_trapping:
            previous_formation_graph = current_figure
            return plot_formation_web(formation, use_trapping=use_trapping, current_figure=current_figure)
        else:
            return go.Figure(**previous_formation_graph)

    else:
        return plot_formation_web(formation, use_trapping=use_trapping)


@app.callback(
    Output('local_formation', 'data'),
    Input('formation_updater', 'n_intervals'),
    prevent_initial_call=True
)
def dynamic_figure_update(
    n_intervals: int
) -> dict[str, any]:
    global previous_formation_graph
    formation_graph_with_colorbar = {}

    if formation_graph:
        formation_graph_with_colorbar = deepcopy(formation_graph)
        del formation_graph['data'][0]  # delete first cell with colorbar

    if formation_graph != previous_formation_graph:
        previous_formation_graph = formation_graph
        return formation_graph_with_colorbar
    else:
        return dash.no_update


@app.callback(
    Output('local_trapping', 'data'),
    Input('trapping_graph_updater', 'n_intervals'),
    prevent_initial_call=True
)
def dynamic_trapping_graph_update(
    n_intervals: int
) -> dict[str, any]:
    global previous_trapping_masses
    global count
    count += 1
    print(f'Attempt {count}')
    if not np.array_equal(trapping_masses, previous_trapping_masses):
        print(f'Attempt succeeded')
        previous_trapping_masses = trapping_masses
        return plot_trapping_distribution(trapping_masses, trapping_time).to_dict()
    else:
        return dash.no_update


def reset_formation_graph() -> None:
    global previous_formation_graph
    global formation_graph
    previous_formation_graph = {}
    formation_graph = {}


def reset_trapping_graph() -> None:
    global previous_trapping_masses
    global trapping_masses
    previous_trapping_masses = []
    trapping_masses = []


def set_formation_graph_callback(
    fig: dict[str, any]
) -> None:
    global formation_graph
    formation_graph = fig


def set_trapping_graph_callback(
    masses: np.array,
    time: np.array
) -> None:
    global trapping_masses
    global trapping_time
    trapping_masses = masses
    trapping_time = time


if __name__ == '__main__':
    app.run_server(debug=False)
