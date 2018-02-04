
bl_info = {
    'name': 'Yer Face: Blender Plugin',
    'author': 'Alex Markley',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': 'TBD',
    'description': 'Blender integration with the Yer Face performance capture tool.',
    'category': 'Animation'
}

import bpy
import os
import errno
import json
import math

isPreviewRunning = False
myPreviewTimer = None
myReader = None
myUpdater = None
unitScale = 0.001


class YerFaceSceneUpdater:
    def __init__(self, context):
        self.object = context.scene.objects['Cube']
        self.locationOffsetX = 0.0
        self.locationOffsetY = 0.0
        self.locationOffsetZ = 0.0
        self.rotationOffsetX = 0.0
        self.rotationOffsetY = 0.0
        self.rotationOffsetZ = 0.0
    def runUpdate(self):
        global myReader
        global unitScale
        packets = myReader.returnNextPackets()
        if len(packets) < 1:
            return
        for packet in packets:
            if packet['meta']['basis']:
                if 'pose' in packet:
                    self.locationOffsetX = packet['pose']['translation']['x'] * (-1.0) * unitScale
                    self.locationOffsetY = packet['pose']['translation']['z'] * unitScale
                    self.locationOffsetZ = packet['pose']['translation']['y'] * unitScale
                    self.rotationOffsetX = packet['pose']['rotation']['x'] * (-1.0)
                    self.rotationOffsetY = packet['pose']['rotation']['z'] * (-1.0)
                    self.rotationOffsetZ = packet['pose']['rotation']['y'] * (-1.0)
            if 'pose' in packet:
                self.object.delta_location.x = (packet['pose']['translation']['x'] * unitScale) + self.locationOffsetX
                self.object.delta_location.y = (packet['pose']['translation']['z'] * (-1.0) * unitScale) + self.locationOffsetY
                self.object.delta_location.z = (packet['pose']['translation']['y'] * (-1.0) * unitScale) + self.locationOffsetZ
                self.object.delta_rotation_euler.x = math.radians(packet['pose']['rotation']['x'] + self.rotationOffsetX)
                self.object.delta_rotation_euler.y = math.radians(packet['pose']['rotation']['z'] + self.rotationOffsetY)
                self.object.delta_rotation_euler.z = math.radians(packet['pose']['rotation']['y'] + self.rotationOffsetZ)

class YerFacePipeReader:
    def __init__(self):
        self.openPipe()
    def openPipe(self):
        self.pipe = None
        self.packetBuffer = ""
        self.pipe = os.open("/tmp/yerface", os.O_RDONLY | os.O_NONBLOCK)
    def closePipe(self):
        os.close(self.pipe)
        self.pipe = None
    def returnNextPackets(self):
        packets = []
        gotAnyFragments = False
        buffer = True
        while buffer != None:
            try:
                buffer = os.read(self.pipe, 1024)
                if len(buffer) > 0:
                    self.packetBuffer += buffer.decode('UTF-8')
                    gotAnyFragments = True
                else:
                    buffer = None
            except OSError as err:
                if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
                    buffer = None
                else:
                    raise
        if gotAnyFragments:
            hunting = True
            while hunting:
                firstBreak = self.packetBuffer.find("\n")
                if firstBreak >= 0:
                    packet = self.packetBuffer[:firstBreak]
                    self.packetBuffer = self.packetBuffer[firstBreak+1:]
                    packetObj = None
                    try:
                        packetObj = json.loads(packet)
                        packets.append(packetObj)
                    except:
                        print("Failed parsing a packet as JSON: " + packet)
                else:
                    hunting = False
        return packets


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
            myReader = YerFacePipeReader()
        else:
            myReader.openPipe()
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
            myReader.closePipe()
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
