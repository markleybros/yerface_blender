
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
        obj = context.scene.objects.get(props.translationTargetObject)
        if obj is not None and obj.type == "ARMATURE":
            box.prop_search(props, "translationTargetBone", obj.pose, "bones")
        row = box.row()
        row.prop(props, "translationShowAdvanced", icon="TRIA_DOWN" if props.translationShowAdvanced else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Advanced Settings")
        if props.translationShowAdvanced:
            box.label(text="Overall scale for translation:")
            box.prop(props, "translationScale")
            box.label(text="Per-axis scale for translation:")
            split = box.split(align=True)
            split.prop(props, "translationScaleX")
            split.prop(props, "translationScaleY")
            split.prop(props, "translationScaleZ")
            box.label(text="Map each target axis to a YerFace axis:")
            box.prop(props, "translationAxisMapX")
            box.prop(props, "translationAxisMapY")
            box.prop(props, "translationAxisMapZ")

        layout.label(text="Rotation Settings:")
        box = layout.box()
        box.label(text="Optional target for facial pose rotation:")
        box.prop_search(props, "rotationTargetObject", context.scene, "objects")
        obj = context.scene.objects.get(props.rotationTargetObject)
        if obj is not None and obj.type == "ARMATURE":
            box.prop_search(props, "rotationTargetBone", obj.pose, "bones")
        row = box.row()
        row.prop(props, "rotationShowAdvanced", icon="TRIA_DOWN" if props.rotationShowAdvanced else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Advanced Settings")
        if props.rotationShowAdvanced:
            box.label(text="Map each target axis to a YerFace axis:")
            box.prop(props, "rotationAxisMapX")
            box.prop(props, "rotationAxisMapY")
            box.prop(props, "rotationAxisMapZ")

        layout.label(text="Facial Rig / Bone Settings:")
        box = layout.box()
        box.label(text="Optional target for facial bones:")
        box.prop_search(props, "faceArmatureObject", context.scene, "objects")
        row = box.row()
        row.prop(props, "faceShowAdvanced", icon="TRIA_DOWN" if props.faceShowAdvanced else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Advanced Settings")
        if props.faceShowAdvanced:
            box.label(text="Scale for face bone motion:")
            box.prop(props, "faceBoneTranslationScale")
            box.label(text="Map each target axis to a YerFace axis:")
            box.prop(props, "faceBoneAxisMapX")
            box.prop(props, "faceBoneAxisMapY")
            box.prop(props, "faceBoneAxisMapZ")

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
