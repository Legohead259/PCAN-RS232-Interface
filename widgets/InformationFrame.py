from tkinter import Frame, Label, StringVar
from tkinter.constants import FALSE, LEFT


class InformationFrame(Frame):
    def __init__(self, root, *args, **kwargs):
        Frame.__init__(self, root, *args, **kwargs)
        self.master = root

        # Initialize display items
        self.pcan_sn = StringVar()
        self.pcan_hw_version = StringVar()
        self.pcan_sw_version = StringVar()
        self.pcan_status = StringVar()
        self.cmd_feedback = StringVar()

        # Configure display items
        self.pcan_sn.trace_add('write', self.sn_observer)
        self.pcan_hw_version.trace_add('write', self.hw_version_observer)
        self.pcan_sw_version.trace_add('write', self.sw_version_observer)
        self.pcan_status.trace_add('write', self.status_observer)
        self.cmd_feedback.trace_add('write', self.cmd_feedback_observer)

        # Initialize widgets
        self.sn_label = Label(self, text="Serial Number: ", anchor='w')
        self.hw_version_label = Label(self, text="Hardware Version: ", anchor='w')
        self.sw_version_label = Label(self, text="Software Version: ", anchor='w')
        self.status_label = Label(self, text="Status: ", anchor='w')
        self.cmd_feedback_label = Label(self, text="No commands sent!", anchor='w')

        # Place widgets
        self.grid_rowconfigure(0, weight=1, uniform='row')
        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform='column')
        self.sn_label.grid(row=0, column=0, sticky='NSEW')
        self.hw_version_label.grid(row=0, column=1, sticky='NSEW')
        self.sw_version_label.grid(row=0, column=2, sticky='NSEW')
        self.status_label.grid(row=0, column=3, sticky='NSEW')
        self.cmd_feedback_label.grid(row=0, column=4, sticky='NSEW')

    # ===OBSERVER CALLBACKS===

    def sn_observer(self, *args):
        self.sn_label.config(text="Serial Number: " + self.pcan_sn.get())

    def hw_version_observer(self, *args):
        self.hw_version_label.config(text="Hardware Version: " + self.pcan_hw_version.get())

    def sw_version_observer(self, *args):
        self.sw_version_label.config(text="Software Version: " + self.pcan_sw_version.get())

    def status_observer(self, *args):
        self.status_label.config(text="Status: " + self.pcan_status.get())

    def cmd_feedback_observer(self, *args):
        self.cmd_feedback_label.config(text=self.cmd_feedback.get())
