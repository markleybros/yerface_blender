
import bpy
import json

from . import SceneUtilities
from . import FIFOReader

class YERFACE_OT_ImportFromFile(bpy.types.Operator):
    bl_idname = "yerface.do_import"
    bl_label = "Do Import"
    bl_description = "Imports YerFace performance capture data to keyframes."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        props = context.scene.yerFaceBlenderProperties

        fps = context.scene.render.fps / context.scene.render.fps_base
        print("Scene FPS is set to: ", fps)

        myReader = FIFOReader.YerFaceFIFOReader()
        myUpdater = SceneUtilities.YerFaceSceneUpdater(context, myReader, fps)

        if props.tickCallback != "":
            tickProps = {
                'userData': props.tickUserData,
                'resetState': True,
                'perfcapPacket': {},
                'insertKeyframes': True,
                'currentFrameNumber': None,
                'flushLastFrame': False,
                'discardLastFrameData': False,
                'samplingMode': None,
                'framesPerSecond': fps
            }
            bpy.app.driver_namespace[props.tickCallback](tickProps)

        print("Kicked off Yer-Face import with file: ", props.inputFilePath)
        try:
            f = open(bpy.path.abspath(props.inputFilePath), "r")
        except:
            print("Failed to open Yer-Face data file!")
            return {'CANCELLED'}

        lastFrame = None
        for line in f:
            packetObj = None
            try:
                packetObj = json.loads(line)
            except:
                print("Failed parsing a line in the YerFace data file!")
                continue
            if packetObj == None:
                print("Got a NULL entry in the YerFace data file for some reason.")
                continue

            myReader.insertNextPacket(packetObj)

            frame = int((packetObj['meta']['startTime'] * fps) + props.importStartFrame)

            if lastFrame is None or frame != lastFrame:
                if lastFrame is not None:
                    discardFrame = False
                    if lastFrame < props.importStartFrame:
                        discardFrame = True
                    myUpdater.flushFrame(lastFrame, discardFrame)
                context.scene.frame_set(frame)

            myUpdater.runUpdate(insertKeyframes=True, currentFrameNumber=frame)
            lastFrame = frame

        if lastFrame is not None:
            myUpdater.flushFrame(lastFrame)

        f.close()

        return {'FINISHED'}
