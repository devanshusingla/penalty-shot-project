from communication import PSClient
import tkinter as tk
from tkinter import ttk
import time
from _thread import start_new_thread

# GUI developed through code inspired from
# https://www.pythontutorial.net/tkinter/tkinter-slider/


class MS:
    def __init__(self, id, time_interval=0.5):
        self.id = id
        self.time_interval = time_interval

    def _start(self, current_value):
        agent = PSClient(id=self.id)
        res = agent.connect()
        if not res:
            print("server not responding")
            return

        state, done = res
        print(state, done)

        while not done:
            time.sleep(self.time_interval)
            res = agent.step(current_value.get())
            if not res:
                print("server not responding")
                break

            state, reward, done, info = res

        agent.close()

    def run(self):
        window = tk.Tk()
        window.title("Mouse Slider")
        window.resizable(False, False)

        current_value = tk.DoubleVar()

        start_button = ttk.Button(
            window,
            text="Start",
            command=lambda: start_new_thread(self._start, (current_value,)),
        )
        start_button.grid(column=1, columnspan=2, row=4)

        def get_current_value():
            return "{: .2f}".format(current_value.get())

        def slider_changed(event):
            value_label.configure(text=get_current_value())

        slider = ttk.Scale(
            window,
            from_=1,
            to=-1,
            length=300,
            orient=tk.VERTICAL,
            command=slider_changed,
            variable=current_value,
        )

        slider.grid(column=3, row=0, rowspan=6, sticky="w")

        # current value label
        current_value_label = ttk.Label(window, text="Current Value:")

        current_value_label.grid(
            row=1, column=1, columnspan=2, sticky="n", ipadx=0, ipady=0
        )

        # value label
        value_label = ttk.Label(window, text=get_current_value())
        value_label.grid(row=2, column=1, columnspan=2, sticky="n")

        window.mainloop()
