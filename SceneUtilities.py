
import math

# def yerFaceCoordinateMapper(inputs):
#     outputs = {}
#     outputs['x'] = inputs['x'] * unitScale
#     outputs['y'] = inputs['z'] * unitScale
#     outputs['z'] = inputs['y'] * (-1.0) * unitScale
#     return outputs
#
# def yerFaceRotationMapper(inputs):
#     outputs = {}
#     outputs['x'] = inputs['x'] * (-1.0)
#     outputs['y'] = inputs['z']
#     outputs['z'] = inputs['y']
#     return outputs

def yerFaceTranslationTargetCoordinateMapper(inputs, unitScale):
    outputs = {}
    outputs['x'] = inputs['x'] * unitScale
    outputs['y'] = inputs['y'] * (-1.0) * unitScale
    outputs['z'] = inputs['z'] * (-1.0) * unitScale
    return outputs

def yerFaceRotationTargetRotationMapper(inputs):
    outputs = {}
    outputs['x'] = inputs['x']
    outputs['y'] = inputs['y'] * (-1.0)
    outputs['z'] = inputs['z'] * (-1.0)
    return outputs

def yerFaceFaceBoneCoordinateMapper(inputs, unitScale):
    outputs = {}
    outputs['x'] = inputs['x'] * unitScale
    outputs['y'] = inputs['y'] * (-1.0) * unitScale
    outputs['z'] = inputs['z'] * (-1.0) * unitScale
    return outputs


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

        self.rotationTarget = context.scene.objects.get(self.props.rotationTargetObject)
        if self.rotationTarget is not None:
            if self.rotationTarget.type == "ARMATURE" and len(self.props.rotationTargetBone) > 0:
                bone = self.rotationTarget.pose.bones.get(self.props.rotationTargetBone)
                if bone is not None:
                    self.rotationTarget = bone

        self.faceArmature = None
        self.faceArmatureBones = None
        if len(self.props.faceArmatureObject) > 0:
            self.faceArmature = context.scene.objects[self.props.faceArmatureObject]
            self.faceArmatureBones = self.faceArmature.pose.bones
        self.faceBoneTranslationScale = self.props.faceBoneTranslationScale

        self.locationOffsetX = 0.0
        self.locationOffsetY = 0.0
        self.locationOffsetZ = 0.0
        self.translationScaleX = self.props.translationScaleX
        self.translationScaleY = self.props.translationScaleY
        self.translationScaleZ = self.props.translationScaleZ

        self.rotationOffsetX = 0.0
        self.rotationOffsetY = 0.0
        self.rotationOffsetZ = 0.0
        self.trackerOffsets = {}

        self.reader = myReader
    def runUpdate(self):
        packets = self.reader.returnNextPackets()
        if len(packets) < 1:
            return
        for packet in packets:
            if packet['meta']['basis']:
                if 'pose' in packet:
                    translation = yerFaceTranslationTargetCoordinateMapper(packet['pose']['translation'], self.translationScale)
                    self.locationOffsetX = translation['x']
                    self.locationOffsetY = translation['y']
                    self.locationOffsetZ = translation['z']
                    rotation = yerFaceRotationTargetRotationMapper(packet['pose']['rotation'])
                    self.rotationOffsetX = rotation['x']
                    self.rotationOffsetY = rotation['y']
                    self.rotationOffsetZ = rotation['z']
                if 'trackers' in packet:
                    for name, tracker in packet['trackers'].items():
                        translation = yerFaceFaceBoneCoordinateMapper(tracker['position'], self.faceBoneTranslationScale)
                        self.trackerOffsets[name] = {}
                        self.trackerOffsets[name]['x'] = translation['x']
                        self.trackerOffsets[name]['y'] = translation['y']
                        self.trackerOffsets[name]['z'] = translation['z']
            if 'pose' in packet:
                if self.translationTarget is not None:
                    translation = yerFaceTranslationTargetCoordinateMapper(packet['pose']['translation'], self.translationScale)
                    self.translationTarget.location.x = self.translationScaleX * (translation['x'] - self.locationOffsetX)
                    self.translationTarget.location.y = self.translationScaleY * (translation['y'] - self.locationOffsetY)
                    self.translationTarget.location.z = self.translationScaleZ * (translation['z'] - self.locationOffsetZ)
                if self.rotationTarget is not None:
                    rotation = yerFaceRotationTargetRotationMapper(packet['pose']['rotation'])
                    self.rotationTarget.rotation_mode = 'XYZ'
                    self.rotationTarget.rotation_euler.x = math.radians(rotation['x'] - self.rotationOffsetX)
                    self.rotationTarget.rotation_euler.y = math.radians(rotation['y'] - self.rotationOffsetY)
                    self.rotationTarget.rotation_euler.z = math.radians(rotation['z'] - self.rotationOffsetZ)
            if 'trackers' in packet and self.faceArmatureBones is not None:
                for name, tracker in packet['trackers'].items():
                    if name not in self.trackerOffsets:
                        self.trackerOffsets[name] = {'x': 0.0, 'y': 0.0, 'z': 0.0}

                    if name not in self.faceArmatureBones:
                        print("Could not operate on bone " + name + " because it does not exist within armature!")
                    else:
                        bone = self.faceArmatureBones[name]
                        translation = yerFaceFaceBoneCoordinateMapper(tracker['position'], self.faceBoneTranslationScale)
                        bone.location.x = translation['x'] - self.trackerOffsets[name]['x']
                        bone.location.y = translation['y'] - self.trackerOffsets[name]['y']
                        bone.location.z = translation['z'] - self.trackerOffsets[name]['z']
