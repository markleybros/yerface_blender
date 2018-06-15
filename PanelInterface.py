
import bpy

import yerface_blender.PreviewModal

class ToolsPanel(bpy.types.Panel):
    bl_label = "YerFace! Performance Capture"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Animation"

    def draw(self, context):
        layout = self.layout
        props = context.scene.yerFaceBlenderProperties
        # self.layout.label(text="Hello World")
        layout.prop_search(props, "translationTargetObject", context.scene, "objects")
        if props.translationTargetObject in context.scene.objects and context.scene.objects[props.translationTargetObject].type == "ARMATURE":
            obj = context.scene.objects[props.translationTargetObject]
            layout.prop_search(props, "translationTargetBone", obj.pose, "bones")
        layout.prop_search(props, "rotationTargetObject", context.scene, "objects")
        if props.rotationTargetObject in context.scene.objects and context.scene.objects[props.rotationTargetObject].type == "ARMATURE":
            obj = context.scene.objects[props.rotationTargetObject]
            layout.prop_search(props, "rotationTargetBone", obj.pose, "bones")
        layout.prop_search(props, "faceArmatureObject", context.scene, "objects")
        layout.prop(props, "websocketURI")
        if yerface_blender.PreviewModal.YerFacePreviewStartOperator.isPreviewRunning(None):
            layout.operator("wm.yerface_preview_stop")
        else:
            layout.operator("wm.yerface_preview_start")

# class TestButton(bpy.types.Operator):
#     bl_idname = "yerface.testbutton"
#     bl_label = "Say Hello"
#
#     def execute(self, context):
#         print("Hello world!", context.scene.yerFaceBlenderProperties.websocketURI)
#         return {'FINISHED'}
