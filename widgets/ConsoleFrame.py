import threading
from tkinter import Button, Frame, StringVar, Text
from tkinter.constants import COMMAND, END
from datetime import datetime
import serial

class ConsoleFrame(Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.master = master
        self.alive = True
        self.connected = False

        # Initialize frame-specific variables
        self.serial_output = StringVar() # Holds the latest output from the serial port
        self.serial_output.trace_add('write', self.serial_output_observer)

        # Initialize widgets
        self.console = Text(self, bg="black", fg="white")

        # Place widgets
        self.console.pack()

    def begin(self, s):
        self._ser = s
        self._start_reader()

    # ===OBSERVERS===

    def serial_output_observer(self, *args):
        _now = datetime.now()
        print(_now) # Debug
        _frame = self.master.pcan.parse_frame_message(self.serial_output.get())
        self.console.insert(END, "{} | {} | {} | {} | {}".format(_now, _frame[0], _frame[1], _frame[2], _frame[3]))
        self.console.see(END)

    # ===TERMINAL FUNCTIONS===

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()
        
    def reader(self):
        """loop and copy serial->console"""
        try:
            while self.alive and not self.connected:
                self.connected = True
                data = self._ser.read(self._ser.in_waiting or 1) # read all that is there or wait for one byte
                if data: # If data is present, write to console
                    self.serial_output.set(data)
        except serial.SerialException: # If borked, kill thread
            self.alive = False
            raise       # XXX handle instead of re-raise?
