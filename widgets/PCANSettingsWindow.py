import tkinter as tk
from tkinter import *
from tkinter import ttk

class PCANSettingsWindow(Toplevel):
    _WIN_WIDTH = 210    # px
    _WIN_HEIGHT = 100   # px

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master

        self.grab_set()
        self.title("PCAN Initialize")
        self.geometry("{}x{}".format(self._WIN_WIDTH, self._WIN_HEIGHT))
        self.attributes('-topmost', 'true')

        # Initialize widgets
        self.port_label = Label(self, text="Port", justify=RIGHT)
        self.baud_label = Label(self, text="Baud", justify=RIGHT)
        self.time_label = Label(self, text="Time", justify=RIGHT)
        self.port_entry = Entry(self, textvariable=self.master._PORT, width=6)
        self.baud_entry = Entry(self, textvariable=self.master._BAUDRATE, width=6)
        self.time_entry = Entry(self, textvariable=self.master._TIMEOUT, width=6)
        self.set_button = Button(self, text="SET", command=self.close_window)
        
        # Place widgets
        self.grid_rowconfigure((0, 1, 2), weight=1, uniform='row')
        self.grid_rowconfigure(3, uniform='row')
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.port_label.grid(row=0, column=0, sticky="E")
        self.port_entry.grid(row=0, column=1, sticky="W")
        self.baud_label.grid(row=1, column=0, sticky="E")
        self.baud_entry.grid(row=1, column=1, sticky="W")
        self.time_label.grid(row=2, column=0, sticky="E")
        self.time_entry.grid(row=2, column=1, sticky="W")
        self.set_button.grid(row=3, column=0, columnspan=2, sticky="NSEW", padx=5, pady=5)

    def close_window(self):
        if self.master.update_pcan_settings():
            self.destroy()
    