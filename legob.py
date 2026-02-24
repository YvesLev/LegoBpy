""" Allow interaction with Lego 9751 / 70909 command module. """
__author__ = 'Originally from Steven Shamlian (dacta.py), Modified by Yves Levesque for Python 3.13 and other improvements'
__version__ = '2025-01-08. Origilnaly from 2014-04-03'
__license__ = ('This software is released under rev. 42 of the Beer-Ware '
               'license. Lego@shamlian.net wrote this software. As long as '
               'you retain this notice, you can do whatever you want with it. '
               'If we meet some day, and you think it\'s worth it, you can '
               'buy me a beer in return. --Steve')

import serial, threading, queue, time
_outQueue = queue.Queue() #queue for outgoing comms
_iRaw=[0]*9 # Raw Value of each port coming from the serial buffer
_iRot=[0]*9 # Rotation Sensor value 0-15 (16 step per turn)
_firstReadDone = False

class LegoB:
    _ser = None # serial object for raw comms
    
    _threadList = [] # list of active threads -- in, out, and keepalive
    _running = threading.Event() # used to safely shut things down on close()
    _iRot=[0]*9
    _firstReadDone = False
    
    # initialization strings
    _INIT_ON = b'p\0'
    _INIT_START = b'###Do you byte, when I knock?$$$'
    _INIT_RETURN = b'###Just a bit off the block!$$$'

    _ix=[0,14,10,6,2,16,12,8,4] # index of lego ports in the read buffer
    
    # commands from http://www.blockcad.net/dacta/
    CMD_NOP = b'\x02'
    CMD_PORTONL = b'\x10'
    CMD_PORTONR = b'\x18'
    CMD_PORTREV = b'\x20'
    CMD_PORTONX = b'\x28'
    CMD_PORTOFF = b'\x30' # check to see if low nibble does anything
    CMD_PORTDRL = b'\x40'
    CMD_PORTDRR = b'\x48'
    CMD_KILLALL = b'\x70' # completely disconnects interface

    _PARAM_POWER = '\xb0'

    isRunning = False
    
    PORT_A = 0
    PORT_B = 1
    PORT_C = 2
    PORT_D = 3
    PORT_E = 4
    PORT_F = 5
    PORT_G = 6
    PORT_H = 7
    PORT_1 = 0
    PORT_2 = 1
    PORT_3 = 2
    PORT_4 = 3
    PORT_5 = 4
    PORT_6 = 5
    PORT_7 = 6
    PORT_8 = 7
        

    def taskKeepAlive(self):
        """ Internal task for sending a nop every 2 seconds (or so). """
        while self._running.isSet():
            time.sleep(1.9)
            _outQueue.put(self.CMD_NOP)

    def taskWrite(self):
        """ Internal task to write commands to the serial port if available. """
        while self._running.isSet():
            if not _outQueue.empty():
                item = _outQueue.get(block=False)
                if self._ser == None:
                    print(repr(item))
                else:
                    self._ser.write(item)
            time.sleep(0.005)

    def out(self, portnum):
        if portnum not in self.outCmd:
            self.outCmd[portnum] = OutCmd(portnum)
        return self.outCmd[portnum]

    def inp(self, portnum):
        if portnum not in self.inpCmd:
            self.inpCmd[portnum] = InpCmd(portnum)
        return self.inpCmd[portnum]

    def taskRead(self):
        """ Internal state machine to read data from the 70909 / 9751. """
        ix=self._ix
        
        if self._ser == None:
            print("Note: no inputs are available.")
            return

        while self._running.isSet():
            global _firstReadDone
            
            buff=b''
            _bufftot = 0
            _buffread = 0
            while _bufftot < 19 and self._running.isSet():
                buff = self._ser.read(19-_bufftot)
                _buffread = len(buff)
                _bufftot += _buffread
                if _bufftot >= 19:
                    checksum = 0
                    for c in buff:
                        checksum += c
                    if (checksum & 0xff) != 0xff:
                        buff = buff[1:_bufftot]
                        _bufftot -= 1
                
            if self._running.isSet():
                for x in range(9):
                    _iRaw[x]=int.from_bytes(buff[ix[x]:ix[x]+2],"big")
                    if x>0:
                        change = _iRaw[x] & 3
                        if _iRaw[x] & 4 == 0 : change *= -1
                        _iRot[x] += change
                _firstReadDone = True


    def close(self):
        """ Safely terminates helper threads and closes serial port. """
        
        print("Shutting down.")
        _outQueue.put(self.CMD_KILLALL)
        time.sleep(0.5)
        self._running.clear()
        for thread in self._threadList:
            while thread.is_alive():
                time.sleep(0.1)
        self._threadList.clear()
        if self._ser != None:
            self._ser.close()
        isRunning= False
        _iRot=[0]*9
    
    def __init__(self, comPort):
        global _firstReadDone
        
        self.outCmd = {}
        self.inpCmd = {}
        
        """ Initialize communications to 9751/70909 and launch helper threads.
        comPort -- COM port number or name (like 'COM1' or '/dev/ttyUSB0')
        """
        
        try:
            self._ser = serial.Serial(comPort, 9600, timeout = 2)
        except serial.SerialException:
            print("Could not open port " + repr(comPort) + "; using stdout instead.")
            self._ser = None

        self._threadList.append(threading.Thread(target = self.taskKeepAlive))
        self._threadList.append(threading.Thread(target = self.taskWrite))
        self._threadList.append(threading.Thread(target = self.taskRead))

        if self._ser != None:
            self._ser.reset_input_buffer()
            self._ser.write(self._INIT_ON)
            self._ser.write(self._INIT_START)
            confirmation = self._ser.read(len(self._INIT_RETURN))
            while confirmation != self._INIT_RETURN:
                print(confirmation) # debug
                confirmation = confirmation[1:] + self._ser.read(1)
            print("Got confirmation string.")

        self._running.set()
        isRunning=True
        for thread in self._threadList:
            thread.start()
        while _firstReadDone == False:
            time.sleep(0.010)

    def __del__(self):
        """ Should be called on close, but there's a bug. Call close() instead.
        """
        self.close()

