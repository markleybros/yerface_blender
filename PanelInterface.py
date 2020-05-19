
import bpy

import yerface_blender.PreviewModal
from yerface_blender.AddonProps import yerFaceInputModeItems

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
            box.prop(props, "translationAnticipationFrames")

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
            box.label(text="Overall scale for rotation:")
            box.prop(props, "rotationScale")
            box.label(text="Per-axis scale for rotation:")
            split = box.split(align=True)
            split.prop(props, "rotationScaleX")
            split.prop(props, "rotationScaleY")
            split.prop(props, "rotationScaleZ")
            box.label(text="Map each target axis to a YerFace axis:")
            box.prop(props, "rotationAxisMapX")
            box.prop(props, "rotationAxisMapY")
            box.prop(props, "rotationAxisMapZ")
            box.prop(props, "rotationAnticipationFrames")

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
            box.prop(props, "faceAnticipationFrames")

        layout.label(text="Phonemes / Mouth Shapes Settings:")
        box = layout.box()
        box.label(text="Optional target for phoneme props:")
        box.prop_search(props, "phonemesTargetObject", context.scene, "objects")
        row = box.row()
        row.prop(props, "phonemesShowAdvanced", icon="TRIA_DOWN" if props.phonemesShowAdvanced else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Advanced Settings")
        if props.phonemesShowAdvanced:
            box.label(text="Scale phoneme application:")
            box.prop(props, "phonemesScale")
            box.prop(props, "phonemesAnticipationFrames")

        layout.label(text="Custom Code Callback:")
        box = layout.box()
        box.label(text="Optionally, specify a driver callback we will pass motion capture data and events to:")
        box.prop(props, "tickCallback")
        box.prop(props, "tickUserData")

        layout.label(text="Input Mode Settings:")
        box = layout.box()
        row = box.row(align=True)
        row.prop(props, "inputMode", expand=True)
        if props.inputMode == "live":
            box.label(text="Live input settings:")
            box.prop(props, "websocketURI")
            row = box.row(align=False)
            row.alignment = 'LEFT'
            if yerface_blender.PreviewModal.YerFacePreviewStartOperator.isPreviewRunning(None):
                row.operator("wm.yerface_preview_stop")
            else:
                row.operator("wm.yerface_preview_start")
        else:
            box.label(text="File input settings:")
            box.prop(props, "inputFilePath")
            box.prop(props, "importStartFrame")
            box.prop(props, "samplingMode")
            row = box.row(align=False)
            row.alignment = 'LEFT'
            row.operator("yerface.do_import")
