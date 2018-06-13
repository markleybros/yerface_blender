
bl_info = {
    'name': 'YerFace: Blender Plugin',
    'author': 'Alex Markley',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': 'TBD',
    'description': 'Blender integration with the YerFace performance capture tool.',
    'category': 'Animation'
}

import bpy
import sys
import os
import errno
import json
import math
import time
from threading import Lock, Thread

def syspathMunge(newpath):
    if newpath not in sys.path:
        sys.path.append(newpath)

syspathMunge(os.path.abspath(os.path.dirname(__file__) + "/vendor"))
from lomond import WebSocket

isPreviewRunning = False
myPreviewTimer = None
myReader = None
myUpdater = None
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
    def __init__(self, context):
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
    def runUpdate(self):
        global myReader
        packets = myReader.returnNextPackets()
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

class YerFaceWebsocketReader:
    def __init__(self):
        self.packets = None
        self.packetsLock = Lock()
        self.websocket = None
        self.thread = None
        self.running = False
    def openWebsocket(self):
        self.packets = []
        self.running = True
        self.thread = Thread(target=self.runWebsocketThread)
        self.thread.start()
    def closeWebsocket(self):
        self.running = False
        self.websocket.close()
        self.thread.join()
        self.thread = None
        self.websocket = None
    def runWebsocketThread(self):
        attempt = 0
        while self.running:
            if attempt > 0:
                time.sleep(0.1)
            attempt = attempt + 1
            self.websocket = WebSocket('ws://localhost:9002')
            for event in self.websocket:
                if event.name == 'text':
                    packetObj = None
                    try:
                        packetObj = json.loads(event.text)
                    except:
                        print("Failed parsing a Websocket event as JSON: " + event.text)
                        continue
                    if packetObj == None:
                        print("Got a NULL event for some reason.")
                        continue
                    self.packetsLock.acquire()
                    self.packets.append(packetObj)
                    self.packetsLock.release()
                else:
                    if not self.running:
                        print("Websocket client thread exiting.")
                        return
    def returnNextPackets(self):
        self.packetsLock.acquire()
        copyPackets = list(self.packets)
        self.packetsLock.release()
        return copyPackets


class YerFacePreviewStartOperator(bpy.types.Operator):
    bl_idname = "wm.yerface_preview_start"
    bl_label = "YerFace Preview Start"
    bl_description = "Start previewing data from the Yer Face performance capture tool."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        global isPreviewRunning
        global myUpdater
        if event.type == 'ESC' or not isPreviewRunning:
            return self.cancel(context)
        if event.type == 'TIMER':
            myUpdater.runUpdate()
        return {'PASS_THROUGH'}

    def execute(self, context):
        global isPreviewRunning
        global myPreviewTimer
        global myReader
        global myUpdater
        isPreviewRunning = True
        if myReader is None:
            myReader = YerFaceWebsocketReader()
        myReader.openWebsocket()
        myUpdater = YerFaceSceneUpdater(context)
        context.window_manager.modal_handler_add(self)
        myPreviewTimer = context.window_manager.event_timer_add(1/context.scene.render.fps, context.window)
        print("STARTED TIMER")
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        global isPreviewRunning
        global myPreviewTimer
        if isPreviewRunning:
            isPreviewRunning = False
            context.window_manager.event_timer_remove(myPreviewTimer)
            myReader.closeWebsocket()
            print("CANCELLED TIMER")
        return {'CANCELLED'}


class YerFacePreviewStopOperator(bpy.types.Operator):
    bl_idname = "wm.yerface_preview_stop"
    bl_label = "YerFace Preview Stop"
    bl_description = "Stop previewing data from the Yer Face performance capture tool."
    bl_options = {'REGISTER'}

    def execute(self, context):
        YerFacePreviewStartOperator.cancel(None, context)
        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
