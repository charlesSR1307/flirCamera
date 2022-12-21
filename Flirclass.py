import PySpin

class flirCamera():
    def __init__(self):
        self.isRunning = True
    
    def instanceCamera(self):
        self.systemInstance = PySpin.System.GetInstance()
        self.camList = self.systemInstance.GetCameras()
        numCameras = self.camList.GetSize()
        
        if numCameras == 0:
            self.camList.Clear()
            self.systemInstance.ReleaseInstance()
            return 0
        else:
            self.cam = self.camList[0]
            return 1
        
    def releaseCamera(self):
        self.cam.EndAcquisition()
        self.cam.DeInit()
        del self.cam
        self.camList.Clear()
        self.systemInstance.ReleaseInstance()
        
    def runSingleCamera(self):
        try:
            self.nodemapTldevice = self.cam.GetTLDeviceNodeMap()
            self.devieName = self.printDeviceInfo()
            self.cam.Init()
            self.nodemap = self.cam.GetNodeMap()
            self.gain = self.cam.Gain.GetValue()
            self.gainAuto = self.cam.GainAuto.GetValue()
            self.exposure = self.cam.ExposureTime.GetValue()
            self.exposureAuto = self.cam.ExposureAuto.GetValue()
            self.gamma = self.cam.Gamma.GetValue()
            self.temperature = self.cam.DeviceTemperature.GetValue()
            self.pixelFormat = self.cam.PixelFormat.GetCurrentEntry().GetSymbolic()
            self.width = self.cam.Width.GetValue()
            self.height = self.cam.Height.GetValue()
            self.frameRate = self.cam.AcquisitionFrameRate()
            self.exposureTime = self.cam.ExposureTime()
            self.adquisitionMode = self.cam.AcquisitionMode()
            self.isRunning=True
            return 1
        except:
            return 0
    
    def printDeviceInfo(self):
        try:
            nodeDeviceInformation = PySpin.CCategoryPtr(self.nodemapTldevice.GetNode('DeviceInformation'))

            if PySpin.IsAvailable(nodeDeviceInformation) and PySpin.IsReadable(nodeDeviceInformation):
                features = nodeDeviceInformation.GetFeatures()
                feature = features[4]
                node_feature = PySpin.CValuePtr(feature)
                if node_feature.GetName() == 'DeviceModelName':
                    result = node_feature.ToString()
            else:
                result = 'not available'

        except PySpin.SpinnakerException as ex:
            #print('Error: %s' % ex)
            return False

        return result

    def getCameraParameters(self):
        self.gain = self.cam.Gain.GetValue()
        self.exposure = self.cam.ExposureTime.GetValue()
        self.fps = self.cam.AcquisitionFrameRate.GetValue()
        self.gamma = self.cam.Gamma.GetValue()
        self.frameRate = self.cam.FrameRate.GetValue()
        self.temperature = self.cam.DeviceTemperature.GetValue()
        self.pixelFormat = self.cam.PixelFormat.GetCurrentEntry().GetSymbolic()
    
    def starCameraContinuousAdquisition(self):        
        nodeAcquisitionMode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
        node_acquisition_mode_continuous = nodeAcquisitionMode.GetEntryByName('Continuous')
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        nodeAcquisitionMode.SetIntValue(acquisition_mode_continuous)

        self.cam.BeginAcquisition()
    