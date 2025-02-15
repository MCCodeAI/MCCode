# Write python code to Set an event to trigger a relative position command of Axis 0 with 100 distance and 1000 velocity, when Output 1.0 = 1. Event id is 10.

#WMX3 python library
from WMX3ApiPython import *
from time import *

INFINITE = int(0xFFFFFFFF)

def main():
    Wmx3Lib = WMX3Api()
    CmStatus = CoreMotionStatus()
    Wmx3Lib_cm = CoreMotion(Wmx3Lib)
    print('Program begin.')
    sleep(0.1)

    # Create devices. 
    ret = Wmx3Lib.CreateDevice('C:\\Program Files\\SoftServo\\WMX3', DeviceType.DeviceTypeNormal, INFINITE)
    if ret!=0:
        print('CreateDevice error code is ' + str(ret) + ': ' + Wmx3Lib.ErrorToString(ret))
        return

    # Set Device Name.
    Wmx3Lib.SetDeviceName('WMX3initTest')

    # Start Communication.
    ret = Wmx3Lib.StartCommunication(INFINITE)
    if ret!=0:
        print('StartCommunication error code is ' + str(ret) + ': ' + Wmx3Lib.ErrorToString(ret))
        return

    # Import and set all the preset motion parameters.
    ret=Wmx3Lib_cm.config.ImportAndSetAll("C:\\Program Files\\SoftServo\\WMX3\\wmx_parameters.xml")
    if ret != 0:
        print('ImportAndSetAll Parameters error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
    sleep(0.5)
 
    # Clear alarms, set servos on, and perform homing for Axes
    for axis in [0]:
        # Clear the amplifier alarm
        timeoutCounter = 0
        while True:
            # GetStatus -> First return value : Error code, Second return value: CoreMotionStatus
            ret, CmStatus = Wmx3Lib_cm.GetStatus()
            if not CmStatus.GetAxesStatus(axis).ampAlarm:
                break
            ret = Wmx3Lib_cm.axisControl.ClearAmpAlarm(axis)
            sleep(0.5)
            timeoutCounter += 1
            if timeoutCounter > 5:
                break
        if timeoutCounter > 5:
            print(f'Clear axis {axis} alarm fails!')
            return

        # Set servo on for Axis
        ret = Wmx3Lib_cm.axisControl.SetServoOn(axis, 1)
        timeoutCounter = 0
        while True:
            # GetStatus -> First return value : Error code, Second return value: CoreMotionStatus
            ret, CmStatus = Wmx3Lib_cm.GetStatus()
            if (CmStatus.GetAxesStatus(axis).servoOn):
                break
            sleep(0.4)
            timeoutCounter += 1
            if (timeoutCounter > 5):
                break
        if (timeoutCounter > 5):
            print('Set servo on for axis {axis} fails!')
            return

        # Sleep is a must between SetServoOn and Homing
        sleep(0.1)

        # Homing
        homeParam = Config_HomeParam()
        ret, homeParam = Wmx3Lib_cm.config.GetHomeParam(axis)
        homeParam.homeType = Config_HomeType.CurrentPos

        # SetHomeParam -> First return value: Error code, Second return value: param error
        ret, homeParamError = Wmx3Lib_cm.config.SetHomeParam(axis, homeParam)

        ret = Wmx3Lib_cm.home.StartHome(axis)
        if ret != 0:
            print(f'StartHome error code for axis {axis} is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
            return
        Wmx3Lib_cm.motion.Wait(axis)


    # Set an event to trigger a relative position command of Axis 0 with 100 distance and 1000 velocity, when Output 1.0 = 1. Event id is 10.
    Wmx3Lib_EventCtl = EventControl(Wmx3Lib)
    eventIN_IO = IoEventInput()
    eventOut_Motion = CoreMotionEventOutput()
    # Event ID
    posEventID = 10
    # RemoveEvent
    Wmx3Lib_EventCtl.RemoveEvent(posEventID)

    eventIN_IO.type = IoEventInputType.IOBit
    eventIN_IO.ioBit.ioSourceType = IOSourceType.Output
    eventIN_IO.ioBit.bitAddress = 0
    eventIN_IO.ioBit.byteAddress = 1

    eventOut_Motion.type = CoreMotionEventOutputType.StartSingleMov
    eventOut_Motion.startSingleMov.axis = 0
    eventOut_Motion.startSingleMov.type = ProfileType.Trapezoidal
    eventOut_Motion.startSingleMov.target = 100
    eventOut_Motion.startSingleMov.velocity = 1000
    eventOut_Motion.startSingleMov.acc = 10000
    eventOut_Motion.startSingleMov.dec = 10000

    # Set input events, output events, and event addresses.
    ret,Event_ID = Wmx3Lib_EventCtl.SetEvent_ID(eventIN_IO, eventOut_Motion, posEventID)
    if ret != 0:
        print('SetEvent_ID error code is ' + str(ret))
        return
    # EnableEvent
    Wmx3Lib_EventCtl.EnableEvent(posEventID, 1)

    sleep(0.01)
    # Set Output 1.0 = 1 to trigger the motion
    Wmx3Lib_Io = Io(Wmx3Lib)
    ret = Wmx3Lib_Io.SetOutBit(0x01, 0x00, 0x01)
    if ret!=0:
        print('SetOutBit error code is ' + str(ret) + ': ' + Wmx3Lib_Io.ErrorToString(ret))
        return

    # Wait until the axis moves to the target position and stops.
    Wmx3Lib_cm.motion.Wait(0)



    # Set servo off for Axes
    for axis in [0]:
        ret = Wmx3Lib_cm.axisControl.SetServoOn(axis, 0)
        if ret != 0:
            print(f'SetServoOn to off error code for axis {axis} is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
            return

    # Stop Communication.
    ret = Wmx3Lib.StopCommunication(INFINITE)
    if ret!=0:
        print('StopCommunication error code is ' + str(ret) + ': ' + Wmx3Lib.ErrorToString(ret))
        return

    # Close Device.
    ret = Wmx3Lib.CloseDevice()
    if ret!=0:
        print('CloseDevice error code is ' + str(ret) + ': ' + Wmx3Lib.ErrorToString(ret))
        return

    print('Program End.')

if __name__ == '__main__':
    main()