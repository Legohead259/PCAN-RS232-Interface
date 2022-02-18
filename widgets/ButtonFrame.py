from tkinter import Button, Entry, Frame, Label, OptionMenu, StringVar, Toplevel, messagebox
from tkinter.constants import DISABLED, NORMAL, RADIOBUTTON, RAISED, SUNKEN, TOP
import string

class ButtonFrame(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.master = master

        # Initialize toggle variables
        self._autopoll = True       # True: Enabled, False: Disabled
        self._autostartup = False   # True: Enabled, False: Disabled
        self._filter_mode = False   # True: Single filter, False: Dual filter
        self._timestamp = False     # True: Enabled, False: Disabled

        # Initialize widgets
        self.stat_button =              Button(self, text="STAT",   width=6, command=self.stat_callback)
        self.info_button =              Button(self, text="INFO",   width=6, command=self.info_callback)
        self.acceptance_code_button =   Button(self, text="CODE",   width=6, command=self.acceptance_code_callback)
        self.acceptance_mask_button =   Button(self, text="MASK",   width=6, command=self.acceptance_mask_callback)
        self.autopoll_button =          Button(self, text="POLL",   width=6, command=self.autopoll_callback, relief=SUNKEN)
        self.autostartup_button =       Button(self, text="START",  width=6, command=self.autostartup_callback)
        self.can_baudrate_button =      Button(self, text="CBAUD",  width=6, command=self.can_baudrate_callback)
        self.uart_baudrate_button =     Button(self, text="SBAUD",  width=6, command=self.uart_baudrate_callback)
        self.filter_button =            Button(self, text="FILTER", width=6, command=self.filter_callback)
        self.timestamp_button =         Button(self, text="TIME",   width=6, command=self.timestamp_callback)
        self.eeprom_write_button =      Button(self, text="EEPROM", width=6, command=self.eeprom_write_callback)

        # Place widgets
        self.stat_button.place(x=30, y=30, width=60, height=30)
        self.info_button.place(x=120, y=30, width=60, height=30)
        self.acceptance_code_button.place(x=30, y=90, width=60, height=30)
        self.acceptance_mask_button.place(x=120, y=90, width=60, height=30)
        self.autopoll_button.place(x=30, y=150, width=60, height=30)
        self.autostartup_button.place(x=120, y=150, width=60, height=30)
        self.can_baudrate_button.place(x=30, y=210, width=60, height=30)
        self.uart_baudrate_button.place(x=120, y=210, width=60, height=30)
        self.filter_button.place(x=30, y=270, width=60, height=30)
        self.timestamp_button.place(x=120, y=270, width=60, height=30)
        self.eeprom_write_button.place(x=75, y=330, width=60, height=30)

    # ===CALLBACKS===

    def stat_callback(self):
        self.master.update_pcan_status()

    def info_callback(self):
        self.master.update_pcan_info()

    def acceptance_code_callback(self):
        self.acceptance_window = AcceptanceRegWindow(self.master, False)

    def acceptance_mask_callback(self):
        self.acceptance_window = AcceptanceRegWindow(self.master, True)

    def autopoll_callback(self):
        self._autopoll = not self._autopoll
        _res = self.master.update_auto_poll(self._autopoll)

        # TODO: Verify button image with actual hardware autopoll status?
        if _res != -1: # Auto poll command successfully sent
            if self._autopoll:
                self.autopoll_button.config(relief=SUNKEN)
            else: 
                self.autopoll_button.config(relief=RAISED)

    def autostartup_callback(self):
        if not self._autostartup:
            _result = messagebox.askquestion('Auto Startup','Do you want to enable auto startup (this will prevent CAN transmisions)') 
            if _result: # User would like to enable auto startup from it being disabled
                self._autostartup = True
                _res = self.master.update_auto_startup(self._autostartup) # Send enable auto startup command
                if _res != -1: # Auto startup command successfully sent
                    self.autostartup_button.config(relief=SUNKEN, bg="red") # Depress the button and make it red
        else:
            self._autostartup = False
            _res = self.master.update_auto_startup(self._autostartup) # Send disable auto startup command
            if _res != -1: # Auto startup command successfully sent
                self.autostartup_button.config(relief=RAISED, bg="SystemButtonFace") # Release the button and make it green

    def can_baudrate_callback(self):
        self.baudrate_window = OptionsPopup(self.master, 1)

    def uart_baudrate_callback(self):
        self.baudrate_window = OptionsPopup(self.master, 0)

    def filter_callback(self):
        if self.master.update_filter_mode(not self._filter_mode) != -1: # Filter command successfully sent
            self._filter_mode = not self._filter_mode
        self.filter_button.config(relief=SUNKEN) if self._filter_mode else self.filter_button.config(relief=RAISED)

    def timestamp_callback(self):
        if self.master.update_timestamp(not self._timestamp) != -1: # Filter command successfully sent
            self._timestamp = not self._timestamp
        self.timestamp_button.config(relief=SUNKEN) if self._timestamp else self.timestamp_button.config(relief=RAISED)

    def eeprom_write_callback(self):
        self.baudrate_window = OptionsPopup(self.master, 2)


class AcceptanceRegWindow(Toplevel):
    def __init__(self, master, type: bool, *args, **kwargs):
        """
        :param type determines if the window will change the acceptance mask (True) or code (False)
        """
        super().__init__(master, *args, **kwargs)
        self.type = type
        self.master = master
        self.grab_set()

        # Create acceptance mask window if type=1, else acceptance code
        self.title("Acceptance Mask") if type else self.title("Acceptance Code")
        self.geometry("210x100")

        # Initialize window-specific variables
        # Default acceptance mask value: 0xFFFFFFFF,
        #         acceptance code value: 0x00000000
        self.acceptance_var = StringVar(value="FFFFFFFF") if type else StringVar(value="00000000")

        # Initialize widgets
        _label_text = "Enter hex acceptance mask:" if type else "Enter hex acceptance code:"
        self.label = Label(self, text =_label_text)
        vcmd = (self.register(self.on_validate), '%S', '%P') # Setup validation function
        self.entry = Entry(self)
        self.entry.insert(0, self.acceptance_var.get())
        self.entry.configure(validate='key', validatecommand=vcmd)
        self.button = Button(self, text="Done", command=self.close_window)

        # Place widgets
        self.label.pack(pady=10)
        self.entry.pack()
        self.button.pack(pady=10)

    def on_validate(self, S, P):
        if S in string.hexdigits and len(P) < 9: # Only allow 0 or 1 and max of 8 letters
            if len(P) == 8: # Eight bits entered
                self.button.configure(state=NORMAL)
                self.acceptance_var.set(P)
            else:
                self.button.configure(state=DISABLED)
            return True
        return False

    def close_window(self):
        # TODO: Keep window open if register fails to set
        if self.type: self.master.update_acceptance_mask(self.acceptance_var.get()) 
        else: self.master.update_acceptance_code(self.acceptance_var.get())
        self.destroy()


class OptionsPopup(Toplevel):
    def __init__(self, master, type: int, *args, **kwargs):
        """
        :param type determines if the baudrate window
                0 = CAN Baudrate
                1 = UART Baudrate
                2 = EEPROM commands
        """
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.type = type
        self.grab_set()
        self.geometry("210x130")

        if type == 0:   self.title("UART Baudrate")
        elif type == 1: self.title("CAN Baudrate")
        elif type == 2: self.title("EEPROM Commands")

        # Create options
        if type == 0: # UART Baudrate
            self.options = ["0 - 230400 baud",
                       "1 - 115200 baud",
                       "2 - 57600 baud (default)",
                       "3 - 38400 baud",
                       "4 - 19200 baud",
                       "5 - 9600 baud",
                       "6 - 2400 baud"]
        elif type == 1: # CAN Baudrate
            self.options = ["10 kbps",
                       "20 kbps",
                       "50 kbps",
                       "100 kbps",
                       "125 kbps",
                       "250 kbps",
                       "500 kbps (default)",
                       "800 kbps",
                       "1 Mbps"]
        elif type == 2: # EEPROM options
            self.options = ["Save current settings",
                            "Reload factory defaults",
                            "Erase all settings"]

        # Initialize window-specific variables
        # Default UART Baudrate:    2 - 57600,
        #         CAN Baudrate:     6 - 500 kbps
        #         EEPROM:           0 - Save current settings
        self.choice = StringVar()
        # TODO: Set initial option to current baudrate settings
        if type == 0:   self.choice.set(value=self.options[2])  
        elif type == 1: self.choice.set(value=self.options[6])
        elif type == 2: self.choice.set(value=self.options[0])

        # Initialize widgets
        _label_text = ""
        if type == 0:   _label_text = "Select UART Baudrate" 
        elif type == 1: _label_text = "Select CAN Baudrate"
        elif type == 2: _label_text = "Select EEPROM command"
        self.label = Label(self, text =_label_text)
        self.drop_menu = OptionMenu(self, self.choice, *self.options)
        self.button = Button(self, text="Done", command=self.close_window)

        # Place widgets
        self.label.pack(pady=10)
        self.drop_menu.pack()
        self.button.pack(pady=10)

    def close_window(self):
        # TODO: Keep window open if baudrate fails to set
        _n = str(self.options.index(self.choice.get()))
        if self.type == 0:      self.master.update_uart_baudrate(_n) 
        elif self.type == 1:    self.master.update_can_baudrate(_n)
        elif self.type == 2:    self.master.update_eeprom(_n)
        self.destroy()