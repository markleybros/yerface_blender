
import bpy
import json

import yerface_blender.SceneUtilities
import yerface_blender.FIFOReader

class YerFaceImportOperator(bpy.types.Operator):
    bl_idname = "yerface.do_import"
    bl_label = "Do Import"
    bl_description = "Imports YerFace performance capture data to keyframes."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        props = context.scene.yerFaceBlenderProperties

        myReader = yerface_blender.FIFOReader.YerFaceFIFOReader()
        myUpdater = yerface_blender.SceneUtilities.YerFaceSceneUpdater(context, myReader)

        print("Kicked off Yer-Face import with file: ", props.inputFilePath)
        try:
            f = open(props.inputFilePath, "r")
        except:
            print("Failed to open Yer-Face data file!")
            return {'CANCELLED'}

        fps = context.scene.render.fps / context.scene.render.fps_base
        print("Scene FPS is set to: ", fps)

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

            myUpdater.runUpdate(insertKeyframes=True, currentFrameNumber=frame)

        f.close()

        return {'FINISHED'}
