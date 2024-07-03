#Another way of rewinding the API buffer is to enable the autoRewind option when calling the Execute function. If this option is enabled, after executing all API functions in the buffer, the API buffer will rewind back to the first API that is in the buffer as if the Rewind function is called. The API buffer will be executed repeatedly until stopped.
#Axis 0 moves to a relative position of 100 at a speed of 100 units per second, waits for completion, and then moves to a relative position of -100 at the same speed. With the autoRewind parameter enabled, the same sequence of functions will be executed repeatedly. After a delay of 5 seconds, a stop function is called to forcibly halt the execution.
    # Axes = [0]

    #Another way of rewinding the API buffer is to enable the autoRewind option when calling the Execute function. If this option is enabled, after executing all API functions in the buffer, the API buffer will rewind back to the first API that is in the buffer as if the Rewind function is called. The API buffer will be executed repeatedly until stopped.
    # Record and execute an API buffer with :Axis 0 and Axis 1 move to a relative position of 50 at a speed of 100. After executing, no functions are added to the buffer, and the same functions are executed again using the Rewind function.
    Wmx3Lib_buf = ApiBuffer(Wmx3Lib)
    opt=ApiBufferOptions()

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
    posCommand.target = 100
    posCommand.profile.velocity = 100
    posCommand.profile.acc = 1000
    posCommand.profile.dec = 1000

    # Execute command to move to a specified relative position.
    ret=Wmx3Lib_cm.motion.StartMov(posCommand)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    #Pause execution until both axes have finished motion
    Wmx3Lib_buf.Wait(0)

    #Add a position command to the API buffer
    posCommand.target =-100
    # Execute command to move to a specified relative position.
    ret=Wmx3Lib_cm.motion.StartMov(posCommand)
    if ret != 0:
        print('StartMov error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    #Pause execution until both axes have finished motion
    Wmx3Lib_buf.Wait(0)

    # End Recording.
    Wmx3Lib_buf.EndRecordBufferChannel()

    #Set the API buffer execution options
    opt.autoRewind=True
    Wmx3Lib_buf.SetOptions(0,opt)

    # Drive the motion accumulated in the buffer so far.
    Wmx3Lib_buf.Execute(0)

    #After a delay of 10 seconds, a stop function is called to forcibly halt the execution.
    sleep(5)

    # Destroy API buffer resources.
    Wmx3Lib_buf.Halt(0)
    Wmx3Lib_buf.FreeApiBuffer(0)

