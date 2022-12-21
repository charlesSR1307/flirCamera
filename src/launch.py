import os
import PySpin
import numpy as np
from .guiV1 import Ui_MainWindow
from .Flirclass import flirCamera
from matplotlib import pyplot as plt
from .threadReading2 import ThreadClassRead
from PyQt5 import  QtWidgets, QtGui, QtCore

class mywindow(QtWidgets.QMainWindow): 
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        super(mywindow, self).__init__()
        self.camera = flirCamera()
        self.ui = Ui_MainWindow()
        self.ctrl = 0
        self.runVideo = True
        self.ui.setupUi(self)
        self.ui.cameraTab.setCurrentIndex(0)
        self.ui.snapshot.clicked.connect(self.saveSnapshot)
        self.ui.startButton.clicked.connect(self.startVideo)
        self.ui.startButton2.clicked.connect(self.startVideo)
        self.ui.pushButtonConnect.clicked.connect(self.loadCamera)
        self.ui.automaticSavePath.clicked.connect(self.saveFilePath)
        self.ui.checkBoxAFR.stateChanged.connect(self.framRateCheck)
        self.ui.stopButton.clicked.connect(self.stopManualVideoThead)
        self.ui.stopCamera.clicked.connect(self.camera.releaseCamera)
        self.ui.stopButton2.clicked.connect(self.stopCalibrationVideo)
        self.ui.comboBoxGain.currentIndexChanged.connect(self.gainSelect)
        self.ui.startAutomaticSequence.clicked.connect(self.startImageSecuence)
        self.ui.comboBoxExposure.currentIndexChanged.connect(self.exposureSelect)
        self.ui.pushButtonSetParameters.clicked.connect(self.setCameraParameters)
        self.ui.exitButton.clicked.connect(QtWidgets.QApplication.instance().quit)
        self.ui.checkBoxcalibrate.stateChanged.connect(self.exposureTimeCalibration)
        
        self.threadRead = ThreadClassRead(parent=None, index=1)
        self.threadRead.start()
        self.threadRead.any_signal.connect(self.readArduino)
        
    def framRateCheck(self):
        if self.ui.checkBoxAFR.isChecked():
            self.ui.editFrameRate.setEnabled(True)
        else:
            self.ui.editFrameRate.setDisabled(True)

    def gainSelect(self):
        if self.ui.comboBoxGain.currentIndex() == 0:
            self.ui.editGain.setEnabled(True)
        else:
            self.ui.editGain.setDisabled(True)
            
    def exposureSelect(self):
        if self.ui.comboBoxExposure.currentIndex() == 0:
            self.ui.editExposure.setEnabled(True)
        else:
            self.ui.editExposure.setEnabled(False)
    
    def loadCamera(self):
        if self.camera.instanceCamera():
            if self.camera.runSingleCamera():
                self.ui.pushButtonSetParameters.setEnabled(True)
                self.ui.labelCameraInfo.setText(self.camera.devieName)
                self.ui.editWidth.setText(str(self.camera.width))
                self.ui.editHeight.setText(str(self.camera.height))
                self.ui.editGain.setText(str(self.camera.gain))
                self.ui.editGamma.setText(str(self.camera.gamma))
                self.ui.editFrameRate.setText(str(self.camera.frameRate))
                self.ui.editExposure.setText(str(self.camera.exposureTime))
            
                if self.camera.gainAuto == 0:
                    self.ui.comboBoxGain.setCurrentIndex(0)
                elif self.camera.gainAuto == 1:
                    self.ui.comboBoxGain.setCurrentIndex(1)
                elif self.camera.gainAuto == 2:
                    self.ui.comboBoxGain.setCurrentIndex(2)
                    
                if self.camera.exposureAuto == 0:
                    self.ui.comboBoxExposure.setCurrentIndex(0)
                    self.ui.editExposure.setEnabled(True)
                elif self.camera.exposureAuto == 1:
                    self.ui.comboBoxExposure.setCurrentIndex(1)
                elif self.camera.exposureAuto == 2:
                    self.ui.comboBoxExposure.setCurrentIndex(2)
                
                if self.camera.pixelFormat == 'Mono8':
                    self.ui.comboBoxPixelFormat.setCurrentIndex(0)
                elif self.camera.pixelFormat == 'Mono16':
                    self.ui.comboBoxPixelFormat.setCurrentIndex(1)
                elif self.camera.pixelFormat == 'Mono10Packed':
                    self.ui.comboBoxPixelFormat.setCurrentIndex(2)
                elif self.camera.pixelFormat == 'Mono12Packed':
                    self.ui.comboBoxPixelFormat.setCurrentIndex(3)
                elif self.camera.pixelFormat == 'Mono10p':
                    self.ui.comboBoxPixelFormat.setCurrentIndex(4)
                elif self.camera.pixelFormat == 'Mono12p':
                    self.ui.comboBoxPixelFormat.setCurrentIndex(5)
        else:
            QtWidgets.QMessageBox
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Camera not connected")
            msg.setWindowTitle("Error")
            msg.exec_()

    def setCameraParameters(self):
        try:
            self.camera.cam.Width.SetValue(int(self.ui.editWidth.text()))
            self.camera.cam.Height.SetValue(int(self.ui.editHeight.text()))
            self.camera.cam.Gamma.SetValue(float(self.ui.editGamma.text()))
            
            if self.ui.comboBoxExposure.currentIndex() == 0:
                self.camera.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
                self.camera.cam.ExposureTime.SetValue(float(self.ui.editExposure.text()))
            elif self.ui.comboBoxExposure.currentIndex() == 1:
                self.camera.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Once)
            elif self.ui.comboBoxExposure.currentIndex() == 2:
                self.camera.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
            
            if self.ui.checkBoxAFR.isChecked():
                self.camera.cam.AcquisitionFrameRateEnable.SetValue(True)
                self.camera.cam.AcquisitionFrameRate.SetValue(float(self.ui.editFrameRate.text()))
            
            if self.ui.comboBoxGain.currentIndex() == 0:
                self.camera.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
                self.camera.cam.Gain.SetValue(float(self.ui.editGain.text()))
            elif self.ui.comboBoxGain.currentIndex() == 1:
                self.camera.cam.GainAuto.SetValue(PySpin.GainAuto_Once)
            elif self.ui.comboBoxGain.currentIndex() == 2:
                self.camera.cam.GainAuto.SetValue(PySpin.GainAuto_Continuous)
            
            if self.ui.comboBoxPixelFormat.currentIndex() == 0:
                self.camera.cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono8)
            elif self.ui.comboBoxPixelFormat.currentIndex() == 1:
                self.camera.cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono16)
            elif self.ui.comboBoxPixelFormat.currentIndex() == 2:
                self.camera.cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono10Packed)
            elif self.ui.comboBoxPixelFormat.currentIndex() == 3:
                self.camera.cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono12Packed)
            elif self.ui.comboBoxPixelFormat.currentIndex() == 4:
                self.camera.cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono10p)
            elif self.ui.comboBoxPixelFormat.currentIndex() == 5:
                self.camera.cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono12p)
            
            self.camera.disconnect()
        except:
            pass
    
    def exposureTimeCalibration(self):
        self.histCtrl = 1
        fig, ax = plt.subplots()
        ax.set_title('Histogram (grayscale)')
        ax.set_xlabel('intensity')
        ax.set_ylabel('Frequency')
        lw = 3
        alpha = 0.5
        if self.camera.pixelFormat == "Mono8":
            bins = 256
        if self.camera.pixelFormat == "Mono12":
            bins = 4096
        lineGray, = ax.plot(np.arange(bins), np.zeros((bins,1)), c='k', lw=lw)
        ax.set_xlim(0, bins-1)
        ax.set_ylim(0, 0.1)
        plt.ion() 
        plt.show()
        
        if self.histCtrl == 1:
            numPixels = np.prod(self.cvImage.shape[:])
            histogram, bins = np.histogram(self.cvImage.ravel(),256,[0,256]) / numPixels
            lineGray.set_ydata(histogram)
            fig.canvas.draw()
        
        if self.ui.checkBoxcalibrate.isChecked():
            if self.ui.setpointEditCalibration.text() == '':
                self.ui.checkBoxcalibrate.setChecked(False)
                QtWidgets.QMessageBox
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("Setpoint not defined!")
                msg.setWindowTitle("Error")
                msg.exec_()

            else:
                setpoint = int(self.ui.setpointEditCalibration.text())
                if self.camera.pixelFormat == 'Mono8':
                    imgMean = np.mean(self.cvImage)
                    
                offset = setpoint - imgMean
                exposure = self.camera.exposureTime
                if offset < -30:
                    self.camera.cam.ExposureTime.SetValue(exposure - 30)
                elif offset > 30:
                    self.camera.cam.ExposureTime.SetValue(exposure + 30)
                elif offset < -1 and offset >= -30:
                    self.camera.cam.ExposureTime.SetValue(exposure - 2)
                elif offset > 1 and offset <= 30:
                    self.camera.cam.ExposureTime.SetValue(exposure + 2)
                elif offset >= -1 and offset <= 1:
                    self.camera.cam.ExposureTime.SetValue(exposure)
                
                self.ui.exposureEditCalibration.setText(str(exposure))
                self.ui.checkBoxcalibrate.setChecked(False)

                QtWidgets.QMessageBox
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText("Calibration done")
                msg.setWindowTitle("Information")
                msg.exec_()
    
    def startVideo(self):
        try:
            if self.camera.instanceCamera():
                self.camera.starCameraContinuousAdquisition()
                self.ui.manualModeVideoState.setTitle('Live video feed On')
                self.isRunning = True
                self.image = [] 
                while self.isRunning:
                    self.processor = PySpin.ImageProcessor()
                    self.processor.SetColorProcessing(PySpin.HQ_LINEAR)
                    
                    self.imageResult = self.camera.cam.GetNextImage(1000)
                    imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono8)
                    self.image = imageConverted.GetNDArray()
                    self.imageResult.Release()
                    
                    QtWidgets.QApplication.processEvents()
                    self.timer = QtCore.QTimer()
                    if self.ui.cameraTab.currentIndex()==1:
                        self.timer.timeout.connect(self.calibrationModeVideoFeed)
                    elif self.ui.cameraTab.currentIndex()==2:
                        self.timer.timeout.connect(self.manualModeVideoFeed)
                    self.timer.start(3)
        except:
            pass
        
    def manualModeVideoFeed(self):
        try:
            cvImage = self.image
            h, w = cvImage.shape
            self.image = QtGui.QImage(cvImage, w, h, cvImage.strides[0], QtGui.QImage.Format_Grayscale8)
            self.ui.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.image))
        except:
            pass
    
    def calibrationModeVideoFeed(self):
        try:
            cvImage = self.image
            h, w = cvImage.shape
            self.image = QtGui.QImage(cvImage, w, h, cvImage.strides[0], QtGui.QImage.Format_Grayscale8)
            self.ui.calibrationImage.setPixmap(QtGui.QPixmap.fromImage(self.image))
        except:
            pass
    
    def stopCalibrationVideo(self):
        try:
            self.camera.cam.EndAcquisition()
            self.isRunning = False
            self.ui.calibrationModeVideoState.setTitle('No video feed ...')
            self.ui.calibrationImage.setPixmap(QtGui.QPixmap())
        except:
            pass
        
    def stopManualVideoThead(self):
        try:
            self.camera.cam.EndAcquisition()
            self.isRunning = False
            self.ui.manualModeVideoState.setTitle('No video feed ...')
            self.ui.imageLabel.setPixmap(QtGui.QPixmap())
        except:
            pass
    
    def saveSnapshot(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(None, 'Single Image Save', os.getcwd(), 'All Files(*.*)')
        
        if self.camera.pixelFormat == 'Mono8':
            imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono8)
        elif self.camera.pixelFormat == 'Mono16':
            imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono16)
        elif self.camera.pixelFormat == 'Mono10Packed':
            imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono10Packed)
        elif self.camera.pixelFormat == 'Mono12Packed':
            imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono12Packed)
        elif self.camera.pixelFormat == 'Mono10p':
            imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono10p)
        elif self.camera.pixelFormat == 'Mono12p':
            imageConverted = self.camera.cam.processor.Convert(self.camera.imageResult, PySpin.PixelFormat_Mono12p)
        
        fileExtension = self.ui.comboBoxFormat.currentText()   
        imageConverted.Save(filename[0] + '.' + fileExtension)

    def startImageSecuence(self):
        self.yData = []
        self.xData = []
        self.samples = 0
        
        self.threadRead.t_est = float(self.ui.stabTimeEdit.text())
        self.threadRead.ti = float(self.ui.startTempEdit.text())
        self.threadRead.tf = float(self.ui.finalTempEdit.text())
        self.threadRead.paso_t = float(self.ui.stepTempEdit.text())
        
        while True:
            QtWidgets.QApplication.processEvents()
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.realTimePlotData)
            self.timer.start(1)

    def saveFilePath(self):
        self.path = QtWidgets.QFileDialog.getSaveFileName(None, 'Single Image Save', os.getcwd(), 'All Files(*.*)')

    def saveSequence(self):
        try:
            fileExtension = self.ui.comboBoxFormat.currentText()
            
            self.imageResult = self.camera.cam.GetNextImage(1000)
            if self.camera.pixelFormat == 'Mono8':
                self.imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono8)
            elif self.camera.pixelFormat == 'Mono16':
                self.imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono16)
            elif self.camera.pixelFormat == 'Mono10Packed':
                self.imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono10Packed)
            elif self.camera.pixelFormat == 'Mono12Packed':
                self.imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono12Packed)
            elif self.camera.pixelFormat == 'Mono10p':
                self.imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono10p)
            elif self.camera.pixelFormat == 'Mono12p':
                self.imageConverted = self.processor.Convert(self.imageResult, PySpin.PixelFormat_Mono12p)
            
            filename = '{}/{}_{}.{}'.format(self.path, self.ui.imagePrefixEdit.text(), self.count, fileExtension)
            self.count += 1
            
            self.imageConverted.Save(filename)
            self.imageResult.Release()

            #self.camera.cam.EndAcquisition()
            
        except:
            pass
        
    def readArduino(self, data):
        try:
            if ~data[1]:
                data2 = data[0]
                self.realTimePlotData(data2)
            elif data[1]:
                self.saveSequence()
        except:
            pass
    
    def realTimePlotData(self, data=None):
        try:
            if data!=None:
                self.ui.label_18.setText(str(data))
                #data = np.random.random()
                self.yData.append(data)
                self.xData.append(self.samples)
                self.samples += 1
                if len(self.yData)>10:
                    self.yData.pop(0)
                    self.xData.pop(0)
                self.ui.realTimegraph.setXRange(self.samples-5, self.samples-1)
                self.ui.realTimegraph.plot(x=self.xData, y=self.yData, symbol='x')
            else:
                pass
        except:
            pass 
        
