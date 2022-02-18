from tkinter import Button, Entry, Frame, Label, StringVar, IntVar
from tkinter.constants import END, RAISED, SUNKEN
from string import hexdigits, digits

from serial.serialutil import CR

class MessageFrame(Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Initialize frame-specific variables
        self.msg_id = StringVar(value="0")
        self._id = IntVar()
        self.msg_dlc = StringVar(value="0")
        self._dlc = IntVar()
        self.msg_data = StringVar()
        self._valid_id = False
        self._ext = False
        self._rtr = False
        self._open = False

        # Initialize widgets
        self.title_label = Label(self, text="CAN Message", bg="#004080", fg="white")
        self.id_label = Label(self, text="ID", anchor='e', bg="#004080", fg="white")
        self.dlc_label = Label(self, text="DLC", anchor='e', bg="#004080", fg="white")
        self.byte_labels = [Label(self, text="Byte{}".format(i), anchor='e', bg="#004080", fg="white") for i in range(0, 8)] # Create 8 byte labels in a list

        id_vcmd = (self.register(self.id_validate), '%S', '%P', '%i') # Setup validation function
        self.id_entry = Entry(self)
        self.id_entry.insert(0, "0")
        self.id_entry.configure(validate="key", validatecommand=id_vcmd)

        dlc_vcmd = (self.register(self.dlc_validate), '%S', '%P') # Setup validation function
        self.dlc_entry = Entry(self)
        self.dlc_entry.insert(0, "0")
        self.dlc_entry.configure(validate="key", validatecommand=dlc_vcmd)

        byte_vcmd = (self.register(self.byte_validate), '%S', '%P') # Setup validation function
        self.byte_entries = [Entry(self) for i in range(0, 8)] # Create 8 byte entries in a list
        for e in self.byte_entries:
            e.insert(0, "00") # Insert default text of 00
            e.configure(validate='key', validatecommand=byte_vcmd) # Attach validation commands

        self.ext_button =       Button(self, text="EXT",        command=self.ext_callback)
        self.rtr_button =       Button(self, text="RTR",        command=self.rtr_callback)
        self.transmit_button =  Button(self, text="TRANSMIT",   command=self.transmit_callback)
        self.open_button =      Button(self, text="OPEN",       command=self.open_callback)
        self.close_button =     Button(self, text="CLOSE",      command=self.close_callback)

        # Place widgets
        self.title_label.place(x=30, y=0, width=150, height=20)
        self.id_label.place(x=45, y=30, width=30, height=20)
        self.id_entry.place(x=90, y=30, width=90, height=20)
        self.dlc_label.place(x=45, y=50, width=30, height=20)
        self.dlc_entry.place(x=90, y=50, width=90, height=20)
        i = 0
        for l in self.byte_labels: # Place byte labels
            l.place(x=30, y=80+i*20, width=60, height=20)
            i += 1
        i = 0
        for e in self.byte_entries: # Place byte entries
            e.place(x=105, y=80+i*20, width=30, height=20)
            i += 1
        self.ext_button.place(x=30, y=280, width=60, height=30)
        self.rtr_button.place(x=120, y=280, width=60, height=30)
        self.transmit_button.place(x=60, y=315, width=90, height=30)
        self.open_button.place(x=30, y=350, width=60, height=30)
        self.close_button.place(x=120, y=350, width=60, height=30)

    # ===OBSERVERS===

    # ===VALIDATORS===

    def id_validate(self, S, P, i):
        # print(P) # Debug
        if self._ext: # If extended identifier enabled
            if S in hexdigits and len(P) < 9: # If hexadecimal characters and within length
                try: # Handles if the entry box is going blank (P='')
                    if int(P, 16) <= 0x1FFFFFFF:
                        return True
                    else:
                        return False
                except ValueError:
                    return True
            else:
                return False
        else: # If standard identifier enabled
            if S in hexdigits and len(P) < 4:
                try: # Handles if the entry box is going blank (P='')
                    if int(P, 16) <= 0x7FF:
                        return True
                    else:
                        return False
                except ValueError:
                    return True
            else:
                return False

    def dlc_validate(self, S, P):
        # print(P) # debug
        if S in digits[0:9] and len(P) < 2: # Check if DLC is single digit
            return True
        return False

    def byte_validate(self, S, P):
        if S in hexdigits and len(P) < 3: # Only allow 2 hexadecimal characters
            return True
        return False

    # ===CALLBACKS===

    def ext_callback(self):
        self._ext = not self._ext
        if self._ext:
            self.ext_button.config(relief=SUNKEN, bg='lime') # Sink and color green
        else:
            self.ext_button.config(relief=RAISED, bg='SystemButtonFace') # Raise and return to normal color

    def rtr_callback(self):
        self._rtr = not self._rtr
        if self._rtr:
            self.rtr_button.config(relief=SUNKEN, bg='lime') # Sink and color green
        else:
            self.rtr_button.config(relief=RAISED, bg='SystemButtonFace') # Raise and return to normal color
        _state = "disabled" if self._rtr else "normal"
        for e in self.byte_entries:
            e.config(state=_state)

    def transmit_callback(self):
        # Generate message type
        if self._rtr:
            _type = 'R' if self._ext else 'r'
        else:
            _type = 'T' if self._ext else 't'
        
        # Get message identifier
        _id = self.id_entry.get().zfill(8) if self._ext else self.id_entry.get().zfill(3)

        # Get message length
        _dlc = self.dlc_entry.get()

        # Get message
        _data = ""
        if not self._rtr:
            for e in self.byte_entries[0:int(_dlc)]: # Get only the required data bytes as determined by DLC
                _data += e.get()

        print(_type + _id + _dlc + _data + '\r') # DEBUG
        self.master.transmit_message((_type + _id + _dlc + _data + '\r').encode("utf-8"))

    def open_callback(self):
        if self.master.update_pcan_open(True):
            self._open = True
            self.open_button.configure(relief=SUNKEN, bg="lime")

    def close_callback(self):
        if self.master.update_pcan_open(False):
            self._open = False
            self.open_button.configure(relief=RAISED, bg="SystemButtonFace")