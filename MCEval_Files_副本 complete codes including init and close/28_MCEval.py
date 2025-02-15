# Write python code to Execute a sequence of motion commands using trigger motion functions and Wait functions.Move Axis 0 as 100 distance with 1000 velocity, and trigger it to move as -100 distance when the remaining time is 0, and then move as 200 distance, and -200 distance after waiting it to be overridable.

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


    # Execute a sequence of motion commands using trigger motion functions and Wait functions.Move Axis 0 as 100 distance with 1000 velocity, and trigger it to move as -100 distance when the remaining time is 0, and then move as 200 distance, and -200 distance after waiting it to be overridable.
    pos = Motion_PosCommand()
    tpos = Motion_TriggerPosCommand()
    wait = Motion_WaitCondition()

    # Set position command parameters
    pos.axis = 0
    pos.profile.type = ProfileType.Trapezoidal;
    pos.profile.velocity = 1000
    pos.profile.acc = 10000
    pos.profile.dec = 10000

    # Set triggered position command parameters
    tpos.axis = 0
    tpos.profile.type = ProfileType.Trapezoidal
    tpos.profile.velocity = 1000
    tpos.profile.acc = 10000
    tpos.profile.dec = 10000
    tpos.trigger.triggerAxis = 0
    tpos.trigger.triggerType = TriggerType.RemainingTime
    tpos.trigger.triggerValue = 0

    # Set wait condition parameters, waiting Axis 0 to be overridable.
    wait.waitConditionType = Motion_WaitConditionType.MotionStartedOverrideReady
    wait.axisCount = 1
    wait.SetAxis(0, 0)

    # Execute motion to move axis forward 100
    pos.target = 100

    ret = Wmx3Lib_cm.motion.StartMov(pos)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    # Execute trigger motion to move axis backward 100 at the end of the previous motion
    tpos.target = -100

    ret = Wmx3Lib_cm.motion.StartMov_Trigger(tpos)
    if ret != 0:
        print('StartMov_Trigger error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    # Wait until trigger motion executes
    ret = Wmx3Lib_cm.motion.Wait_WaitCondition(wait)
    if ret != 0:
        print('Wait_WaitCondition error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    # Execute trigger motion to move axis forward 200 at the end of the previous motion
    tpos.target = 200

    ret = Wmx3Lib_cm.motion.StartMov_Trigger(tpos)
    if ret != 0:
        print('StartMov_Trigger error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    # Wait until trigger motion executes
    ret = Wmx3Lib_cm.motion.Wait_WaitCondition(wait)
    if ret != 0:
        print('Wait_WaitCondition error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    # Execute trigger motion to move axis backward 20000 at the end of the previous motion
    tpos.target = -200
    ret = Wmx3Lib_cm.motion.StartMov_Trigger(tpos)
    if ret != 0:
        print('StartMov_Trigger error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    # Wait until motion is finished
    ret = Wmx3Lib_cm.motion.Wait(0)
    if ret != 0:
        print('Wait error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return
    


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