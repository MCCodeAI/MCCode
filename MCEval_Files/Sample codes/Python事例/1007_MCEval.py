#The following code will rewind the API buffer after executing, and then execute the buffer again.Axis 0 and Axis 1 move to a relative position of 50 at a speed of 100. After executing, no functions are added to the buffer, and the same functions are executed again using the Rewind function.
    # Axes = [0，1]

    #The Wait function will suspend the execution of the API buffer until the axis completes the current motion command, and then a new motion command will be used to override the current motion.

    # Record and execute an API buffer with :Axis 0 and Axis 1 move to a relative position of 50 at a speed of 100. After executing, no functions are added to the buffer, and the same functions are executed again using the Rewind function.
    Wmx3Lib_buf = ApiBuffer(Wmx3Lib)
    bufStatus=ApiBufferStatus()

    #  Clear the buffer of the specified channel.
    Wmx3Lib_buf.Clear(0)
    # Create a buffer for the specified channel.
    Wmx3Lib_buf.CreateApiBuffer(0, 1024 * 1024 * 3)
    # Start recording for the specified channel.
    Wmx3Lib_buf.StartRecordBufferChannel(0)

    cond =ApiBufferCondition()

    # Add a position command to the API buffer.
    posCommand = Motion_PosCommand()
    posCommand.profile.type = ProfileType.Trapezoidal
    posCommand.axis = 0
    posCommand.target = 50
    posCommand.profile.velocity = 100
    posCommand.profile.acc = 1000
    posCommand.profile.dec = 1000

    # Execute command to move to a specified relative position.
    ret=Wmx3Lib_cm.motion.StartMov(posCommand)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    #Add a position command to the API buffer
    posCommand.axis=1
    # Execute command to move to a specified relative position.
    ret=Wmx3Lib_cm.motion.StartMov(posCommand)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    #Pause execution until both axes have finished motion
    Wmx3Lib_buf.Wait(0)
    Wmx3Lib_buf.Wait(1)

    # End Recording.
    Wmx3Lib_buf.EndRecordBufferChannel()
    # Drive the motion accumulated in the buffer so far.
    Wmx3Lib_buf.Execute(0)

    # Check the status periodically to see if execution has finished
    counter = 50
    while True:
        ret,bufStatus=Wmx3Lib_buf.GetStatus(0)
        sleep(0.01)
        counter=counter-1
        if(bufStatus.remainingBlockCount<=0&counter<=0):
            break;

    #Rewind the buffer, and then execute it again
    Wmx3Lib_buf.Rewind(0)

    #Wait for the axis to complete motion
    Wmx3Lib_cm.motion.Wait(0)
    Wmx3Lib_cm.motion.Wait(1)

    # Destroy API buffer resources.
    Wmx3Lib_buf.Halt(0)
    Wmx3Lib_buf.FreeApiBuffer(0)

