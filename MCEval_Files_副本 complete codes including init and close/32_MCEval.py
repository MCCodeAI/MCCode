# Write python code to Execute a PVT interpolation command of Axis 0 and Axis 1 of 4 points as a format of (Position0, Velocity0, Time0, Position1, Velocity1, Time1): (0,0,0,0,0,0),(50,1000,100,100,2000,100),(100,2000,200,250,1000,200),(200,0,300,300,0,300)

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
    for axis in [0, 1]:
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


    # Execute a PVT interpolation command of Axis 0 and Axis 1 of 4 points as a format of (Position0, Velocity0, Time0, Position1, Velocity1, Time1): (0,0,0,0,0,0),(50,1000,100,100,2000,100),(100,2000,200,250,1000,200),(200,0,300,300,0,300)
    pvti = Motion_PVTIntplCommand()

    pvtparameter0 = Motion_PVTPoint()
    pvtparameter1 = Motion_PVTPoint()

    pvti.axisCount = 2
    pvti.SetAxis(0, 0)
    pvti.SetAxis(1, 1)
    pvti.SetPointCount(0, 4)
    pvti.SetPointCount(1, 4)

    # Define point data
    pvtparameter0.pos = 0
    pvtparameter0.velocity = 0
    pvtparameter0.timeMilliseconds = 0
    pvtparameter1.pos = 0
    pvtparameter1.velocity = 0
    pvtparameter1.timeMilliseconds = 0
    pvti.SetPoints(0, 0, pvtparameter0)
    pvti.SetPoints(1, 0, pvtparameter1)

    pvtparameter0.pos = 50
    pvtparameter0.velocity = 1000
    pvtparameter0.timeMilliseconds = 100
    pvtparameter1.pos = 100
    pvtparameter1.velocity = 2000
    pvtparameter1.timeMilliseconds = 100
    pvti.SetPoints(0, 1, pvtparameter0)
    pvti.SetPoints(1, 1, pvtparameter1)

    pvtparameter0.pos = 100
    pvtparameter0.velocity = 2000
    pvtparameter0.timeMilliseconds = 200
    pvtparameter1.pos = 250
    pvtparameter1.velocity = 1000
    pvtparameter1.timeMilliseconds = 200
    pvti.SetPoints(0, 2, pvtparameter0)
    pvti.SetPoints(1, 2, pvtparameter1)

    pvtparameter0.pos = 200
    pvtparameter0.velocity = 0
    pvtparameter0.timeMilliseconds = 300
    pvtparameter1.pos = 300
    pvtparameter1.velocity = 0
    pvtparameter1.timeMilliseconds = 300
    pvti.SetPoints(0, 3, pvtparameter0)
    pvti.SetPoints(1, 3, pvtparameter1)


    ret = Wmx3Lib_cm.motion.StartPVT_Intpl(pvti)
    if ret != 0:
        print('StartPVT_Intpl error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    
    # Wait for the motion to complete. Start a blocking wait command, returning only when Axis 0 and Axis 1 become idle.
    axisSel = AxisSelection()
    axisSel.axisCount = 2
    axisSel.SetAxis(0, 0)
    axisSel.SetAxis(1, 1)
    ret = Wmx3Lib_cm.motion.Wait_AxisSel(axisSel)
    if ret != 0:
        print('Wait_AxisSel error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return
    


    # Set servo off for Axes
    for axis in [0, 1]:
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