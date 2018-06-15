
import bpy

import yerface_blender.PreviewModal

class ToolsPanel(bpy.types.Panel):
    bl_label = "YerFace! Performance Capture"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Animation"

    def draw(self, context):
        # self.layout.label(text="Hello World")
        self.layout.prop(context.scene.yerFaceBlenderProperties, "websocketURI")
        if yerface_blender.PreviewModal.YerFacePreviewStartOperator.isPreviewRunning(None):
            self.layout.operator("wm.yerface_preview_stop")
        else:
            self.layout.operator("wm.yerface_preview_start")

# class TestButton(bpy.types.Operator):
#     bl_idname = "yerface.testbutton"
#     bl_label = "Say Hello"
#
#     def execute(self, context):
#         print("Hello world!", context.scene.yerFaceBlenderProperties.websocketURI)
#         return {'FINISHED'}
