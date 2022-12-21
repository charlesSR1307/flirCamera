import time
import serial
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread

class ThreadClassRead(QThread, ):
    any_signal = pyqtSignal(object)
    def __init__(self, parent=None, index=0, **kwargs):
        super(ThreadClassRead, self).__init__(parent)
        self.index=index
        self.is_running=True
        self.ti = None
        self.tf = None
        self.paso_t = None
        self.t_est = None
        self.ser = 0
        
    def connectArd(self):
        try:
            val = None
            if self.ser != 0:
                self.ser.flush()

            ports = serial.tools.list_ports.comports()
            for port in ports:
                if 'ACM0' in port.device:
                    self.ser = serial.Serial(port.device,115200, timeout=1, write_timeout=1)
            return 1
        
        except:
            return 0
        
    def run(self):
        if self.connectArd():
            while True:
                val = "esperando"
                if self.ti != None:
                    temps = np.arange(self.ti,self.tf+self.paso_t,self.paso_t) 
                    num = 0
                    for k in range(1):
                        for i in temps:
                            num = num + 1
                            print("i:" + str(i))                                
                            self.ser.write(str(i).encode('utf-8'))
                            self.ser.reset_input_buffer()
                            time.sleep(1)
                            self.ser.write(str(i).encode('utf-8'))
                            self.ser.reset_input_buffer()       

                            time.sleep(self.t_est)
                            setpoint=False

                            while setpoint == False:
                                self.ser.write(str(i).encode('utf-8'))
                                self.ser.reset_input_buffer()  
                                self.ser.flush()
                                T = float(self.ser.readline().decode("utf-8")[0:-2])
                                print(T)
                                
                                if abs(T-i) < 0.5:         
                                    setpoint = True
                                    print(T)

                            self.any_signal.emit([T, setpoint])

                    self.ser.write(str(25).encode('utf-8'))
                    self.ser.close()
    
                time.sleep(0.0001)
    
    def stop(self):
        self.is_running = False
        self.terminate()