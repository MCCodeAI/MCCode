#The following example demonstrates a position synchronous output function using the LessThan comparison type.The position synchronization comparison values are: 100, 200, 300, with the position synchronization output point at 0.0. Axis 0 is to move to the target position of 400, with a speed of 500, and acceleration and deceleration are set to 5000.
    # Axes = [0]

    # Set the comparison axis 0 command position output to 0.0.
    PsoOut.outputType = EventControl_PSOOutputType.IOOutput
    PsoOut.byteAddress = 0
    PsoOut.bitAddress = 0
    PsoOut.invert = 0
    PsoCompSor.sourceType = EventControl_ComparatorSourceType.PosCommand
    PsoCompSor.axis = 0
    # The comparison position values are: 100, 200, 300.
    point = [100,200,300]

    #  Create a command value of axis 0 moves a distance of 400 from the current position at a speed of 500, with an acceleration and deceleration of 5000.
    posCommand = Motion_PosCommand()
    posCommand.profile.type = ProfileType.Trapezoidal
    posCommand.axis = 0
    posCommand.profile.velocity = 500
    posCommand.profile.acc = 5000
    posCommand.profile.dec = 5000
    posCommand.target = 400
    # Set parameters for a position synchronous output channel. A position synchronous output channel is able to output an output signal when certain conditions, such as an axis reaching a certain position, are met.
    ret =Wmx3Lib_EventCtl.SetPSOConfig(0,EventControl_ComparisonType.LessThan,PsoCompSor,PsoOut,0)
    if ret != 0:
        print('SetPSOConfig to off error code is ' + str(ret) + ': ' + Wmx3Lib_EventCtl.ErrorToString(ret))
    # Set multiple data points for a position synchronous output channel.
    ret =Wmx3Lib_EventCtl.SetPSOMultipleData(0,3,point)
    if ret != 0:
        print('SetPSOMultipleData to off error code is ' + str(ret) + ': ' + Wmx3Lib_EventCtl.ErrorToString(ret))
    # Get the channel status
    ret,PsoStu = Wmx3Lib_EventCtl.GetPSOStatus(0)
    PsoCount = Wmx3Lib_EventCtl.GetPSODataCount(0)
    #If the channel is already open, execute StopPSO.
    if PsoStu.enabled == 1:
        Wmx3Lib_EventCtl.StopPSO(0)
        sleep(0.01)
    # StartPSO
    ret = Wmx3Lib_EventCtl.StartPSO(0)
    if ret != 0:
        print('StartPSO to off error code is ' + str(ret) + ': ' + Wmx3Lib_EventCtl.ErrorToString(ret))
    # Execute command to move to a specified absolute position.
    ret =Wmx3Lib_cm.motion.StartPos(posCommand)
    if ret != 0:
        print('StartPos to off error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
    Wmx3Lib_cm.motion.Wait(0)
    # StopPSO
    Wmx3Lib_EventCtl.StopPSO(0)
