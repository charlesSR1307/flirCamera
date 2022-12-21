# coding=utf-8

import os
import PySpin
import sys
import cv2

def acquire_images(cam, nodemap, nodemap_tldevice):
    try:
        result = True

        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        cam.BeginAcquisition()

        processor = PySpin.ImageProcessor()

        processor.SetColorProcessing(PySpin.HQ_LINEAR)

        while True:
            try:

                image_result = cam.GetNextImage(1000)

                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:

                    width = image_result.GetWidth()
                    height = image_result.GetHeight()

                    image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)

                    opencvImage = image_converted.GetNDArray()
                    cv2.imshow('Live Feed', opencvImage)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    image_result.Release()

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False

        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def print_device_info(nodemap):
    try:
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            result = True
            #features = node_device_information.GetFeatures()
            #for feature in features:
                #node_feature = PySpin.CValuePtr(feature)
                #print('%s: %s' % (node_feature.GetName(),
                                  #node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))
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
