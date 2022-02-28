import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objects as go

from plotting.plot_formation_web import plot_formation
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

app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])
app.title = 'CO2 storage simulator'
server = app.server

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
                            color='secondary',
                            n_clicks_timestamp='0',
                        ),
                        dbc.Button(
                            'Smart well location',
                            id='smart_well_location',
                            color='secondary',
                            n_clicks_timestamp='0',
                        ),
                        dbc.Button(
                            'Basic well location',
                            id='basic_well_location',
                            color='secondary',
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
    Output('output_graph', 'figure'),
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
def run_function(
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
) -> go.Figure:
    button_pressed = np.argmax(
        np.array(
            [
                0,
                float(simulation),
                float(smart_well_location),
                float(basic_well_location),
            ]
        )
    )

    output = 'Start'

    if button_pressed == 1:
        masses, time = explore_simulation((487000.0, 6721000.0))
        output = plot_trapping_distribution(masses, time)
    elif button_pressed == 2:
        output = 'Smart well location'
    elif button_pressed == 3:
        output = 'Basic well location'

    return output


@app.callback(
    Output('display', 'figure'),
    [Input('display', 'clickData'), Input('formation_dropdown', 'value')]
)
def _plot_formation_with_well(
    click_data: dict[str, list[dict[str, float]]],
    formation: str,
):
    marker = None
    if click_data:
        x = click_data['points'][0]['x']
        y = click_data['points'][0]['y']
        marker = (x, y)

    return plot_formation(formation, marker=marker)


if __name__ == '__main__':
    app.run_server(debug=False)
