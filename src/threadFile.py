from PyQt5.QtCore import pyqtSignal, QThread

import time
class ThreadClass(QThread):
    any_signal = pyqtSignal(int)
    def __init__(self, parent=None, index=0):
        super(ThreadClass, self).__init__(parent)
        self.index=index
        self.is_running=True
    
    def run(self):
        #print('Starting thread...', self.index)
        cnt=0
        while True:
            time.sleep(1)
            cnt+=1
            self.any_signal.emit(cnt)
    
    def stop(self):
        self.is_running = False
        #print('Stopping thread...', self.index)
        self.terminate()
