import numpy as np
import plotly.graph_objects as go

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
YEAR = 365 * DAY


def plot_trapping_distribution(
    masses_np: np.array,
    t_np: np.array,
) -> go.Figure:
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

    fig = go.Figure()
    for i in range(len(masses_np)):
        fig.add_trace(go.Scatter(
            x=t_years, y=masses_np[i],
            mode='lines',
            line=dict(width=0.5, color=color_map[i]),
            stackgroup='one',
            name=labels[i],
        ))

    yaxis_max = max(np.sum(masses_np, axis=0))

    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, b=0, t=0),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        yaxis=dict(
            range=[0, yaxis_max],
            title='Mass (MT)'
        ),
        xaxis=dict(
            title='Years since simulation start'
        )
    )

    return fig
