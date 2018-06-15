
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

        box = layout.box()
        box.label(text="Motion / Translation Settings")
        box.prop_search(props, "translationTargetObject", context.scene, "objects")
        if props.translationTargetObject in context.scene.objects and context.scene.objects[props.translationTargetObject].type == "ARMATURE":
            obj = context.scene.objects[props.translationTargetObject]
            box.prop_search(props, "translationTargetBone", obj.pose, "bones")
        box.prop(props, "translationScale")

        box = layout.box()
        box.label(text="Rotation Settings")
        box.prop_search(props, "rotationTargetObject", context.scene, "objects")
        if props.rotationTargetObject in context.scene.objects and context.scene.objects[props.rotationTargetObject].type == "ARMATURE":
            obj = context.scene.objects[props.rotationTargetObject]
            box.prop_search(props, "rotationTargetBone", obj.pose, "bones")

        box = layout.box()
        box.label(text="Facial Rig / Bone Settings")
        box.prop_search(props, "faceArmatureObject", context.scene, "objects")

        box = layout.box()
        box.label(text="Live Input Data Settings")
        box.prop(props, "websocketURI")

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
