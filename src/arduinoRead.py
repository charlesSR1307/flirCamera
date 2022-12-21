import time
import serial
import numpy as np
import serial.tools.list_ports
from abc import abstractmethod

# Separar envio y lectura de datos del arduino}
# de los ciclos de verificación del código
# Probar combinar el codigo de lectura del arduino con el hilo

class mainRead():
    def __init__(self):
        self.ser = 0
        
    @abstractmethod
    def readData(self, ti, tf, paso_t, t_est):
        try:
            val = None
            if self.ser != 0:
                self.ser.flush()

            ports = serial.tools.list_ports.comports()
            for port in ports:
                if 'ACM0' in port.device:
                    self.ser = serial.Serial(port.device,115200, timeout=1, write_timeout=1)
                    val = "esperando"
                    if ti != None:
                        temps = np.arange(ti,tf+paso_t,paso_t) 
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

                                time.sleep(t_est)
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
                                return [T, setpoint]                                    

                        self.ser.write(str(25).encode('utf-8'))
                        self.ser.close()
        except:
            return 'Error'


obj = mainRead()
while True:
    x, y = obj.readData(25, 55, 10, 1)