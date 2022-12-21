import os
import PySpin
import sys
import cv2

def acquire_images(cam, nodemap, nodemap_tldevice):
    try:
        result = True

        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        node_acquisition_mode_single_frame = node_acquisition_mode.GetEntryByName('SingleFrame')
        node_acquisition_mode_multi_frame = node_acquisition_mode.GetEntryByName('MultiFrame')
        
        #acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        #node_acquisition_mode_single_frame = node_acquisition_mode_single_frame.GetValue()
        #node_acquisition_mode_multi_frame = node_acquisition_mode_multi_frame.GetValue()

        acquisition_mode = int(input('Seleccione el modo de adquisición: \n 0: Continuo \n 1: Captura de un frame \n 2: Captura de múltiples frames \n'))
        # Set integer value from entry node as new value of enumeration node
        if acquisition_mode > 2 or acquisition_mode < 0:
            print('Ha seleccionado una opción no válida')
        else:
            node_acquisition_mode.SetIntValue(acquisition_mode)
            
            # Set size
            cam.Width.SetValue(1080)
            cam.Height.SetValue(720)
            
            # Get Gain
            gain = cam.Gain.GetValue()
            # cam.GainAuto.SetValue(PySpin.GainAuto_SingleFrame)
            # Get Exposure - micro seconds
            exposure = cam.ExposureTime.GetValue()
            # cam.ExposureAuto.SetValue(PySpin.ExposureAuto_SingleFrame)
            
            # FPS
            fps = cam.AcquisitionFrameRate.GetValue()
            
            # Gamma
            #cam.GammaEnable.SetValue(True)
            gamma = cam.Gamma.GetValue()

            # Temperature
            temperature = cam.DevziceTemperature.GetValue()
            
            # Pixel
            # Image Bits
            # 0 - Mono8
            # 1 - Mono16
            # 2 - Mono10Packed
            # 3 - Mono12Packed
            # 4 - Mono10p
            # 5 - Mono12p
            cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono10p)
            pixel_format = cam.PixelFormat.GetCurrentEntry().GetSymbolic()
            
            cam.BeginAcquisition()

            processor = PySpin.ImageProcessor()

            processor.SetColorProcessing(PySpin.HQ_LINEAR)

            if acquisition_mode == 0:
                while True:
                    image_result = cam.GetNextImage(1000)                 
                    
                    if image_result.IsIncomplete():
                        print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                    else:
                        image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)

                        opencvImage = image_converted.GetNDArray()
                        cv2.imshow('Continuous', opencvImage)

                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                    image_result.Release()

                cam.EndAcquisition()
                
            elif acquisition_mode == 1:
                image_result = cam.GetNextImage(1000)

                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:
                    image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
                    #image_converted.Save(filename)
                    # Get size
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()
                              
                    opencvImage = image_converted.GetNDArray()
                    cv2.imshow('Single Frame', opencvImage)
                    cv2.waitKey(0)

                image_result.Release()
            
            elif acquisition_mode == 2:
                n_images = int(input("Ingrese la cantidad de imagenes a capturar: "))
                for i in range(n_images):
                    image_result = cam.GetNextImage(1000)

                    if image_result.IsIncomplete():
                        print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                    else:

                        image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
                        opencvImage = image_converted.GetNDArray()
                        image_converted.Save('Multi Frame %d.png' % i)
                        image_result.Release()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def print_device_info(nodemap):
    try:
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            result = True
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))
        else:
            print('Device control information not available.')
            result = False

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def run_single_camera(cam):
    try:
        result = True

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        result &= acquire_images(cam, nodemap, nodemap_tldevice)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def main():    
    try:
        test_file = open('test.txt', 'w+')
    except IOError:
        print('Unable to write to current directory. Please check permissions.')
        input('Press Enter to exit...')
        return False

    test_file.close()
    os.remove(test_file.name)

    result = True

    system = PySpin.System.GetInstance()

    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()
    if num_cameras == 0:
        cam_list.Clear()
        system.ReleaseInstance()

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    cam = cam_list[0]

    result &= run_single_camera(cam)
    del cam

    cam_list.Clear()

    system.ReleaseInstance()
    cv2.destroyAllWindows()

    input('Done! Press Enter to exit...')
    return result

if __name__ == '__main__':
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
