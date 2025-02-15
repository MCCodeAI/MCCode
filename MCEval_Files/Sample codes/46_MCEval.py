# Write python code to Executes a path interpolation of Axis 0 and 1 with a rotation Axis 2 without stopping after executing each segment, and the velocity is 100. Sequence consisting of four linear interpolations and enable rotating the X and Y axes around the center of rotation. The center of rotation is (50,50). The positions of four linear interpolations are: (100,0),(100,100),(0,100),(0,0). Auto smoothing radius after 1st, 2nd and 3rd segment are 30, 20, 10.
    # Axes = [0, 1, 2]

    Wmx3Lib_adv = AdvancedMotion(Wmx3Lib)

    path = AdvMotion_PathIntplWithRotationCommand()
    ret = Wmx3Lib_adv.advMotion.FreePathIntplWithRotationBuffer(0)
    # Create the path interpolation with rotation buffer
    ret = Wmx3Lib_adv.advMotion.CreatePathIntplWithRotationBuffer(0, 1000)
    if ret != 0:
        print('CreatePathIntplWithRotationBuffer error code is ' + str(ret) + ': ' + Wmx3Lib_adv.ErrorToString(ret))
        return

    # Configure the path interpolation with rotation channel
    conf = AdvMotion_PathIntplWithRotationConfiguration()

    conf.SetAxis(0, 0)  # X axis
    conf.SetAxis(1, 1)  # Y axis
    conf.rotationalAxis = 2  # Rotational axis
    conf.SetCenterOfRotation(0, 50)  # X axis center of rotation position
    conf.SetCenterOfRotation(1, 50)  # Y axis center of rotation position

    # Rotational axis angle correction motion profile parameters
    conf.angleCorrectionProfile.type = ProfileType.Trapezoidal
    conf.angleCorrectionProfile.velocity = 200
    conf.angleCorrectionProfile.acc = 1800
    conf.angleCorrectionProfile.dec = 1800

    # Enable auto smoothing
    conf.enableAutoSmooth = 1

    # Do not stop the motion along the path at very small angles between two segments
    conf.angleCorrectionMinimumAngle = 0.01

    # Enable constant profile
    conf.enableConstProfile = 1

    ret = Wmx3Lib_adv.advMotion.SetPathIntplWithRotationConfiguration(0, conf)
    if ret != 0:
        print('SetPathIntplWithRotationConfiguration error code is ' + str(ret) + ': ' + Wmx3Lib_adv.ErrorToString(ret))
        return

    #Set Axis 2 to single-turn mode, single-turn encoder count. Single-turn mode is necessary for rotation axis in path interpolatioin with rotation function.
    ret=Wmx3Lib_cm.config.SetSingleTurn(2,True,360000)
    if ret != 0:
        print('SetSingleTurn error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    # Add the path interpolation with rotation commands
    path.numPoints = 4

    # Only specify the profile for the first point as constant profile is enabled
    point = AdvMotion_PathIntplWithRotationCommandPoint()
    point.type = AdvMotion_PathIntplSegmentType.Linear
    profile = Profile()
    point.profile.type = ProfileType.Trapezoidal
    point.profile.velocity = 100
    point.profile.acc = 2000
    point.profile.dec = 2000
    point.SetTarget(0, 100)
    point.SetTarget(1, 0)
    point.autoSmoothRadius = 30  # Auto smoothing radius after first segment
    path.SetPoint(0, point)

    point = AdvMotion_PathIntplWithRotationCommandPoint()
    point.type = AdvMotion_PathIntplSegmentType.Linear
    point.SetTarget(0, 100)
    point.SetTarget(1, 100)
    point.autoSmoothRadius = 20  # Auto smoothing radius after second segment
    path.SetPoint(1, point)

    point = AdvMotion_PathIntplWithRotationCommandPoint()
    point.type = AdvMotion_PathIntplSegmentType.Linear
    point.SetTarget(0, 0)
    point.SetTarget(1, 100)
    point.autoSmoothRadius = 10  # Auto smoothing radius after third segment
    path.SetPoint(2, point)

    point = AdvMotion_PathIntplWithRotationCommandPoint()
    point.type = AdvMotion_PathIntplSegmentType.Linear
    point.SetTarget(0, 0)
    point.SetTarget(1, 0)
    path.SetPoint(3, point)

    ret = Wmx3Lib_adv.advMotion.AddPathIntplWithRotationCommand(0, path)
    if ret != 0:
        print('AddPathIntplWithRotationCommand error code is ' + str(ret) + ': ' + Wmx3Lib_adv.ErrorToString(ret))
        return

    # Execute path interpolation with rotation
    ret = Wmx3Lib_adv.advMotion.StartPathIntplWithRotation(0)

    if ret != 0:
        print('StartPathIntplWithRotation error code is ' + str(ret) + ': ' + Wmx3Lib_adv.ErrorToString(ret))
        return
    Wmx3Lib_cm.motion.Wait(0)
    timeoutCounter = 0
    # Wait until the path interpolation with rotation is in Idle state
    pathStatus = AdvMotion_PathIntplWithRotationState()
    ret, pathStatus = Wmx3Lib_adv.advMotion.GetPathIntplWithRotationStatus(0)
    while True:
        if (pathStatus.state == AdvMotion_PathIntplWithRotationState.Idle):
            break
        sleep(0.1)
        timeoutCounter = timeoutCounter + 1
        if (timeoutCounter > 500):
            break
        ret, pathStatus = Wmx3Lib_adv.advMotion.GetPathIntplWithRotationStatus(0)
    if (timeoutCounter > 500):
        print('PathIntplWithRotation Runuing timeout.!')
        return
    # Free the path interpolation with rotation buffer (normally, the buffer should only be freed at the end of the application)
    ret = Wmx3Lib_adv.advMotion.FreePathIntplWithRotationBuffer(0)
    if ret != 0:
        print('FreePathIntplWithRotationBuffer error code is ' + str(ret) + ': ' + Wmx3Lib_adv.ErrorToString(ret))
        return

    #Turn off Axis 2 single-turn mode.
    AxisParam=Config_AxisParam()
    ret,AxisParam =Wmx3Lib_cm.config.GetAxisParam()
    AxisParam.SetSingleTurnMode(2,False)

    ret,AxisParamError=Wmx3Lib_cm.config.SetAxisParam(AxisParam)
    if ret != 0:
        print('Close SingleTurnMode error code is ' + str(ret) + ': ' + Wmx3Lib_adv.ErrorToString(ret))
        return

