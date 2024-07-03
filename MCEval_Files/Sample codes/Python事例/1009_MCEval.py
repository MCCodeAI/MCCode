#Several functions in the API buffer provide simple flow control for the API buffer, so that a part of the API buffer can be executed only if a particular condition is satisfied.When Output 0.0 = 1 and 0.2 = 1，trigger Axis 0 to move to a relative position of 100 at a speed of 100.When Output 0.0 = 1 and 0.2 = 0，trigger Axis 0 to move to a relative position of -100 at a speed of 100.When Output 0.1 = 1 and 0.2 = 1，trigger Axis 1 to move to a relative position of 100 at a speed of 100.When Output 0.1 = 1 and 0.2 = 2，trigger Axis 0 to move to a relative position of -100 at a speed of 100.When Output 0.0 = 0,0.1=0 and 0.2 = 1，trigger Axis 2 to move to a relative position of 100 at a speed of 100.When Output 0.0 = 0,0.1=0 and 0.2 = 0，trigger Axis 2 to move to a relative position of -100 at a speed of 100.
    # Axes = [0，1,2]

    #Several functions in the API buffer provide simple flow control for the API buffer, so that a part of the API buffer can be executed only if a particular condition is satisfied.
    # Record and execute an API buffer with :
    #The motion will be in the positive direction if bit 0.2 is on and in the negative direction if bit 0.2 is off.
    #If bit 0.0 is on, the axis 0 will execute motion.
    #Otherwise, if bit 0.1 is on, the axis 0 will execute motion.
    #Otherwise, the axis 2 will execute motion.
    Wmx3Lib_buf = ApiBuffer(Wmx3Lib)
    cond=ApiBufferCondition()

    #  Clear the buffer of the specified channel.
    Wmx3Lib_buf.Clear(0)
    # Create a buffer for the specified channel.
    Wmx3Lib_buf.CreateApiBuffer(0, 1024 * 1024 * 3)
    # Start recording for the specified channel.
    Wmx3Lib_buf.StartRecordBufferChannel(0)

    cond =ApiBufferCondition()
    opt = ApiBufferOptions()

    # Add a position command to the API buffer.
    posCommand = Motion_PosCommand()
    posCommand.profile.type = ProfileType.Trapezoidal
    posCommand.target = 100
    posCommand.profile.velocity = 100
    posCommand.profile.acc = 1000
    posCommand.profile.dec = 1000

    #Set the IF branch
    cond.bufferConditionType=ApiBufferConditionType.IOOutput
    cond.arg_ioOutput.byteAddress =0
    cond.arg_ioOutput.bitAddress =0
    Wmx3Lib_buf.FlowIf(cond)

    #Set the nested IF branch
    cond.arg_ioOutput.byteAddress=0
    cond.arg_ioOutput.bitAddress=2
    Wmx3Lib_buf.FlowIf(cond)

    #Add position command,Output 0.0=1;0.2=1执行
    posCommand.axis=0
    posCommand.target=100

    # Execute command to move to a specified relative position.
    ret=Wmx3Lib_cm.motion.StartMov(posCommand)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    #Set the nested ELSE branch
    Wmx3Lib_buf.FlowElse()

    #Add position command,Output 0.0=1;0.2=0执行
    posCommand.axis=0
    posCommand.target=-100

    # Execute command to move to a specified relative position.
    ret=Wmx3Lib_cm.motion.StartMov(posCommand)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    #Set the nested END IF
    Wmx3Lib_buf.FlowEndIf()

    #Set the ELSE IF branch
    cond.arg_ioOutput.byteAddress=0
    cond.arg_ioOutput.bitAddress=1
    Wmx3Lib_buf.FlowElseIf(cond)

    #Set the nested IF branch
    cond.arg_ioOutput.byteAddress=0
    cond.arg_ioOutput.bitAddress=2
    Wmx3Lib_buf.FlowIf(cond)

    #Add position command,Output 0.1=1;0.2=1执行
    posCommand.axis=1
    posCommand.target=100

    # Execute command to move to a specified relative position.
    ret=Wmx3Lib_cm.motion.StartMov(posCommand)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    #Set the nested ELSE branch
    Wmx3Lib_buf.FlowElse()

    #Add position command,Output 0.1=1;0.2=0执行
    posCommand.axis=1
    posCommand.target=-100

    # Execute command to move to a specified relative position.
    ret=Wmx3Lib_cm.motion.StartMov(posCommand)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    #Set the nested END IF
    Wmx3Lib_buf.FlowEndIf()

    #Set the ELSE branch
    Wmx3Lib_buf.FlowElse()

    #Set the nested IF branch
    cond.arg_ioOutput.byteAddress=0
    cond.arg_ioOutput.bitAddress=2
    Wmx3Lib_buf.FlowIf(cond)

    #Add position command,Output 0.0=0;0.1=0;0.2=1执行
    posCommand.axis=2
    posCommand.target=100

    # Execute command to move to a specified relative position.
    ret=Wmx3Lib_cm.motion.StartMov(posCommand)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

   #Set the nested ELSE branch
    Wmx3Lib_buf.FlowElse()

    #Add position command,,Output 0.0=0;0.1=0;0.2=0执行
    posCommand.axis=2
    posCommand.target=-100

    # Execute command to move to a specified relative position.
    ret=Wmx3Lib_cm.motion.StartMov(posCommand)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    #Set the nested END IF
    Wmx3Lib_buf.FlowEndIf()

    #Set the END IF
    Wmx3Lib_buf.FlowEndIf()

    # End Recording.
    Wmx3Lib_buf.EndRecordBufferChannel()

    Wmx3Lib_Io = Io(Wmx3Lib)
    # Set Output 0.0 = 1; 0.2 = 1 to trigger Axis 0 to move to a relative position of 100 at a speed of 100.
    Wmx3Lib_Io.SetOutBit(0,0,1)
    Wmx3Lib_Io.SetOutBit(0,2,1)
    Wmx3Lib_buf.Execute(0)

    #Wait for the axis 0 motion to complete.
    Wmx3Lib_cm.motion.Wait(0)

    # Set Output 0.0 = 1; 0.2 = 0 to trigger Axis 0 to move to a relative position of -100 at a speed of 100.
    Wmx3Lib_Io.SetOutBit(0,0,1)
    Wmx3Lib_Io.SetOutBit(0,2,0)
    Wmx3Lib_buf.Rewind(0)

    #Wait for the axis 0 motion to complete.
    Wmx3Lib_cm.motion.Wait(0)
    Wmx3Lib_Io.SetOutBit(0, 0, 0)

    # Set Output 0.0 = 1; 0.2 = 1 to trigger Axis 1 to move to a relative position of 100 at a speed of 100.
    Wmx3Lib_Io.SetOutBit(0,1,1)
    Wmx3Lib_Io.SetOutBit(0,2,1)
    Wmx3Lib_buf.Rewind(0)

    #Wait for the axis 1 motion to complete.
    Wmx3Lib_cm.motion.Wait(1)

    # Set Output 0.0 = 1; 0.2 = 0 to trigger Axis 1 to move to a relative position of -100 at a speed of 100.
    Wmx3Lib_Io.SetOutBit(0,1,1)
    Wmx3Lib_Io.SetOutBit(0,2,0)
    Wmx3Lib_buf.Rewind(0)

    #Wait for the axis 1 motion to complete.
    Wmx3Lib_cm.motion.Wait(1)
    Wmx3Lib_Io.SetOutBit(0, 1, 0)

    # Set Output 0.0 = 0; 0.1=0;0.2 = 1 to trigger Axis 2 to move to a relative position of 100 at a speed of 100.
    Wmx3Lib_Io.SetOutBit(0, 1, 0)
    Wmx3Lib_Io.SetOutBit(0,1,0)
    Wmx3Lib_Io.SetOutBit(0,2,1)
    Wmx3Lib_buf.Rewind(0)

    #Wait for the axis 2 motion to complete.
    Wmx3Lib_cm.motion.Wait(2)

    # Set Output 0.0 = 0; 0.1=0;0.2 = 0 to trigger Axis 2 to move to a relative position of -100 at a speed of 100.
    Wmx3Lib_Io.SetOutBit(0, 1, 0)
    Wmx3Lib_Io.SetOutBit(0,1,0)
    Wmx3Lib_Io.SetOutBit(0,2,0)
    Wmx3Lib_buf.Rewind(0)

    #Wait for the axis 2 motion to complete.
    Wmx3Lib_cm.motion.Wait(2)

    # Destroy API buffer resources.
    Wmx3Lib_buf.Halt(0)
    Wmx3Lib_buf.FreeApiBuffer(0)

