#!/usr/bin/python3

import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import RPi.GPIO as GPIO

# - - - - - - - - - - - - - - - - 
# - - -  ReplicaRobotArm  - - - -
# - - - - - - - - - - - - - - - -
class ReplicaRobotArm:
    def __init__(self):
        self.mcp      = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(0, 0))
        self.posDict  = {"X": 0, "Y": 0, "Z": 0}
        self.servoPos = 0
        self.corrDict = {"X": 0, "Y": 0, "Z": 0}
        self.getCorrValues()
        self.k = 0.002
        self.k_z = 0.003

    def update(self):
        self.updatePosDict()
        self.updateServoPos()
        self.offsetPosDict()
        self.multiplyPosDict()
       # self.printPosDict()

    def getCorrValues(self):
        print("Returning to the origin position.")
        self.corrDict["X"] = self.mcp.read_adc(1)
        self.corrDict["Y"] = self.mcp.read_adc(2)
        self.corrDict["Z"] = self.mcp.read_adc(3)

    def updatePosDict(self):
        self.posDict["X"] = self.mcp.read_adc(1)
        self.posDict["Y"] = self.mcp.read_adc(2)
        self.posDict["Z"] = self.mcp.read_adc(3)

    def updateServoPos(self):
        self.servoPos = self.mcp.read_adc(0)

    def offsetPosDict(self):
        for key, value in self.posDict.items():
            self.posDict[key] = value - self.corrDict[key] 

    def multiplyPosDict(self):
        for key, value in self.posDict.items():
            if key == "Z":
                self.posDict[key] = value * self.k_z
            else:
                self.posDict[key] = value * self.k

    def printPosDict(self):
        for key, value in self.posDict.items():
            print(key, value)

# - - - - - - - - - - - - - - - - 
# 0 1 2 3
# s X Y Z
# X -> Lefthand rotation (Grey gear)
# Y -> Righthand rotation (Black gear)
# Z -> Base rotation
# - - - - - - - - - - - - - - - -