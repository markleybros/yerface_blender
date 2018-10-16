
import math

class YerFaceSceneUpdater:
    def __init__(self, context, myReader):
        self.props = context.scene.yerFaceBlenderProperties

        self.translationTarget = context.scene.objects.get(self.props.translationTargetObject)
        if self.translationTarget is not None:
            if self.translationTarget.type == "ARMATURE" and len(self.props.translationTargetBone) > 0:
                bone = self.translationTarget.pose.bones.get(self.props.translationTargetBone)
                if bone is not None:
                    self.translationTarget = bone
        self.translationScale = self.props.translationScale
        self.translationAxisMap = {
            'x': self.interpretAxisMapProp(self.props.translationAxisMapX),
            'y': self.interpretAxisMapProp(self.props.translationAxisMapY),
            'z': self.interpretAxisMapProp(self.props.translationAxisMapZ)
        }

        self.rotationTarget = context.scene.objects.get(self.props.rotationTargetObject)
        if self.rotationTarget is not None:
            if self.rotationTarget.type == "ARMATURE" and len(self.props.rotationTargetBone) > 0:
                bone = self.rotationTarget.pose.bones.get(self.props.rotationTargetBone)
                if bone is not None:
                    self.rotationTarget = bone
        self.rotationScale = self.props.rotationScale
        self.rotationAxisMap = {
            'x': self.interpretAxisMapProp(self.props.rotationAxisMapX),
            'y': self.interpretAxisMapProp(self.props.rotationAxisMapY),
            'z': self.interpretAxisMapProp(self.props.rotationAxisMapZ)
        }

        self.faceArmature = None
        self.faceArmatureBones = None
        if len(self.props.faceArmatureObject) > 0:
            self.faceArmature = context.scene.objects[self.props.faceArmatureObject]
            self.faceArmatureBones = self.faceArmature.pose.bones
        self.faceBoneTranslationScale = self.props.faceBoneTranslationScale
        self.faceBoneAxisMap = {
            'x': self.interpretAxisMapProp(self.props.faceBoneAxisMapX),
            'y': self.interpretAxisMapProp(self.props.faceBoneAxisMapY),
            'z': self.interpretAxisMapProp(self.props.faceBoneAxisMapZ)
        }

        self.phonemesTarget = None
        if len(self.props.phonemesTargetObject) > 0:
            self.phonemesTarget = context.scene.objects.get(self.props.phonemesTargetObject)
        self.phonemesScale = self.props.phonemesScale

        self.locationOffsetX = 0.0
        self.locationOffsetY = 0.0
        self.locationOffsetZ = 0.0
        self.translationScaleX = self.props.translationScaleX
        self.translationScaleY = self.props.translationScaleY
        self.translationScaleZ = self.props.translationScaleZ

        self.rotationOffsetX = 0.0
        self.rotationOffsetY = 0.0
        self.rotationOffsetZ = 0.0
        self.rotationScaleX = self.props.rotationScaleX
        self.rotationScaleY = self.props.rotationScaleY
        self.rotationScaleZ = self.props.rotationScaleZ

        self.trackerOffsets = {}
        self.trackerWarnedAlready = {}

        self.phonemesWarnedAlready = {}

        self.oldValues = {}

        self.reader = myReader
    def runUpdate(self, insertKeyframes = False, currentFrameNumber = -1):
        packets = self.reader.returnNextPackets()
        if len(packets) < 1:
            return
        for packet in packets:
            if packet['meta']['basis']:
                if 'pose' in packet:
                    translation = self.TranslationTargetCoordinateMapper(packet['pose']['translation'])
                    self.locationOffsetX = translation['x']
                    self.locationOffsetY = translation['y']
                    self.locationOffsetZ = translation['z']
                    rotation = self.RotationTargetRotationMapper(packet['pose']['rotation'])
                    self.rotationOffsetX = rotation['x']
                    self.rotationOffsetY = rotation['y']
                    self.rotationOffsetZ = rotation['z']
                if 'trackers' in packet:
                    for name, tracker in packet['trackers'].items():
                        translation = self.FaceBoneCoordinateMapper(tracker['position'])
                        self.trackerOffsets[name] = {}
                        self.trackerOffsets[name]['x'] = translation['x']
                        self.trackerOffsets[name]['y'] = translation['y']
                        self.trackerOffsets[name]['z'] = translation['z']
            if 'pose' in packet:
                if self.translationTarget is not None:
                    translation = self.TranslationTargetCoordinateMapper(packet['pose']['translation'])
                    newValues = {
                        "x": self.translationScaleX * (translation['x'] - self.locationOffsetX),
                        "y": self.translationScaleY * (translation['y'] - self.locationOffsetY),
                        "z": self.translationScaleZ * (translation['z'] - self.locationOffsetZ)
                    }
                    self.translationTarget.location.x = newValues["x"]
                    self.translationTarget.location.y = newValues["y"]
                    self.translationTarget.location.z = newValues["z"]
                    if insertKeyframes:
                        self.handleKeyframeInsertion(localKey="translationTarget", target=self.translationTarget, dataPath="location", newValues=newValues, currentFrameNumber=currentFrameNumber)
                if self.rotationTarget is not None:
                    rotation = self.RotationTargetRotationMapper(packet['pose']['rotation'])
                    self.rotationTarget.rotation_mode = 'XYZ'
                    newValues = {
                        "x": math.radians(self.rotationScaleX * (rotation['x'] - self.rotationOffsetX)),
                        "y": math.radians(self.rotationScaleY * (rotation['y'] - self.rotationOffsetY)),
                        "z": math.radians(self.rotationScaleZ * (rotation['z'] - self.rotationOffsetZ))
                    }
                    self.rotationTarget.rotation_euler.x = newValues["x"]
                    self.rotationTarget.rotation_euler.y = newValues["y"]
                    self.rotationTarget.rotation_euler.z = newValues["z"]
                    if insertKeyframes:
                        self.handleKeyframeInsertion(localKey="rotationTarget", target=self.rotationTarget, dataPath="rotation_euler", newValues=newValues, currentFrameNumber=currentFrameNumber)
            if 'trackers' in packet and self.faceArmatureBones is not None:
                for name, tracker in packet['trackers'].items():
                    if name not in self.trackerOffsets:
                        self.trackerOffsets[name] = {'x': 0.0, 'y': 0.0, 'z': 0.0}

                    if name not in self.faceArmatureBones:
                        if name not in self.trackerWarnedAlready:
                            print("Could not operate on bone " + name + " because it does not exist within armature!")
                            self.trackerWarnedAlready[name] = True
                    else:
                        bone = self.faceArmatureBones[name]
                        translation = self.FaceBoneCoordinateMapper(tracker['position'])
                        newValues = {
                            "x": translation['x'] - self.trackerOffsets[name]['x'],
                            "y": translation['y'] - self.trackerOffsets[name]['y'],
                            "z": translation['z'] - self.trackerOffsets[name]['z']
                        }
                        bone.location.x = newValues["x"]
                        bone.location.y = newValues["y"]
                        bone.location.z = newValues["z"]
                        if insertKeyframes:
                            self.handleKeyframeInsertion(localKey="armatureBone-" + name, target=bone, dataPath="location", newValues=newValues, currentFrameNumber=currentFrameNumber)
            if 'phonemes' in packet and self.phonemesTarget is not None:
                for p, val in packet['phonemes'].items():
                    name = "Phoneme." + p
                    if name not in self.phonemesTarget:
                        if name not in self.phonemesWarnedAlready:
                            print("Could not operate on phoneme property " + name + " because it does not exist as an object property!")
                            self.phonemesWarnedAlready[name] = True
                    else:
                        newValues = {
                            "phoneme": val * self.phonemesScale
                        }
                        self.phonemesTarget[name] = newValues["phoneme"]
                        if insertKeyframes:
                            self.handleKeyframeInsertion(localKey="phoneme-" + name, target=self.phonemesTarget, dataPath="[\"" + name + "\"]", newValues=newValues, currentFrameNumber=currentFrameNumber)
                ### FIXME: Not sure of the best way to mark the object dirty after updating custom properties. This works, but it's a hack.
                if not insertKeyframes:
                    self.phonemesTarget.location.x += 0.0


    def TranslationTargetCoordinateMapper(self, inputs):
        outputs = {}
        inputs['_'] = 0.0
        for i in ['x', 'y', 'z']:
            outputs[i] = inputs[self.translationAxisMap[i]['axis']] * self.translationAxisMap[i]['invert'] * self.translationScale
        return outputs

    def RotationTargetRotationMapper(self, inputs):
        outputs = {}
        inputs['_'] = 0.0
        for i in ['x', 'y', 'z']:
            outputs[i] = inputs[self.rotationAxisMap[i]['axis']] * self.rotationAxisMap[i]['invert'] * self.rotationScale
        return outputs

    def FaceBoneCoordinateMapper(self, inputs):
        outputs = {}
        inputs['_'] = 0.0
        for i in ['x', 'y', 'z']:
            outputs[i] = inputs[self.faceBoneAxisMap[i]['axis']] * self.faceBoneAxisMap[i]['invert'] * self.faceBoneTranslationScale
        return outputs

    def interpretAxisMapProp(self, prop):
        parts = prop.split('.')
        invert = 1.0
        if parts[0] == 'n':
            invert = -1.0
        return {'invert': invert, 'axis': parts[1]}

    def interpretAxisAsRNAIndex(self, axis):
        rnaAxisMap = {
            "x": 0,
            "y": 1,
            "z": 2
        }
        if axis in rnaAxisMap:
            return rnaAxisMap[axis]
        return -1

    def handleKeyframeInsertion(self, localKey, target, dataPath, newValues, currentFrameNumber):
        for axis, value in newValues.items():
            if localKey not in self.oldValues:
                self.oldValues[localKey] = {}
            if axis not in self.oldValues[localKey]:
                self.oldValues[localKey][axis] = {}
            if "value" in self.oldValues[localKey][axis] and value == self.oldValues[localKey][axis]["value"]:
                print("deduplicating keyframe: ", localKey, axis)
                return;
            target.keyframe_insert(data_path=dataPath, index=self.interpretAxisAsRNAIndex(axis), frame=currentFrameNumber)
            self.oldValues[localKey][axis]["value"] = value
