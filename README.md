# PCAN UI

PCAN UI is an application built to add a user interface to the PS-RS-232 device and add a Python library to integrate it with other embedded applications

Version: 0.1.0

## Installation

Install [Python 3.9.x](https://www.python.org/downloads/) or higher to get started.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install tkinter and pyserial

```bash
pip install tkinter
```

```bash
pip install pyserial
```

## Usage

1. Run PCAN_Interface_Application.py OR
2. Run the pre-combiled application located in /dist

Note: Pre-compiled applicaton only compatible with Windows 10 64-bit

## Application Notes
This application is intended to breakout the configuration settings of the PCAN-RS-232 device and allow users to send/receive CANbus messages over RS-232 serial.
There are 4 main sections to the user interface: the configuration commands (left), the device information and feedback (bottom), the CAN message creator (right), and the serial reception terminal (center).

### Configuration commands

Command | Description
| :---: |  :--- 
STAT    | Get PCAN device status
INFO    | Get PCAN device information (serial number, hardware version, software version)
CODE    | Set the Acceptance Code Filter for the PCAN (see SJA1000 datasheet)
MASK    | Set the Acceptance Mask Filter for the PCAN (see SJA1000 datasheet)
POLL    | Enable auotpolling (transmit CAN message over serial as soon as it is received)
START   | Enable auto start up
CBAUD   | Configure the CANbus bitrate
SBAUD   | Configure the serial terminal settings
FILTER  | Enable single or dual-channel filtering (see SJA1000 datasheet)
TIME    | Enable CAN message reception timestamps
EEPROM  | Save settings to non-volatile storage

**Note: there is a bug in the PCAN firmware. When auto start up is enabled, the PCAN will not be able to transmit CAN messages**

### CAN Message Terminal

By default, PCAN UI will open and enable the defualt settings on the UI and on the PCAN device. When the OPEN button is selected, any CAN messages received by the PCAN will automatically display in the central terminal in the following formats:
* tXXXYZZ...
* TXXXXXXXXYZZ...
* rXXXY
* RXXXXXXXXY

Where "t" stands for 11-bit identifier message, "T" stands for 29-bit identifier message, "r' stands for 11-bit identifier request, "R" stands for 29-bit request.

### Sending CAN Transmissions and Requests

To send a CAN transmission, first open the CAN channel using the "OPEN" button. Then, select if the message will be an extended identifier using the "EXT" toggle. Finally, fill in the identifier, DLC, and byte entries with your message. The application should limit the identifier to the maximum allowable value (depending on standard or extended identifier) and restrict the byte entry fields to hexadecimal values. **Note: if the number of byte entries exceeds the DLC value, the message will be truncated to the DLC length.**

To send a CAN request, following the same initial steps as a transmission, but select the "RTR" toggle. This will disable the entries for the data bytes and allow you to enter a target identifier (11-bit or 29-bit depending on "EXT" toggle) and a desired DLC.

## Improvements and Bug Fixes
- [] Add logger for the serial reception terminal
- [] Add a logger for application events
- [] Format the serial reception terminal to be more intuitive and user-friendly
- [] Replace "SBAUD" command with menu bar for serial port configuration
- [] Implement database importing for automatically interpretting CAN messages based on identifiers and ICDs
- [] Breakout PCAN library to seperate wheel file or external library that can be easily downloaded/used indepentently of PCAN UI

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.

Copyright 2021 Braidan Duffy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
