from tkinter import Tk, Canvas, Entry, Button
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from plotting.plot_formation import plot_formation
from simulation.explore_simulation import explore_simulation

FORMATIONS = [
    'brentgrp', 'brynefm', 'fensfjordfm', 'gassumfm',
    'johansenfm', 'krossfjordfm', 'pliocenesand',
    'sandnesfm', 'skadefm', 'sognefjordfm', 'statfjordfm',
    'ulafm', 'utsirafm', 'stofm', 'nordmelafm', 'tubaenfm',
    'bjarmelandfm', 'arefm', 'garnfm', 'ilefm', 'tiljefm'
]


class GUI:
    def __init__(self):
        self.window = Tk()
        self.window.title('CO2 storage simulator')
        self.formation = 13
        self.scatter = None
        self.well_x = 0
        self.well_y = 0

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
            bg="#ffffff",
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
            command=lambda: explore_simulation(
                [(self.well_x, self.well_y)],
                formation=FORMATIONS[self.formation],
                show_plot=True
            )
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

        figure, _ = plot_formation(
            FORMATIONS[self.formation],
            self,
            set_callbacks=True,
            callback_func=on_click,
            use_trapping=True
        )

        self.scatter = FigureCanvasTkAgg(figure, self.window)
        self.scatter.get_tk_widget().pack(side=tk.LEFT, fill=tk.Y)

        self.window.resizable(False, False)
        self.window.mainloop()


def on_click(
    event,
    gui: GUI,
    formation: str
) -> None:
    x_mouse, y_mouse = event.mouseevent.xdata, event.mouseevent.ydata
    gui.well_x = float(x_mouse)
    gui.well_y = float(y_mouse)

    figure, _ = plot_formation(
        formation,
        gui,
        set_callbacks=True,
        callback_func=on_click,
        show_well=True,
        use_trapping=True
    )

    gui.scatter.get_tk_widget().destroy()
    gui.scatter = FigureCanvasTkAgg(figure, gui.window)
    gui.scatter.get_tk_widget().pack(side=tk.LEFT, fill=tk.Y)


if __name__ == '__main__':
    gui = GUI()
    gui.run()
