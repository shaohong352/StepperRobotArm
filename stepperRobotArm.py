#!/usr/bin/python3

import time
from serial import Serial
from servoGripper import ServoGripper

# - - - - - - - - - - - - - - - - 
# - - -  StepperRobotArm  - - - -
# - - - - - - - - - - - - - - - -
class StepperRobotArm:
    def __init__(self, led, pi, servoGripperPin):
        self.pi = pi
        self.servoGripperPin = servoGripperPin
        self.servoGripper = ServoGripper(self.pi, self.servoGripperPin)
        self.blinkLED = led
        self.port = Serial("/dev/ttyAMA0", baudrate=115200, timeout=0.001)
        self.wakeUpGrbl()
        self.useCurrentPosAsOrigin()
        self.currentPosDict = {"X": 0, "Y": 0, "Z": 0}
        self.replayList = []
        self.replayStepList = []
        self.mode = 'idle'
        self.endlessReplay = False
        # available modes are:
        # - idle
        # - follow
        # - replay

    def wakeUpGrbl(self):
        self.port.write(b"\r\n\r\n")
        print("waking up grbl")
        time.sleep(2)
        self.port.flushInput()

    def waitForResponse(self):
        return self.port.readline()

    def sendBlock(self):
        port.write(b"G90 G0 X5.0 Y5.0 Z5.0")
        port.write(b"\n")

    def checkIfIdle(self):
        self.port.write(b"?")
        if b"Idle" in self.waitForResponse():
            if self.servoGripper.mode is "idle":
                return True
        else:
            return False

    def setMode(self, mode):
        if mode is 'follow':
            self.mode = 'follow'
            print("Follow mode enabled.")
        elif mode is 'replay':
            self.mode = 'replay'
            print("Replay mode enabled.")
        elif mode is 'idle':
            self.mode = 'idle'
            print("Arm is idle.")
        else:
            raise NameError('unknown mode.')

    def moveToPosition(self, targetPosDict):
        self.sendTargetPositions(
            -targetPosDict["X"], 
            targetPosDict["Y"], 
            -targetPosDict["Z"])

    def moveToPositionRaw(self, targetPosDict):
        self.sendTargetPositions(
            targetPosDict["X"], 
            targetPosDict["Y"], 
            targetPosDict["Z"])

    def moveGripperToPosition(self, pos):
        self.servoGripper.setTargetPos(pos)

    def sendTargetPositions(self, x, y, z):
        self.currentPosDict = {"X": x, "Y": y, "Z": z}
        self.port.write(b"G90 G0 ")
        self.port.write(b" X" + "{:.4f}".format(x).encode())
        self.port.write(b" Y" + "{:.4f}".format(y).encode())
        self.port.write(b" Z" + "{:.4f}".format(z).encode())
        self.port.write(b"\n")
        self.waitForResponse()

    def getTotalChange(self, rArmPosDict):
        total = abs(-rArmPosDict["X"] - self.currentPosDict["X"])
        total = total + abs(rArmPosDict["Y"] - self.currentPosDict["Y"])
        total = total + abs(-rArmPosDict["Z"] - self.currentPosDict["Z"])
        return total

    def shortPressAction(self):
        # This function gets executed on short button press.
        if self.mode is 'follow':
            self.saveCurrentPos()
        else:
            print("Preparing Replay.")
            self.prepareReplay()

    def saveCurrentPos(self):
        print("Saving current position.")
        self.replayList.append(('arm', dict(self.currentPosDict)))
        self.replayList.append(('gripper', self.servoGripper.currentPos))
        self.blinkLED.setMode('fastBlinkTwice')

    def prepareReplay(self):
        # copy replay list into replay step list
        self.replayStepList = list(self.replayList)

    def deleteReplayList(self):
        print("Deleting replay List.")
        self.replayList = []

    def setEndlessReplay(self, value):
        print('Endless replay:', value)
        self.endlessReplay = value 

    def replayEnded(self):
        if self.endlessReplay:
            self.prepareReplay()
        else:
            print("Replay has completed.")

    def useCurrentPosAsOrigin(self):
        self.port.write(b"G10 P0 L20 X0 Y0 Z0")
        self.port.write(b"\n")
        self.waitForResponse()
        
    def setMotorHold(self, mode):
        if mode is 'hold':
            print("Motors are holding themselves in place.")
            self.port.write(b"$1 = 255")
            self.port.write(b"\n")
            self.waitForResponse()
        elif mode is 'release':
            print("Motors have released their hold.")
            self.port.write(b"$1 = 0")
            self.port.write(b"\n")
            self.waitForResponse()
        else:
            raise NameError('unknown mode.')