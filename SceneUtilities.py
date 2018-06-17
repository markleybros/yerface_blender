
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

        self.reader = myReader
    def runUpdate(self):
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
                    self.translationTarget.location.x = self.translationScaleX * (translation['x'] - self.locationOffsetX)
                    self.translationTarget.location.y = self.translationScaleY * (translation['y'] - self.locationOffsetY)
                    self.translationTarget.location.z = self.translationScaleZ * (translation['z'] - self.locationOffsetZ)
                if self.rotationTarget is not None:
                    rotation = self.RotationTargetRotationMapper(packet['pose']['rotation'])
                    self.rotationTarget.rotation_mode = 'XYZ'
                    self.rotationTarget.rotation_euler.x = math.radians(self.rotationScaleX * (rotation['x'] - self.rotationOffsetX))
                    self.rotationTarget.rotation_euler.y = math.radians(self.rotationScaleY * (rotation['y'] - self.rotationOffsetY))
                    self.rotationTarget.rotation_euler.z = math.radians(self.rotationScaleZ * (rotation['z'] - self.rotationOffsetZ))
            if 'trackers' in packet and self.faceArmatureBones is not None:
                for name, tracker in packet['trackers'].items():
                    if name not in self.trackerOffsets:
                        self.trackerOffsets[name] = {'x': 0.0, 'y': 0.0, 'z': 0.0}

                    if name not in self.faceArmatureBones:
                        print("Could not operate on bone " + name + " because it does not exist within armature!")
                    else:
                        bone = self.faceArmatureBones[name]
                        translation = self.FaceBoneCoordinateMapper(tracker['position'])
                        bone.location.x = translation['x'] - self.trackerOffsets[name]['x']
                        bone.location.y = translation['y'] - self.trackerOffsets[name]['y']
                        bone.location.z = translation['z'] - self.trackerOffsets[name]['z']

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
