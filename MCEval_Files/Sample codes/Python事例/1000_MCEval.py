#Create a Normal E-CAM table corresponding to the master axis positions (-100, -50, 0, 50, 100) and the slave axis positions (100, 150, 100, 50, 100).The axis starts moving to the position of -200 at a speed of 1000, then establishes the E-CAM table, and subsequently moves from the position of -200 to 200 at a speed of 100.
    # Axes = [0，1]

    #Start an absolute position command of Axis 0 to position -200  with 1000 velocity.
    # Create a command value.
    posCommand = Motion_PosCommand()
    posCommand.profile.type = ProfileType.Trapezoidal
    posCommand.axis = 0
    posCommand.target = -200
    posCommand.profile.velocity = 1000
    posCommand.profile.acc = 1000
    posCommand.profile.dec = 1000

    # Execute command to move to a specified absolute position. e.g. 'Move to Position -300..'
    ret = Wmx3Lib_cm.motion.StartPos(posCommand)
    if ret != 0:
        print('StartPos error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
    Wmx3Lib_cm.motion.Wait(0)

    # The following example illustrates a typical Normal type E-CAM table:
    #   Master Axis Position      Slave Axis Position
    #   -100                      100
    #   -50                       150
    #   0                         100
    #   50                        50
    #   100                       100

    ECAMdata =AdvSync_ECAMData()
    ecopt =AdvSync_ECAMOptions()

    ecopt.type=AdvSync_ECAMType.Normal
    ecopt.source.type=AdvSync_ECAMSourceType.MasterCommandPos
    #PyNone: When the E-CAM is activated, the slave axis synchronizes with the master axis immediately.
    ecopt.clutch.type=AdvSync_ECAMClutchType.PyNone
    #In the AdvSync.ECAMClutchType.SimpleCatchUp mode, it is used to track the speed of the master-slave curve in the E-CAM table.
    ecopt.clutch.simpleCatchUpVelocity=1000
    #In the AdvSync.ECAMClutchType.SimpleCatchUp mode, it is used to catch up with the acceleration and deceleration of the master-slave curve in the E-CAM table.
    ecopt.clutch.simpleCatchUpAcc=10000

    #Set the E-CAM table.
    ECAMdata.masterAxis=0
    ECAMdata.slaveAxis=1
    ECAMdata.numPoints=5
    ECAMdata.options=ecopt

    ECAMdata.SetMasterPos(0, -100)
    ECAMdata.SetMasterPos(1, -50)
    ECAMdata.SetMasterPos(2, 0)
    ECAMdata.SetMasterPos(3, 50)
    ECAMdata.SetMasterPos(4, 100)

    ECAMdata.SetSlavePos(0,100)
    ECAMdata.SetSlavePos(1, 150)
    ECAMdata.SetSlavePos(2, 100)
    ECAMdata.SetSlavePos(3, 50)
    ECAMdata.SetSlavePos(4, 100)

    # Start ECAM
    ret=Wmx3Lib_adv.advSync.StartECAM(0,ECAMdata)
    if ret!=0:
        print('StartECAM error code is ' + str(ret) + ': ' + Wmx3Lib.ErrorToString(ret))
        return

    # Create a command value with a target value of 200.
    posCommand = Motion_PosCommand()
    posCommand.profile.type = ProfileType.Trapezoidal
    posCommand.axis = 0
    posCommand.target = 200
    posCommand.profile.velocity = 100
    posCommand.profile.acc = 1000
    posCommand.profile.dec = 1000

    # Execute command to move from current position to specified absolute position.
    ret = Wmx3Lib_cm.motion.StartPos(posCommand)
    if ret!=0:
        print('StartPos error code is ' + str(ret) + ': ' + Wmx3Lib_cm.ErrorToString(ret))
        return

    # Wait until the axis moves to the target position and stops.
    Wmx3Lib_cm.motion.Wait(0)