class OutCmd:
    def __init__(self, port):
        self.port = (port-1) & 7
        self.power = 7
        self.ton = 50
    def on(self):
        _outQueue.put((b'\x28'[0] | self.port).to_bytes(1,'big'))
    def onl(self):
        _outQueue.put((b'\x10'[0] | self.port).to_bytes(1,'big'))
    def onr(self):
        _outQueue.put((b'\x18'[0] | self.port).to_bytes(1,'big'))
    def off(self):
        _outQueue.put((b'\x38'[0] | self.port).to_bytes(1,'big'))
    def float(self):
        _outQueue.put((b'\x30'[0] | self.port).to_bytes(1,'big'))
    def rev(self):
        _outQueue.put((b'\x20'[0] | self.port).to_bytes(1,'big'))
    def l(self):
        _outQueue.put((b'\x40'[0] | self.port).to_bytes(1,'big'))
    def r(self):
        _outQueue.put((b'\x48'[0] | self.port).to_bytes(1,'big'))
    def pow(self, power):
        self.power = power & 7
        _outQueue.put((b'\xB0'[0] | self.power).to_bytes(1,'big') + (1 << self.port).to_bytes(1,'big'))
    def onfor(self, ton):
        self.ton = ton & 0xFF
        _outQueue.put((b'\xC0'[0] | self.port).to_bytes(1,'big') + (self.ton).to_bytes(1,'big'))

class InpCmd:
    def __init__(self, port):
        self.port = port
    @property
    def on(self):
        if self.port>0:
            iOn=(_iRaw[self.port] & 0x0008)==0
        else:
            iOn=(_iRaw[self.port] & 0x1000)!=0
        return iOn
    
    @property
    def val(self):
        iVal=(_iRaw[self.port]>>6) & 0x03FF
        return iVal

    @property
    def tempf(self):
        iVal=(_iRaw[self.port]>>6) & 0x03FF
        return (760.0 - iVal) / 4.4 + 32.0

    @property
    def tempc(self):
        iVal=(_iRaw[self.port]>>6) & 0x03FF
        return ((760.0 - iVal) / 4.4) * 5.0 / 9.0

    @property
    def rot(self):
        return _iRot[self.port]
    
    @rot.setter
    def rot(self, r):
        _iRot[self.port] = r