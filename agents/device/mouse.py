from communication import PSClient
import numpy as np
import tkinter as tk
from tkinter import ttk
import time

window = tk.Tk()
window.title("Mouse Slider")
window.resizable(False, False)

start_button = ttk.Button(window, text='Start', command=lambda : time.sleep(2))
start_button.grid(
    column=1,
    columnspan=2,
    row=4
)

current_value = tk.DoubleVar()

def get_current_value():
    return '{: .2f}'.format(current_value.get())

def slider_changed(event):
    value_label.configure(text=get_current_value())

slider = ttk.Scale(window, from_=-1, to=1, length=300, orient=tk.VERTICAL, command=slider_changed, variable=current_value)

slider.grid(
    column=3,
    row=0,
    rowspan=6,
    sticky='w'
)


# current value label
current_value_label = ttk.Label(
    window,
    text='Current Value:'
)

current_value_label.grid(
    row=1,
    column=1,
    columnspan=2,
    sticky='n',
    ipadx=0,
    ipady=0
)

# value label
value_label = ttk.Label(
    window,
    text=get_current_value()
)
value_label.grid(
    row=2,
    column = 1,
    columnspan=2,
    sticky='n'
)

window.mainloop()