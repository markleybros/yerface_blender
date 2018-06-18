
import bpy

import yerface_blender.SceneUtilities

class YerFaceImportOperator(bpy.types.Operator):
    bl_idname = "yerface.do_import"
    bl_label = "Do Import"
    bl_description = "Imports YerFace performance capture data to keyframes."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        props = context.scene.yerFaceBlenderProperties

        print("Howdy hey: ", props.inputFilePath)

        return {'FINISHED'}
