
import math
import bpy

def interpretAxisAsRNAIndex(axis):
    rnaAxisMap = {
        "x": 0,
        "y": 1,
        "z": 2
    }
    if axis in rnaAxisMap:
        return rnaAxisMap[axis]
    return -1

def handleUpdateTargetAll(target, dataPath, newValues):
    for axis, value in newValues.items():
        handleUpdateTarget(target, dataPath, axis, value)

def handleUpdateTarget(target, dataPath, axis, value):
    idx = interpretAxisAsRNAIndex(axis)
    if idx >= 0:
        setattr(getattr(target, dataPath), axis, value)
    else:
        setattr(target, dataPath, value)

class KeyframeHelper:
    def __init__(self):
        self.lastSetValues = {}
        self.currentFrameValues = {}

    def accumulateFrameData(self, localKey, target, dataPath, newValues, anticipation):
        self.currentFrameValues[localKey] = {
            "target": target,
            "dataPath": dataPath,
            "anticipation": anticipation,
            "values": newValues
        }

    def flushFrame(self, flushFrameNumber = -1, discardFrameData = False):
        if not discardFrameData:
            for localKey, dict in self.currentFrameValues.items():
                self.handleKeyframeInsertion(frameNumber=flushFrameNumber, localKey=localKey, target=dict["target"], dataPath=dict["dataPath"], newValues=dict["values"], anticipation=dict["anticipation"])
        self.currentFrameValues = {}

    def handleKeyframeInsertion(self, frameNumber, localKey, target, dataPath, newValues, anticipation):
        for axis, value in newValues.items():
            if localKey not in self.lastSetValues:
                self.lastSetValues[localKey] = {}
            if axis not in self.lastSetValues[localKey]:
                self.lastSetValues[localKey][axis] = {}
            if "value" in self.lastSetValues[localKey][axis]:
                delta = abs(value - self.lastSetValues[localKey][axis]["value"])
                if delta < 0.0000000001:
                    continue
                if frameNumber - self.lastSetValues[localKey][axis]["frame"] > anticipation:
                    handleUpdateTarget(target, dataPath, axis, self.lastSetValues[localKey][axis]["value"])
                    target.keyframe_insert(data_path=dataPath, index=interpretAxisAsRNAIndex(axis), frame=frameNumber - anticipation)
            handleUpdateTarget(target, dataPath, axis, value)
            target.keyframe_insert(data_path=dataPath, index=interpretAxisAsRNAIndex(axis), frame=frameNumber)
            self.lastSetValues[localKey][axis]["value"] = value
            self.lastSetValues[localKey][axis]["frame"] = frameNumber
