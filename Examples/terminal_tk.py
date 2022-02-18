#!usr/bin/python3
#Filename: gui_serial_blocking.py
#Date: 30 September 2017
#Trying to receive serial port data into GUI text window.
#https://raspberrypi.stackexchange.com/questions/73148/want-to-read-com-port-data-and-write-into-tkinter-text-window

from tkinter import *
from serial import SerialException

class Application(Frame):
    """Build the windows to show 20x10 Customer Pole Display data"""

    def __init__(self, master):
        super(Application, self).__init__(master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.label1 = Label(self, text='Text window for data from serial port:')
        self.label1.grid(row=0, column=0, sticky =W)

        self.text1 = Text(self, width=20, height=2)
        self.text1.grid(row=1, column=0)
        self.text1.focus_set()


    def writeDisplay(self,inputCharacter):
        myCharacter = inputCharacter
        varText = self.text1.get("1.0", END)
        varReplaced = varText + myCharacter
        self.text1.delete("1.0", END)
        self.text1.insert(END, varReplaced)

    def openDisplay(self):
        root = Tk()
        root.title('Text widget test')
        root.geometry('360x250')
        #app = Application(root)
        app.mainloop()

class mySerialport():
    import serial, time    #initialization and open the port
    global ser
    ser = serial.Serial()        
    ser.port = "/dev/ttyUSB0"
    #ser.port = "COM2"
    ser.baudrate = 9600
    ser.bytesize = serial.EIGHTBITS #number of bits per bytes
    ser.parity = serial.PARITY_NONE #set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE #number of stop bits
    #ser.timeout = None          #block read
    ser.timeout = 1            #non-block read
    #ser.timeout = 2              #timeout block read
    ser.xonxoff = False     #disable software flow control
    ser.rtscts = False     #disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
    ser.writeTimeout = 2     #timeout for write
                            #possible timeout values:
                            #    1. None: wait forever, block call
                            #    2. 0: non-blocking mode, return immediately
                            #    3. x, x is bigger than 0, float allowed, timeout block call

    def myOpenSerialPort():
        try: 
            ser.open()
        except SerialException:
            print ("error open serial port: " + ser.port )
            exit()

    def myReadbyte():
        if ser.isOpen():
            try:            
                response = ser.readline(1)
                return(response)
            #except Exception, e1:
            except SerialException as e1:
                print ("error communicating...: " + str(e1))
        else:
            print ("cannot open serial port ")


if __name__ == "__main__":
    root = Tk()
    root.title('Text widget test')
    root.geometry('360x250')
    app = Application(root)
    app.mainloop()       

    #Open the serial port and get date.    
    mySerialport() #Create serial port.
    mySerialport.myOpenSerialPort() #Open the port.

    #Get serial data forever and write to GUI
    while(True):

        #getting serial data
        foo= mySerialport.myReadbyte()

        #writing serial data to display.
        #Application.writeDisplay(foo)   #Place holder for writing to GUI text window.

        #For development, print to shell instead.
        print(foo.decode()) 