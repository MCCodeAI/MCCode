
from WMX3ApiPython import *
from time import sleep

INFINITE = int(0xFFFFFFFF)

def main():
    Wmx3Lib = WMX3Api()
    Wmx3Lib_cm = CoreMotion(Wmx3Lib)
    
    # Create and initialize device
    Wmx3Lib.CreateDevice('C:\\Program Files\\SoftServo\\WMX3', DeviceType.DeviceTypeNormal, INFINITE)
    Wmx3Lib.SetDeviceName('WMX3initTest')
    Wmx3Lib.StartCommunication(INFINITE)
    
    # Initialize and home all axes
    for axis in range(4):
        Wmx3Lib_cm.axisControl.ClearAmpAlarm(axis)
        Wmx3Lib_cm.axisControl.SetServoOn(axis, 1)
        sleep(0.1)
        homeParam = Config_HomeParam()
        ret, homeParam = Wmx3Lib_cm.config.GetHomeParam(axis)
        homeParam.homeType = Config_HomeType.CurrentPos
        Wmx3Lib_cm.config.SetHomeParam(axis, homeParam)
        Wmx3Lib_cm.home.StartHome(axis)
        Wmx3Lib_cm.motion.Wait(axis)
    
    sleep(2)  # Initial sleep
    
    # Move Axis 1
    posCommand = Motion_PosCommand()
    posCommand.profile.type = ProfileType.Trapezoidal
    posCommand.axis = 1
    posCommand.target = -400
    posCommand.profile.velocity = 100
    posCommand.profile.acc = 1000000
    posCommand.profile.dec = 1000000
    Wmx3Lib_cm.motion.StartPos(posCommand)
    
    # Move Axis 2 and Axis 0 simultaneously
    posCommand.axis = 2
    posCommand.target = -300
    Wmx3Lib_cm.motion.StartPos(posCommand)
    
    posCommand.axis = 0
    posCommand.target = -300
    Wmx3Lib_cm.motion.StartPos(posCommand)
    
    Wmx3Lib_cm.motion.Wait(1)
    Wmx3Lib_cm.motion.Wait(2)
    Wmx3Lib_cm.motion.Wait(0)
    
    sleep(2)  # Sleep after movements
    
    # Linear interpolation between Axis 0 and Axis 3
    lin = Motion_LinearIntplCommand()
    lin.axisCount = 2
    lin.SetAxis(0, 0)
    lin.SetAxis(1, 3)
    lin.profile.type = ProfileType.Trapezoidal
    lin.profile.velocity = 1000
    lin.profile.acc = 10000
    lin.profile.dec = 10000
    
    # First interpolation
    lin.SetTarget(0, -250)
    lin.SetTarget(1, 50)
    Wmx3Lib_cm.motion.StartLinearIntplPos(lin)
    Wmx3Lib_cm.motion.Wait(0)
    
    # Second interpolation
    lin.SetTarget(0, -350)
    lin.SetTarget(1, -50)
    Wmx3Lib_cm.motion.StartLinearIntplPos(lin)
    Wmx3Lib_cm.motion.Wait(0)
    
    # Third interpolation
    lin.SetTarget(0, -210)
    lin.SetTarget(1, 60)
    Wmx3Lib_cm.motion.StartLinearIntplPos(lin)
    Wmx3Lib_cm.motion.Wait(0)
    
    sleep(4)  # Final sleep
    
    # Turn off servos and stop communication
    for axis in range(4):
        Wmx3Lib_cm.axisControl.SetServoOn(axis, 0)
    
    Wmx3Lib.StopCommunication(INFINITE)
    Wmx3Lib.CloseDevice()
    
    print('Program End.')

if __name__ == '__main__':
    main()
