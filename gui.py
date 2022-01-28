from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from modules.co2lab.examples.explore_simulation import explore_simulation

import matplotlib.pyplot as plt

# from modules.co2lab.reinforcement_learning.basic_policy import run_basic_policy
# from modules.co2lab.reinforcement_learning.nn_policy import run_nn_policy

from matplotlib import cm
from matplotlib.collections import PolyCollection

from utils import get_vertices, get_colors

COLOUR_INTENSITY = 0.85

FORMATIONS = [
    'brentgrp', 'brynefm', 'fensfjordfm', 'gassumfm',
    'johansenfm', 'krossfjordfm', 'pliocenesand',
    'sandnesfm', 'skadefm', 'sognefjordfm', 'statfjordfm',
    'ulafm', 'utsirafm', 'stofm', 'nordmelafm', 'tubaenfm',
    'bjarmelandfm', 'arefm', 'garnfm', 'ilefm', 'tiljefm']

CSV_FILE = 'centroids'

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


class GUI:
    window = Tk()
    window.title('CO2 storage simulator')
    scatter = None
    formation = 8

    def run(self):
        self.window.geometry("755x519")
        self.window.configure(bg="#3A7FF6")

        injection_rate = tk.StringVar()
        injection_rate.set('10')
        injection_period = tk.StringVar()
        injection_period.set('50')
        injection_time_steps = tk.StringVar()
        injection_time_steps.set('5')
        migration_period = tk.StringVar()
        migration_period.set('100')
        migration_time_steps = tk.StringVar()
        migration_time_steps.set('5')

        canvas = Canvas(
            self.window,
            bg="#3A7FF6",
            height=719,
            width=962,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.place(x=0, y=0)
        canvas.create_rectangle(
            431.0,
            0.0,
            862.0,
            519.0,
            fill="#FCFCFC",
            outline="")

        button_1 = Button(
            text='Run simulation',
            borderwidth=0,
            highlightthickness=1,
            highlightbackground='#3A7FF6',
            command=lambda: print('HERE!!!')
        )
        button_1.place(
            x=471.0,
            y=320.0,
            width=196.0,
            height=42.0
        )

        button_2 = Button(
            text='Run basic well location',
            borderwidth=0,
            highlightthickness=1,
            highlightbackground='#3A7FF6',
            command=lambda: print('HERE!!!')
        )
        button_2.place(
            x=471.0,
            y=434.0,
            width=196.0,
            height=42.0
        )

        button_3 = Button(
            text='Run smart well location',
            borderwidth=0,
            highlightthickness=1,
            highlightbackground='#3A7FF6',
            command=lambda: print('HERE!!!')
        )
        button_3.place(
            x=471.0,
            y=377.0,
            width=196.0,
            height=42.0
        )

        canvas.create_text(
            471.0,
            15.0,
            anchor="nw",
            text="Set simulation parameters",
            fill="#505485",
            font=("Roboto Bold", 24 * -1)
        )

        entry_1 = Entry(
            textvariable=injection_rate,
            highlightthickness=1,
            borderwidth=0,
            highlightbackground='#3A7FF6'
        )
        entry_1.place(
            x=657.0,
            y=62.0,
            width=35.0,
            height=29.0
        )

        entry_2 = Entry(
            textvariable=injection_period,
            highlightthickness=1,
            borderwidth=0,
            highlightbackground='#3A7FF6'
        )
        entry_2.place(
            x=657.0,
            y=112.0,
            width=35.0,
            height=29.0
        )

        entry_3 = Entry(
            textvariable=injection_time_steps,
            highlightthickness=1,
            borderwidth=0,
            highlightbackground='#3A7FF6'
        )
        entry_3.place(
            x=657.0,
            y=162.0,
            width=35.0,
            height=29.0
        )

        entry_4 = Entry(
            textvariable=migration_period,
            highlightthickness=1,
            borderwidth=0,
            highlightbackground='#3A7FF6'
        )
        entry_4.place(
            x=657.0,
            y=214.0,
            width=35.0,
            height=29.0
        )

        entry_5 = Entry(
            textvariable=migration_time_steps,
            highlightthickness=1,
            borderwidth=0,
            highlightbackground='#3A7FF6'
        )
        entry_5.place(
            x=657.0,
            y=264.0,
            width=35.0,
            height=29.0
        )

        canvas.create_text(
            471.0,
            68.0,
            anchor="nw",
            text="Injection rate",
            fill="#000000",
            font=("Montserrat Regular", 15 * -1)
        )

        canvas.create_text(
            471.0,
            118.0,
            anchor="nw",
            text="Injection period",
            fill="#000000",
            font=("Montserrat Regular", 15 * -1)
        )

        canvas.create_text(
            471.0,
            168.0,
            anchor="nw",
            text="Injection time steps",
            fill="#000000",
            font=("Montserrat Regular", 15 * -1)
        )

        canvas.create_text(
            471.0,
            220.0,
            anchor="nw",
            text="Migration period",
            fill="#000000",
            font=("Montserrat Regular", 15 * -1)
        )

        canvas.create_text(
            471.0,
            271.0,
            anchor="nw",
            text="Migration time steps",
            fill="#000000",
            font=("Montserrat Regular", 15 * -1)
        )

        figure = plot_formation(
            FORMATIONS[self.formation],
            use_trapping=True
        )

        GUI.scatter = FigureCanvasTkAgg(figure, GUI.window)
        GUI.scatter.get_tk_widget().pack(side=tk.LEFT, fill=tk.Y)

        self.window.resizable(False, False)
        self.window.mainloop()


def plot_formation(
    formation: str,
    well_x=0,
    well_y=0,
    show_well=False,
    use_trapping=False
) -> plt.Figure:
    vertices_formation = get_vertices(formation, 'faces', 'vertices')
    colors_formation = get_colors(formation)

    fig = plt.Figure(dpi=93)
    ax = fig.add_subplot()

    face_colors = [
        cm.viridis(x) for x in
        colors_formation / COLOUR_INTENSITY / colors_formation.max()
    ]

    collection = PolyCollection(
        vertices_formation,
        facecolors=face_colors,
        edgecolors='k',
        linewidths=0.05,
        alpha=0.9,
        picker=10
    )

    ax.add_collection(collection)

    if use_trapping:
        vertices_trapping = get_vertices(formation, 'faces_trapping', 'vertices_trapping')
        trapping_collection = PolyCollection(
            vertices_trapping,
            edgecolors='r',
            linewidths=0.5,
        )
        ax.add_collection(trapping_collection)

    ax.autoscale_view()
    if show_well:
        ax.scatter(well_x, well_y, c='k', marker='x')
        ax.annotate('Well', (well_x, well_y), textcoords="offset points", xytext=(0, 3))

    fig.canvas.callbacks.connect('pick_event', lambda event: _on_click(event, formation))

    return fig


def _on_click(event, formation):
    x_mouse, y_mouse = event.mouseevent.xdata, event.mouseevent.ydata
    GUI.well_x = x_mouse
    GUI.well_y = y_mouse

    figure = plot_formation(
        formation,
        x_mouse,
        y_mouse,
        show_well=True,
        use_trapping=True
    )

    GUI.scatter.get_tk_widget().destroy()
    GUI.scatter = FigureCanvasTkAgg(figure, GUI.window)
    GUI.scatter.get_tk_widget().pack(side=tk.LEFT, fill=tk.Y)


gui = GUI()
gui.run()
