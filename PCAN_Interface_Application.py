from widgets.MessageFrame import MessageFrame
from widgets.ConsoleFrame import ConsoleFrame
from widgets.PCANSettingsWindow import PCANSettingsWindow
from lib.PCAN_RS_232 import PCAN_RS_232
from tkinter import *
from widgets.InformationFrame import InformationFrame
from widgets.ButtonFrame import ButtonFrame
from serial import SerialException

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("PCAN-RS-232 Interface")
        self.geometry('960x420')
        self.resizable(FALSE, FALSE)
        
        # Create main containers
        self.button_frame = ButtonFrame(self, bg="#004080", pady=3)
        self.center_frame = ConsoleFrame(self, padx=3, pady=3)
        self.can_msg_frame = MessageFrame(self, bg="#004080", pady=3)
        self.btm_frame = InformationFrame(self, bg="#004080", pady=3)

        # Layout containers
        self.button_frame.place(x=0, y=0, width=210, height=390)
        self.center_frame.place(x=210, y=0, width=540, height=390)
        self.can_msg_frame.place(x=750, y=0, width=210, height=390)
        self.btm_frame.place(x=0, y=390, width=960, height=30)

        # Initialize application variables
        self._PORT = StringVar(value="COM1")        # Default: COM1
        self._BAUDRATE = StringVar(value="57600")   # Default: 57600
        self._TIMEOUT = StringVar(value="1")        # Default: 1 (s)
        try:
            self.pcan = PCAN_RS_232(self._PORT.get(), int(self._BAUDRATE.get()), int(self._TIMEOUT.get()))
            self.center_frame.begin(self.pcan)
        except SerialException: # Default device not found
            self.pcan_window = PCANSettingsWindow(self) # Open a window to configure PCAN settings

    # ===PCAN INTERACTION FUNCTIONS===

    def update_pcan_settings(self):
        try:
            self.pcan = PCAN_RS_232(self._PORT.get(), int(self._BAUDRATE.get()), int(self._TIMEOUT.get()))
            self.center_frame.begin(self.pcan)
            return True
        except SerialException:
            return False

    # ===WIDGET INTERFACE FUNCTIONS===
    
    def update_pcan_status(self):
        _stat = self.pcan.get_status_flags()
        if _stat != -1:
            self.btm_frame.pcan_status.set(_stat)
            self.btm_frame.cmd_feedback.set("Received PCAN status")
        else:
            self.btm_frame.cmd_feedback.set("FAILED to get PCAN status")

    def update_pcan_open(self, open):
        _res = self.pcan.open_channel() if open else self.pcan.close_channel()
        if _res != -1: # Channel successfully opened/closed
            _text = "Opened CAN Channel" if open else "Closed CAN channel"
            self.btm_frame.cmd_feedback.set(_text)
            return True
        else:
            _text = "FAILED to open CAN channel" if open else "FAILED to close CAN channel"
            self.btm_frame.cmd_feedback.set(_text)
            return False
    
    def update_pcan_info(self):
        _sn = self.pcan.get_serial_number()
        _info = self.pcan.get_version_info()
        print(_info) # DEBUG
        if _info != -1:
            self.btm_frame.pcan_sn.set(_sn)
            self.btm_frame.pcan_hw_version.set(_info[0])
            self.btm_frame.pcan_sw_version.set(_info[1])
            self.btm_frame.cmd_feedback.set("Received PCAN info")
        else:
            self.btm_frame.cmd_feedback.set("FAILED to get PCAN info")

    def update_acceptance_mask(self, mask):
        _res = self.pcan.set_acceptance_mask_register(mask)
        if _res != -1: # Acceptance mask register successfuly set
            self.btm_frame.cmd_feedback.set("Set mask to " + mask)
        else:
            self.btm_frame.cmd_feedback.set("FAILED to set acceptance mask")
        return _res

    def update_acceptance_code(self, code):
        _res = self.pcan.set_acceptance_code_register(code)
        if _res != -1: # Acceptance code register successfuly set
            self.btm_frame.cmd_feedback.set("Set code to "+ code)
        else:
            self.btm_frame.cmd_feedback.set("FAILED to set acceptance code")
        return _res

    def update_auto_poll(self, en: bool):
        _res = self.pcan.set_auto_poll(en)
        if _res != -1: # Auto poll successfully set
            _text = "ENABLED auto poll feature" if en else "DISABLED auto poll feature"
            self.btm_frame.cmd_feedback.set(_text)
        else:
            self.btm_frame.cmd_feedback.set("FAILED to set auto poll")
        return _res

    def update_auto_startup(self, en: bool):
        _res = self.pcan.set_auto_startup(en)
        if _res != -1: # Auto startup successfully set
            _text = "ENABLED auto startup feature" if en else "DISABLED auto startup feature"
            self.btm_frame.cmd_feedback.set(_text)
        else:
            self.btm_frame.cmd_feedback.set("FAILED to set auto startup")
        return _res

    def update_can_baudrate(self, n: str):
        _res = self.pcan.set_can_bitrate(n)
        if _res != -1: # CAN baudrate successfully set
            self.btm_frame.cmd_feedback.set("Set CAN baudrate") # TODO: Include baudrate
        else:
            self.btm_frame.cmd_feedback.set("FAILED to set CAN baudrate")
        return _res

    def update_uart_baudrate(self, n: str):
        _res = self.pcan.set_uart_bitrate(n)
        # TODO: Edit application baudrate to reflect new set baudrate!!!!!!!!!!
        if _res != -1: # UART baudrate successfully set
            self.btm_frame.cmd_feedback.set("Set UART baudrate") # TODO: Include baudrate
        else:
            self.btm_frame.cmd_feedback.set("FAILED to set UART baudrate")
        return _res
    
    def update_filter_mode(self, n: bool):
        _res = self.pcan.set_filter_mode(n)
        if _res != -1: # Filter mode successfully set
            _text = "Set mode to Single Filter" if n else "Set mode to Dual Filter"
            self.btm_frame.cmd_feedback.set(_text)
        else:
            self.btm_frame.cmd_feedback.set("FAILED to set filter mode")
        return _res

    def update_timestamp(self, n: bool):
        _res = self.pcan.enable_timestamps(n)
        if _res != -1: # Filter mode successfully set
            _text = "Enabled timestamp feature" if n else "Disabled timestamp feature"
            self.btm_frame.cmd_feedback.set(_text)
        else:
            self.btm_frame.cmd_feedback.set("FAILED to timestamp feature")
        return _res

    def update_eeprom(self, n: str):
        if self.pcan.write_to_eeprom(n) != -1:
            if n == '0':    self.btm_frame.cmd_feedback.set("Saved settings to EEPROM")
            elif n == '1':  self.btm_frame.cmd_feedback.set("Reloaded factory settings")
            elif n == '2':  self.btm_frame.cmd_feedback.set("Deleted all settings")
        else:
            self.btm_frame.cmd_feedback.set("FAILED to command EEPROM")

    def transmit_message(self, msg):
        if self.pcan.send_message(msg) != -1: # Message successfully sent
            self.btm_frame.cmd_feedback.set("Sent message")
        else:
            self.btm_frame.cmd_feedback.set("FAILED to send message")

_app = App()

try:
    if __name__ == '__main__':
        _app.mainloop() # Begin interface application
finally: # On app close
    try:
        _app.update_pcan_open(False) # Close CAN connection
        _app.update_eeprom('1') # Reset to factory-default settings
    except:
        pass