
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

def yerFaceTopBoneCoordinateMapper(inputs):
    outputs = {}
    outputs['x'] = inputs['x'] * unitScale
    outputs['y'] = inputs['y'] * (-1.0) * unitScale
    outputs['z'] = inputs['z'] * (-1.0) * unitScale
    return outputs

def yerFaceTopBoneRotationMapper(inputs):
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
        self.object = context.scene.objects['Snufflefungus']
        self.topBone = self.object.pose.bones['Top']
        self.faceArmature = context.scene.objects['Snufflefungus Face Armature']
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
                    translation = yerFaceTopBoneCoordinateMapper(packet['pose']['translation'])
                    self.locationOffsetX = translation['x']
                    self.locationOffsetY = translation['y']
                    self.locationOffsetZ = translation['z']
                    rotation = yerFaceTopBoneRotationMapper(packet['pose']['rotation'])
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
                translation = yerFaceTopBoneCoordinateMapper(packet['pose']['translation'])
                self.topBone.location.x = poseLocationXScale * (translation['x'] - self.locationOffsetX)
                self.topBone.location.y = poseLocationYScale * (translation['y'] - self.locationOffsetY)
                self.topBone.location.z = poseLocationZScale * (translation['z'] - self.locationOffsetZ)
                rotation = yerFaceTopBoneRotationMapper(packet['pose']['rotation'])
                self.topBone.rotation_mode = 'XYZ'
                self.topBone.rotation_euler.x = math.radians(rotation['x'] - self.rotationOffsetX)
                self.topBone.rotation_euler.y = math.radians(rotation['y'] - self.rotationOffsetY)
                self.topBone.rotation_euler.z = math.radians(rotation['z'] - self.rotationOffsetZ)
            if 'trackers' in packet:
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
