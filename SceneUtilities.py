
import math

unitScale = 0.00328084 # millimeters to feet
#unitScale = 0.01
faceBoneUnitScale = 0.01
poseLocationXScale = 0.5
poseLocationYScale = 1.0
poseLocationZScale = 0.5

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

def yerFaceTranslationTargetCoordinateMapper(inputs):
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

def yerFaceFaceBoneCoordinateMapper(inputs):
    outputs = {}
    outputs['x'] = inputs['x'] * faceBoneUnitScale
    outputs['y'] = inputs['y'] * (-1.0) * faceBoneUnitScale
    outputs['z'] = inputs['z'] * (-1.0) * faceBoneUnitScale
    return outputs


class YerFaceSceneUpdater:
    def __init__(self, context, myReader):
        self.props = context.scene.yerFaceBlenderProperties
        self.translationTarget = None
        if len(self.props.translationTargetObject) > 0:
            obj = context.scene.objects[self.props.translationTargetObject]
            self.translationTarget = obj
            if obj.type == "ARMATURE" and len(self.props.translationTargetBone) > 0:
                self.translationTarget = obj.pose.bones[self.props.translationTargetBone]
        self.rotationTarget = None
        if len(self.props.rotationTargetObject) > 0:
            obj = context.scene.objects[self.props.rotationTargetObject]
            self.rotationTarget = obj
            if obj.type == "ARMATURE" and len(self.props.rotationTargetBone) > 0:
                self.rotationTarget = obj.pose.bones[self.props.rotationTargetBone]
        self.faceArmature = None
        self.faceArmatureBones = None
        if len(self.props.faceArmatureObject) > 0:
            self.faceArmature = context.scene.objects[self.props.faceArmatureObject]
            self.faceArmatureBones = self.faceArmature.pose.bones
        self.locationOffsetX = 0.0
        self.locationOffsetY = 0.0
        self.locationOffsetZ = 0.0
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
                    translation = yerFaceTranslationTargetCoordinateMapper(packet['pose']['translation'])
                    self.locationOffsetX = translation['x']
                    self.locationOffsetY = translation['y']
                    self.locationOffsetZ = translation['z']
                    rotation = yerFaceRotationTargetRotationMapper(packet['pose']['rotation'])
                    self.rotationOffsetX = rotation['x']
                    self.rotationOffsetY = rotation['y']
                    self.rotationOffsetZ = rotation['z']
                if 'trackers' in packet:
                    for name, tracker in packet['trackers'].items():
                        translation = yerFaceFaceBoneCoordinateMapper(tracker['position'])
                        self.trackerOffsets[name] = {}
                        self.trackerOffsets[name]['x'] = translation['x']
                        self.trackerOffsets[name]['y'] = translation['y']
                        self.trackerOffsets[name]['z'] = translation['z']
            if 'pose' in packet:
                global poseLocationXScale, poseLocationYScale, poseLocationZScale;
                if self.translationTarget is not None:
                    translation = yerFaceTranslationTargetCoordinateMapper(packet['pose']['translation'])
                    self.translationTarget.location.x = poseLocationXScale * (translation['x'] - self.locationOffsetX)
                    self.translationTarget.location.y = poseLocationYScale * (translation['y'] - self.locationOffsetY)
                    self.translationTarget.location.z = poseLocationZScale * (translation['z'] - self.locationOffsetZ)
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
                        translation = yerFaceFaceBoneCoordinateMapper(tracker['position'])
                        bone.location.x = translation['x'] - self.trackerOffsets[name]['x']
                        bone.location.y = translation['y'] - self.trackerOffsets[name]['y']
                        bone.location.z = translation['z'] - self.trackerOffsets[name]['z']
