
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

        layout.label(text="Motion / Translation Settings:")
        box = layout.box()
        box.label(text="Optional target for facial pose motion:")
        box.prop_search(props, "translationTargetObject", context.scene, "objects")
        if props.translationTargetObject in context.scene.objects and context.scene.objects[props.translationTargetObject].type == "ARMATURE":
            obj = context.scene.objects[props.translationTargetObject]
            box.prop_search(props, "translationTargetBone", obj.pose, "bones")
        box.label(text="Overall scale for translation:")
        box.prop(props, "translationScale")
        box.label(text="Per-axis scale for translation:")
        split = box.split(align=True)
        split.prop(props, "translationScaleX")
        split.prop(props, "translationScaleY")
        split.prop(props, "translationScaleZ")

        layout.label(text="Rotation Settings:")
        box = layout.box()
        box.label(text="Optional target for facial pose rotation:")
        box.prop_search(props, "rotationTargetObject", context.scene, "objects")
        if props.rotationTargetObject in context.scene.objects and context.scene.objects[props.rotationTargetObject].type == "ARMATURE":
            obj = context.scene.objects[props.rotationTargetObject]
            box.prop_search(props, "rotationTargetBone", obj.pose, "bones")

        layout.label(text="Facial Rig / Bone Settings:")
        box = layout.box()
        box.prop_search(props, "faceArmatureObject", context.scene, "objects")
        box.label(text="Scale for face bone motion:")
        box.prop(props, "faceBoneTranslationScale")

        layout.label(text="Live Input Data Settings:")
        box = layout.box()
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
