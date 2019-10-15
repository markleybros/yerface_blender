
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
        if localKey not in self.currentFrameValues:
            self.currentFrameValues[localKey] = {
                "target": target,
                "dataPath": dataPath,
                "anticipation": anticipation,
                "values": {}
            }
        for axis, value in newValues.items():
            if axis not in self.currentFrameValues[localKey]['values']:
                self.currentFrameValues[localKey]['values'][axis] = [];
            self.currentFrameValues[localKey]['values'][axis].append(value)

    def flushFrame(self, flushFrameNumber = -1, discardFrameData = False, samplingMode = 'average'):
        if not discardFrameData:
            for localKey, dict in self.currentFrameValues.items():
                accumulatedValues = {}
                for axis, values in dict["values"].items():
                    accumulatedValues[axis] = 0.0
                    if samplingMode == 'average':
                        for value in values:
                            accumulatedValues[axis] = accumulatedValues[axis] + (value / len(values))
                    elif samplingMode == 'first':
                        accumulatedValues[axis] = values[0]
                    elif samplingMode == 'last':
                        accumulatedValues[axis] = values[-1]

                self.handleKeyframeInsertion(frameNumber=flushFrameNumber, localKey=localKey, target=dict["target"], dataPath=dict["dataPath"], newValues=accumulatedValues, anticipation=dict["anticipation"])
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
