# Write python code to Create and execute a cyclic buffer memory space for Axis 4, to pisition 100 within 200 cycles, then move a relative 0 distance within 600 cycles, then to pisition -100 within 200 cycles, then sleep 1.5s, and close the cyclic buffer.
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
 
    # Clear alarms, set servos on, and perform homing for Axis 4
    for axis in [4]:
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


    # Create and execute a cyclic buffer memory space for Axis 4, to pisition 100 within 200 cycles, then move a relative 0 distance within 600 cycles, then to pisition -100 within 200 cycles, then sleep 1.5s, and close the cyclic buffer.
    Wmx3Lib_cyc = CyclicBuffer(Wmx3Lib)

    # Create a new cyclic buffer memory space for Axis 4, with a size of 1,024 cycles.
    ret = Wmx3Lib_cyc.OpenCyclicBuffer(4, 1024)
    if ret != 0:
        print('OpenCyclicBuffer error code is ' + str(ret) + ': ' + Wmx3Lib_cyc.ErrorToString(ret))
        return

    # Start the execution of the cyclic position command buffer for Axis 4.
    ret = Wmx3Lib_cyc.Execute(4)
    if ret != 0:
        print('Execute error code is ' + str(ret) + ': ' + Wmx3Lib_cyc.ErrorToString(ret))
        return

    # Dynamically add points to move from the current position to the absolute position of 100 within 200 cycles.
    cyclicBufferSingleAxisCommand = CyclicBufferSingleAxisCommand()
    cyclicBufferSingleAxisCommand.type = CyclicBufferCommandType.AbsolutePos
    cyclicBufferSingleAxisCommand.intervalCycles = 200
    cyclicBufferSingleAxisCommand.command = 100
    ret = Wmx3Lib_cyc.AddCommand(4, cyclicBufferSingleAxisCommand)
    if ret != 0:
        print('AddCommand error code is ' + str(ret) + ': ' + Wmx3Lib_cyc.ErrorToString(ret))
        return

    # The relative position is 0, which means there was no movement for 600 cycles from the previous position.
    cyclicBufferSingleAxisCommand.type = CyclicBufferCommandType.RelativePos
    cyclicBufferSingleAxisCommand.intervalCycles = 600
    cyclicBufferSingleAxisCommand.command = 0
    ret = Wmx3Lib_cyc.AddCommand(4, cyclicBufferSingleAxisCommand)
    if ret != 0:
        print('AddCommand error code is ' + str(ret) + ': ' + Wmx3Lib_cyc.ErrorToString(ret))
        return

    # Move from the current position to the absolute position of -100 within 200 cycles.
    cyclicBufferSingleAxisCommand.type = CyclicBufferCommandType.AbsolutePos
    cyclicBufferSingleAxisCommand.intervalCycles = 200
    cyclicBufferSingleAxisCommand.command = -100
    ret = Wmx3Lib_cyc.AddCommand(4, cyclicBufferSingleAxisCommand)
    if ret != 0:
        print('AddCommand error code is ' + str(ret) + ': ' + Wmx3Lib_cyc.ErrorToString(ret))
        return

    # Wait for 1.5 seconds until the motion ends.
    sleep(1.5)

    # Close the cyclic buffer memory space.
    ret = Wmx3Lib_cyc.CloseCyclicBuffer(4)
    if ret != 0:
        print('CloseCyclicBuffer error code is ' + str(ret) + ': ' + Wmx3Lib_cyc.ErrorToString(ret))
        return



    # Set servo off for Axis 4
    for axis in [4]:
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