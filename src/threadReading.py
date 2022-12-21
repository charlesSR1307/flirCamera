import time
from arduinoRead import mainRead
from PyQt5.QtCore import pyqtSignal, QThread

class ThreadClassRead(QThread, ):
    any_signal = pyqtSignal(object)
    def __init__(self, parent=None, index=0, **kwargs):
        super(ThreadClassRead, self).__init__(parent)
        self.index=index
        self.is_running=True
        self.readData = mainRead()
        self.ti = None
        self.tf = None
        self.paso_t = None
        self.t_est = None
        
    def run(self):
        #print('Starting thread...', self.index)
        while True:
            time.sleep(0.0001)
            data = self.readData.readData(self.ti, self.tf, self.paso_t, self.t_est)
            self.any_signal.emit(data)
    
    def stop(self):
        self.is_running = False
        #print('Stopping thread...', self.index)
        self.terminate()
