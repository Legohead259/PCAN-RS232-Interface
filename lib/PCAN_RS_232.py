import serial
from serial.serialutil import CR

class PCAN_RS_232(serial.Serial):
    # Constants for PCAN interface
    CLOSE_CAN_CHANNEL           = b'C' + CR
    GET_SERIAL_NUMBER           = b'N' + CR
    GET_STATUS_FLAGS            = b'F' + CR
    GET_VERSION_INFO            = b'V' + CR
    LISTEN_CAN_CHANNEL          = b'L' + CR
    OPEN_CAN_CHANNEL            = b'O' + CR
    WRITE_EEPROM_DATA           = b'e'
    SET_ACCPETANCE_CODE_REG     = b'M'      
    SET_ACCEPTANCE_MASK_REG     = b'm'
    SET_AUTO_POLL               = b'X'
    SET_AUTO_STARTUP            = b'Q'
    SET_BTR0_BTR1_RATE          = b's'
    SET_CAN_BAUDRATE            = b'S'
    SET_FILTER_MODE             = b'W'
    SET_TIMESTAMP               = b'Z'
    SET_UART_BAUDRATE           = b'U'
    TRANSMIT_EXTENDED_CAN_FRAME = b'T'
    TRANSMIT_EXTENDED_RTR_FRAME = b'R'
    TRANSMIT_STANDARD_CAN_FRAME = b't'
    TRANSMIT_STANDARD_RTR_FRAME = b'r'

    # Flags
    _can_open = False

    def __init__(self, port, baudrate, timeout=1, *args, **kwargs):
        super().__init__(port=port, baudrate=baudrate, timeout=timeout, *args, **kwargs)
        self.reset_output_buffer() # Clear input/output buffers on initialization

    # =====GENERAL FUNCTIONS=====

    def open_channel(self):
        """
        Open the CAN channel in normal mode (sending & receiving).
        
        :pre This command is accepted only if the CAN channel is closed and 
        has already been initialized with either the S or the s command.
        
        :note Open the channel, green LED starts blinking slowly 1Hz.
            
        :return	-1 when ERROR occurs (typically the CAN channel is already open)
        :return	1 when CAN channel successfully opened
        """
        _res = self.send_message(self.OPEN_CAN_CHANNEL)
        if _res == 1: # CAN Channel successfully opened
            self._can_open = True
        return _res

    def open_channel_listen(self):
        """
        Open the CAN channel in listening mode (receiving only).

        :pre This command is accepted only if the CAN channel is closed and
        has already been initialized with either the "S" or "s" command.

        :note Open the channel, green LED starts blinking slowly 1Hz.

        :return -1 when ERROR occurs (typically the CAN channel is already in listen mode)
        :return 1 when the CAN channel is successfully opened in listening mode
        """
        _res = self.send_message(self.LISTEN_CAN_CHANNEL)
        if _res == 1: # CAN Channel successfully opened
            self._can_open = True
        return _res

    def close_channel(self):
        """
        Close the CAN channel

        :pre This command is accepted only if the CAN channel is opened

        :note Close the channel, green LED will become solid.

        :return -1 when ERROR occurs (typically the CAN channel is already closed)
        : return 1 when the CAN channel is successfully closed
        """
        _res = self.send_message(self.CLOSE_CAN_CHANNEL)
        if _res == 1: # CAN Channel successfully closed
            self._can_open = False
        return _res

    def enable_timestamps(self, en: bool):
        """
        Sets Time Stamp ON/OFF for received frames only.
        
        :pre This command is accepted only if the CAN channel is closed. 
        
        The timestamp feature is OFF by default. When enabled, four additional bytes will be added to the beginning
        of a CAN data frame like so:
        b'tXXXXiiildd...' where the four X's are the timestamp's hex value in milliseconds.
        
        :param n=False Turn OFF the timestamp feature 
        :param n=True Turn ON the timestamp feature
        
        :note The value is saved in EEPROM and is set each time the PCAN-RS-232 is powered up.
        :note The timestamp will roll over every minute
        
        :return	-1 when ERROR occurs (typically CAN channel is open)
        :return	1 when timestamp command successfully enacted
        """
        en = format(en, '01b').encode('utf-8') # Encode the en argument so the PCAN module can understand it
        return self._send_message_close_only(self.SET_TIMESTAMP + en + b'\r')

    def write_to_eeprom(self, n):
        """
        Writes configuration settings to EEPROM. 
        Don't write too often, intended for emergency cases and debugging !! 
        
        Use this function when you have set up CAN speed and filters
        and you want the PCAN-RS-232 to boot up with these settings
        automatically on every power on. Perfect for logging etc.
        or when no master is available to set up the PCAN-RS-232.
        
        :param n=0 Save current settings
        :param n=1 Reset to factory defaults
        :param n=2 Delete all settings

        :return	-1 when ERROR occurs (typically will never happen)
        :return	-1 when EEPROM command is successfully executed
        """
        # Input validation
        if isinstance(n, str) and int(n) in range(0,3): n = n.encode('utf-8')   # Check if n is a string and in correct range (0-2) and encode (b'X')
        elif isinstance(n, int) and n in range(0,3): n = str(n).encode('utf-8') # Check if n is an int and in correct rance (0-2) and encode (b'X')
        else: return -1                                                         # Return an error otherwise

        return self._send_message_close_only(self.WRITE_EEPROM_DATA + n + b'\r')

    # =====GETTERS/SETTERS=====

    def get_version_info(self):
        """
        Get version number of both PCAN-RS-232 hardware and software

        :return	-1 when ERROR occurs (typically will never happen)
        :return tuple with hardware and software versions hex strings, respectively
        """
        _rec = self.send_message(self.GET_VERSION_INFO)
        if _rec != -1: # Message successfully sent and received appropriate reply
            _rec = _rec.decode('utf-8') # Convert to string
            return (_rec[1:3], _rec[3:5]) # Return the hardware/software version hex representations as a tuple
        else:
            return _rec
    
    def get_serial_number(self):
        """
        Get PCAN module's serial number

        :return -1 when ERROR occurs (typically will never happen)
        :return the device's serial number as a number string
        """
        _rec = self.send_message(self.GET_SERIAL_NUMBER)
        if _rec != -1: # Message successfully sent and received appropriate reply
            _rec = _rec.decode('utf-8') # Convert to string
            return _rec[1:5] # Return serial number
        else:
            return _rec

    def get_status_flags(self):
        """
        Read Status Flags.
        
        :pre This command is accepted only if the CAN channel is open. 
        
        :return	-1 when ERROR occurs (typically when the CAN channel is closed)
        :return	A hex value representing the 8 status flags
                Bit 0 : CAN receive FIFO queue full
                Bit 1 : CAN transmit FIFO queue full
                Bit 2 : Error warning (EI), see SJA1000 datasheet
                Bit 3 : Data Overrun (DOI), see SJA1000 datasheet
                Bit 4 : Not used.
                Bit 5 : Error Passive (EPI), see SJA1000 datasheet
                Bit 6 : Arbitration Lost (ALI), see SJA1000 datasheet
                Bit 7 : Bus Error (BEI), see SJA1000 datasheet
        """
        _rec = self._send_message_open_only(self.GET_STATUS_FLAGS)
        if _rec != -1:
            _rec = _rec.decode('utf-8') # Convert to string
            return _rec[1:3] # Return the hex string for the status flags
        else:
            return _rec

    def set_acceptance_code_register(self, reg):
        """
        Sets Acceptance Code Register (ACn Register of SJA1000).

        :pre This command is accepted only if CAN channel is initialized but closed.

        :param reg Acceptance Code in hex with LSB first, AC0, AC1, AC2 & AC3.
        For more info, see NXP SJA1000 datasheet.

        :note The setting is is saved in EEPROM and remembered on next startup (only if autostart > 0).
        :note Set Acceptance Code to 0x00000000.
        This is default when power on with Autostart=0, i.e. all frames will come through
        .
        :return	-1 when ERROR occurs (typically when the CAN channel is open)
        :return	1 when the code register is successfully implemented
        """
        # Input validation
        if isinstance(reg, str): reg = int(reg, 16) if len(reg) <= 8 else int(reg[0:8], 16) # Check if reg is a string and convert to int. If longer than 8 char, cut off excess
        if reg in range(0, 0xFFFFFFFF+1): reg = format(reg, '08x').encode('utf-8')            # Check if reg is in the correct range (0-FFFFFFFF) then encode it (b'XXXXXXXX')
        else: return -1                                                                     # Return an error otherwise
            
        return self.send_message(self.SET_ACCPETANCE_CODE_REG + reg + b'\r')

    def set_acceptance_mask_register(self, mask):
        """
        Sets Acceptance Mask Register (AMn Register of SJA1000).

        :pre This command is accepted only if CAN channel is initialized but closed. 
        
        The Acceptance Code Register and the Acceptance Mask Register work together and they can
        filter out 2 groups of messages. 
        For more detailed info, see NXP SJA1000 datasheet. 
        In 11bit IDs it is possible to filter out a single ID this way, but in 29bit IDs it is only
        possible to filter out a group of IDs. 
        The example below will set a filter (dual mode) to only receive all 11bit IDs from 0x300 to 0x3FF.
        M00006000[CR] -> AC0=0x00, AC1=0x00, AC2=0x60 & AC3=0x00
        m00001FF0[CR] -> AM0=0x00, AM1=0x00, AM2=0x1F & AM3=0xF0
        The first command tells the filter 2 to match 2 bits and if they are not set 
        (in this case it corresponds to 0x3nn, the 3). 
        The second command tells the nn to be don't care, so it could be from 0 to FF,
        though not so easy to read, since they are not placed nice in a row in memory. 
        Filter 1 is turned off (uses AM0, AM1 & half lower AM3). 
        The last byte in the mask could also be 0xE0 instead of 0xF0,
        then we filter out the RTR bit as well and you wont accept RTR frames.
        
        :param xxxxxxxx Acceptance Mask in hex with LSB first, AM0, AM1, AM2 & AM3.
        For more detailed info, see NXP SJA1000 datasheet.
        
        :note The setting is is saved in EEPROM and remembered on next startup (only if autostart > 0).
        :note Set Acceptance Mask to 0xFFFFFFFF.
        This is default when power on with Autostart=0, i.e. all frames will come through.
        
        :return	-1 when ERROR occurs (typically when the CAN channel is open)
        :return	1 when the mask register is successfully implemented
        """
        # Input validation
        if isinstance(mask, str): mask = int(mask, 16) if len(mask) <= 8 else int(mask[0:8], 16)    # Check if mask is a string and convert to int. If longer than 8 char, cut off excess
        if mask in range(0, 0xFFFFFFFF+1): mask = format(mask, '08x').encode('utf-8')                 # Check if mask is in the correct range (0-FFFFFFFF) then encode it (b'XXXXXXXX')
        else: return -1                                                                             # Return an error otherwise

        return self.send_message(self.SET_ACCEPTANCE_MASK_REG + mask + b'\r')

    def set_auto_poll(self, en: bool):
        """
        Sets Auto Poll/Send ON/OFF for received frames. 
        
        :pre This command is accepted only if the CAN channel is closed. 
        
        The value will be saved in EEPROM and remembered next time the PCAN-RS-232 is powered up.
        It is set to OFF by default, to be compatible with old programs written for PCAN-RS-232. 
        Setting it to ON will disable the P and A commands and
        change the reply back from using the t and T command 
        (see these commands for more information on the reply). 
        It is strongly recommended to set this feature and upgrade from the old polling mechanism. 
        Doing so will save bandwith and increases number of CAN frames that can be sent to the PCAN-RS-232. 
        With this feature set, CAN frames will be sent out on the RS232 as soon as the CAN channel is opened.
        
        :param n=0 turn off Auto Poll/Send feature
        :param n=1 turn on Auto Poll/Send feature
        
        :return	-1 when ERROR occurs (typically when the CAN channel is open)
        :return	1 when the Auto poll command is successfully implemented
        """
        en = format(en, '01x').encode('utf-8') # Encode the en argument so the PCAN module can understand it
        return self._send_message_close_only(self.SET_AUTO_POLL + en + b'\r')

    def set_auto_startup(self, n):
        """
        Auto Startup feature (from power on).

        :warning THIS WILL DISABLE TRANSMIT COMMANDS!!! DO NOT USE!!
        
        :pre This command is accepted only if the CAN channel is open. 
        
        Use this function when you have set up CAN
        speed and filters and you want the PCAN-RS-232 to boot up with these
        settings automatically on every power on. Perfect for logging etc. or
        when no master is availible to set up the PCAN-RS-232.
        Note: Auto Send is only possible (see X command), so
        CAN frames are sent out automatically on RS232
        when received on CAN side. No polling is allowed.
        
        :param	n=0 Turn OFF the Auto Startup feature 
        :param	n=1 Turn ON the Auto Startup feature in normal mode.
        :param	n=2 Turn ON the Auto Startup feature in listen only mode
        
        :note The value is saved in EEPROM and is set each time the PCAN-RS-232 is powered up.

        :return	-1 when ERROR occurs (typically the CAN channel is closed)
        :return	1 when the Auto Startup command is successfully executed
        """
        # Input validation
        if isinstance(n, str): n = int(n)                           # Check if n is a string then convert to int
        if n in range(0,3): n = format(n, '01n').encode('utf-8')    # Check if n is in the correct range (0-2) then encode it (b'X')
        else: return -1                                             # Return an error otherwise

        return self._send_message_open_only(self.SET_AUTO_STARTUP + n + b'\r')
    
    def set_can_bitrate_btr0_btr1(self, btr0, btr1):
        """
        Set the BTR0 and BTR1 registers to determine CANbus bitrate

        :pre This command is acccepted only if the CAN channel is closed
        
        :note these values are overwritten by the set_can_bitrate() function. Use that instead

        :return -1 if an ERROR occurs
        :retrun 1 if the BTR0/BTR1 registers are successfully set
        """
        # Input validation
        if isinstance(btr0, str):
            btr0 = btr0.encode('utf-8')
        elif isinstance(btr0, int):
            btr0 = format(btr0, '02x').encode('utf-8')
        else:
            return -1

        if isinstance(btr1, str):
            btr1 = btr1.encode('utf-8')
        elif isinstance(btr1, int):
            btr1 = format(btr1, '02x').encode('utf-8')
        else:
            return -1

        return self._send_message_close_only(self.SET_BTR0_BTR1_RATE + btr0 + btr1 + b'\r')

    def set_can_bitrate(self, n):
        """
        Determines the CANbus bitrate

        :pre This command is accepted only if the CAN channel is closed

        :note These values overwrite the registers provided by set_can_bitrate_btr0_btr1()

        :param n=0 : 10 kbit/s
        :param n=1 : 20 kbit/s
        :param n=2 : 50 kbit/s
        :param n=3 : 100 kbit/s
        :param n=4 : 125 kbit/s
        :param n=5 : 250 kbit/s
        :param n=6 : 500 kbit/s
        :param n=7 : 800 kbit/s
        :param n=8 : 1 Mbit/s

        :return -1 if an ERROR occurs
        :return 1 if the CANbus bitrate is successfully set
        """
        # Input validation
        if isinstance(n, str): n = int(n)                           # Check if n is a string then convert to int
        if n in range(0,9): n = format(n, '01n').encode('utf-8')    # Check if n is in the correct range (0-8) then encode it (b'X')
        else: return -1                                             # Return an error otherwise 

        return self._send_message_close_only(self.SET_CAN_BAUDRATE + n + b'\r')
    
    def set_filter_mode(self, m: bool):
        """
        Sets the PCAN module's filter mode

        :pre This command can only be accepted when the CAN channel is closed

        :note This setting is saved in EEPROM and remembered for next startup

        :param m=0 dual-filter mode
        :param m=1 single-filter mode

        :return -1 if an ERROR occurs
        :retrun 1 if the filter command is successfully implemented
        """
        m = format(m, '01b').encode('utf-8') # Encode the m argument so the PCAN module can understand it
        return self._send_message_close_only(self.SET_FILTER_MODE + m + b'\r')        
    
    def set_uart_bitrate(self, n):
        """
        Setup UART with standard bitrates where n is 0-6.
        
        :pre This command is accepted only if the CAN channel is closed. 
        
        :param	UART bitrate selector n (where n is 0-6)
        :param n=0 . Setup 230400 baud (not guaranteed to work)
        :param n=1 .. Setup 115200 baud
        :param n=2 ... Setup 57600 baud (default when delivered)
        :param n=3 .... Setup 38400 baud
        :param n=4 ..... Setup 19200 baud
        :param n=5 ...... Setup 9600 baud
        :param n=6 ....... Setup 2400 baud
        
        :note The dots above indicate how many times the red LED blinks when the device is powered up.
        :note This is a simple way of showing which RS232 speed is currently configured.
        :note The value is saved in EEPROM and is set each time the PCAN-RS-232 is powered up.
        :note default UART is 57600 baud.
        
        :return -1 if an ERROR occurs
        :retrun 1 if the UART baud is successfully set
        """
        # Input validation
        if isinstance(n, str): n = int(n)                           # Check if n is a string then convert to int
        if n in range(0,7): n = format(n, '01n').encode('utf-8')    # Check if n is in correct range (0-6) then encode (b'X')
        else: return -1                                             # Return an error otherwise

        # Change serial baudrate of PCAN module
        if self._can_open: 
            self.close_channel()
        self.write(self.SET_UART_BAUDRATE + n + b'\r')

        # Adjust serial port baudrate to maintain 
        _n = int(n.decode())
        if   _n == 0: self.baudrate = 230400
        elif _n == 1: self.baudrate = 115200
        elif _n == 2: self.baudrate = 57600 # Default
        elif _n == 3: self.baudrate = 38400
        elif _n == 4: self.baudrate = 19200
        elif _n == 5: self.baudrate = 9600
        elif _n == 6: self.baudrate = 2400

        return self._receive_reply()

    # =====TRANSMIT FUNCTIONS=====

    def transmit_extended_message(self, id, dlc, data):
        """
        Transmits an extended-identifier (29-bit) CAN data frame across the network

        :pre This command is only accepted when the CAN channel is open and auto start = 0

        :param id the CAN message ID as a hex value
        :param dlc the length of the CAN message data as an integer value
        :param data a byte array of the data within the CAN message as a hex string or byte list, equal in size to "dlc" (0-16 characters)

        :return -1 if an ERROR occurs (typically CAN channel is closed, DLC != length(data), or autostart > 0)
        :return 1 if data frame successfully transmitted
        """
        # Input validation
        if isinstance(id, str): id = int(id, 16)                    # Check if ID is a string then convert to int
        if id <= 0x1FFFFFFF: id = format(id, '08x').encode('utf-8') # Check if ID is in correct range (0-0x1FFFFFFF) and encode it (b'XXXXXXXX')
        else: return -1                                             # Return error if not in correct range

        if isinstance(dlc, str): dlc = int(dlc)                         # Check if DLC is a string and convert to int
        if dlc in range(0,9): dlc = format(dlc, '01n').encode('utf-8')  # Check if DLC is in correct range (0-8) and is the length of the data and encode (b'X')
        else: return -1                                                 # Return error if not in correct range or does not equal length of data
        
        if isinstance(data, str): data = data.encode('utf-8')                                       # Check if data is a hex string and encode it
        elif isinstance(data, list): data = ''.join(format(n,'02X') for n in data).encode('utf-8')  # Check if data is a list then format it into string and encode it (b'XX...')
        else: return -1                                                                             # Return error if not string or list

        return self.send_message(b'T' + id + dlc + data + b'\r')

    def transmit_extended_request(self, id, dlc):
        """
        Transmits an extended-identifier (29-bit) CAN request frame across the network

        :pre This command is only accepted when the CAN channel is open

        The CANbus RTR frame does not contain any data. Rather, it is a request to a specified ID to
        transmit a data packet that the sending device desires.

        :param id the CAN request ID as a hex value
        :param dlc the expected length of the incoming CAN data as an int value

        :return -1 if an ERROR occurs (typically CAN channel is closed, DLC != length(data), or autostart > 0)
        :return 1 if data frame successfully transmitted
        """
        # Input validation
        if isinstance(id, str): id = int(id, 16)                    # Check if ID is a hex string and convert to int
        if id <= 0x1FFFFFFF: id = format(id, '08x').encode('utf-8') # Check if ID is in correct range (0-1FFFFFFF) and encode it (b'XXXXXXXX')
        else: return -1                                             # Return error if not in correct range

        if isinstance(dlc, str): dlc = int(dlc)                                 # Check if DLC is a string and convert to int
        if dlc in range(0,9) and dlc: dlc = format(dlc, '01n').encode('utf-8')  # Check if DLC is in correct range (0-8) and encode (b'X')
        else: return -1                                                         # Return error if not in correct range or does not equal length of data

        return self.send_message(b'R' + id + dlc + b'\r')

    def transmit_standard_message(self, id, dlc, data):
        """
        Transmits a standard-identifier (11-bit) CAN data frame across the network

        :pre This command is only accepted when the CAN channel is open

        :param id the CAN message ID as a hex value
        :param dlc the length of the CAN message data as an integer value
        :param data a byte array of the data within the CAN message as a hex string (0-16 characters) or byte list

        :return -1 if an ERROR occurs (typically CAN channel is closed, DLC != length(data), or autostart > 0)
        :return 1 if data frame successfully transmitted
        """
        # Input validation
        if isinstance(id, str): id = int(id, 16)                # Check if ID is a hex string and convert to int
        if id <= 0x7FF: id = format(id, '03x').encode('utf-8')  # Check if ID is in correct range (0-0x7FF) and encode it (b'XXX')
        else: return -1                                         # Return error if not in correct range

        if isinstance(dlc, str): dlc = int(dlc)                         # Check if DLC is a string and convert to int
        if dlc in range(0,9): dlc = format(dlc, '01n').encode('utf-8')  # Check if DLC is in correct range (0-8) and is the length of the data and encode (b'X')
        else: return -1                                                 # Return error if not in correct range or does not equal length of data
        
        if isinstance(data, str): data = data.encode('utf-8')                                       # Check if data is a hex string and encode it
        elif isinstance(data, list): data = ''.join(format(n,'02X') for n in data).encode('utf-8')  # Check if data is a list then format it into string and encode it (b'XX...') 
        else: return -1                                                                             # Return error if not string or list

        # Note: Transmitting can only be performed when the CAN channel is OPEN and AUTOSTART is OFF
        return self.send_message(b't' + id + dlc + data + b'\r')

    def transmit_standard_request(self, id, dlc):
        """
        Transmits a standard-identifier (11-bit) CAN request frame across the network

        :pre This command is only accepted when the CAN channel is open

        The CANbus RTR frame does not contain any data. Rather, it is a request to a specified ID to
        transmit a data packet that the sending device desires.

        :param id the CAN request ID as a hex value
        :param dlc the expected length of the incoming CAN data as an integer value

        :return -1 if an ERROR occurs (typically CAN channel is closed, DLC != length(data), or autostart > 0)
        :return 1 if data frame successfully transmitted
        """
        # Input validation
        if isinstance(id, str): id = int(id, 16)                # Check if ID is a hex string and convert to int
        if id <= 0x7FF: id = format(id, '03x').encode('utf-8')  # Check if ID is in correct range (0-7FF) and encode it (b'XXX')
        else: return -1                                         # Return error if not in correct range

        if isinstance(dlc, str): dlc = int(dlc)                                 # Check if DLC is a string and convert to int
        if dlc in range(0,9) and dlc: dlc = format(dlc, '01n').encode('utf-8')  # Check if DLC is in correct range (0-8) and encode (b'X')
        else: return -1                                                         # Return error if not in correct range or does not equal length of data

        # Note: Transmitting can only be performed when the CAN channel is OPEN and AUTOSTART is OFF
        return self.send_message(b'r' + id + dlc + b'\r')

    # =====UTILITY=====

    def send_message(self, msg):
        """
        Sends the specified message across the serial bus to the PCAN module

        :param The UTF-8 encoded message to be sent

        :return -1 if an ERROR occurs or timeout
        :return 1 if the PCAN module aknowledges the command
        :return the contents of the reception bus if the PCAN module sent data over
        """
        self.write(msg)
        return self._receive_reply()

    def _send_message_close_only(self, msg):
        """
        Sends the specified message to the PCAN module across the serial port.
        Will automatically close and reopen the CAN channel if required.

        :param The UTF-8 encoded message to be sent

        :return -1 if an ERROR occurs
        :return 1 if the PCAN module aknowledges the command
        :return the contents of the reception bus if the PCAN module sent data over
        """
        if self._can_open:
            self.close_channel()
            _res = self.send_message(msg)
            self.open_channel()
            return _res
        else:
            return self.send_message(msg)

    def _send_message_open_only(self, msg):
        """
        Sends the specified message to the PCAN module across the serial port.
        Will automatically reopen and close the CAN channel if required.

        :param The UTF-8 encoded message to be sent

        :return -1 if an ERROR occurs
        :return 1 if the PCAN module aknowledges the command
        :return the contents of the reception bus if the PCAN module sent data over
        """
        if not self._can_open:
            self.open_channel()
            _res = self.send_message(msg)
            self.close_channel()
            return _res
        else:
            return self.send_message(msg)

    def _receive_reply(self):
        """
        Receives data from the PCAN module over the serial port and returns some values

        :return -1 if an ERROR occurs
        :return 1 if the PCAN module aknowledges the command
        :return the contents of the reception bus if the PCAN module sent data over
        """
        _gen_ack = [b'\r', b'\r\r', b'Z\r', b'z\r']
        _rec_buf = self.read_until('\r')
        # print(_rec_buf) # Debug

        if _rec_buf == b'\x07' or _rec_buf == b'': # Message failed to be interpreted or send
            return -1
        elif _rec_buf in _gen_ack: # General Acknowledgement
            return 1
        else:                   # Return full message
            return _rec_buf

    def empty_buffers(self):
        """
        Empties the input/output serial buffers
        """
        self.reset_input_buffer()
        self.reset_output_buffer()

    def parse_frame_message(msg:str):
        """
        Parses a CAN message sent from the PCAN module over the serial bus
        Example: 't1234DEADBEEF' - standard (11-bit) identifier message frame
                'R123456784'    - extended (29-bit) identifier request frame
        Returns a tuple with type, ID, size, and message
        Example: ('t', '00000123', '4', 'DEADBEEF')
                ('R', '00000123', '4')
        """

        _type = msg[0:1] # type is the first character of the message
        _ext = _type == 'T' or _type == 'R' # Determine if the message is an extended (29-bit) identifier frame
        _rtr = _type.lower() == 'r' # Determine if the message is a request frame
        _id = msg[1:4] if not _ext else msg[1:9] # Grab the ID depending on length of it (type-dependent)
        _id = _id.zfill(8)
        _size = msg[4:5] if not _ext else msg[9:10] # Grab the data size
        if not _rtr:
            _data = msg[5:5+int(_size)*2+1] if not _ext else msg[10:10+int(_size)*2+1] # Get the message data bytes depending on the size indicated by _size
        else:
            _data = ""
        return(_type, _id, _size, _data)