
import bpy

yerFaceAxisMapEnumItems = [
    ('p.x', '+X', "Positive X Axis", 0),
    ('n.x', '-X', "Negative X Axis", 1),
    ('p.y', '+Y', "Positive Y Axis", 2),
    ('n.y', '-Y', "Negative Y Axis", 3),
    ('p.z', '+Z', "Positive Z Axis", 4),
    ('n.z', '-Z', "Negative Z Axis", 5),
    ('p._', 'N/A', "Disabled", 6)
]

yerFaceInputModeItems = [
    ('live', 'Live/Network Input', "Live Websocket Input", 0),
    ('file', 'File Input', "Perfcap File Input", 1)
]

yerFaceSamplingModeItems = [
    ('first', 'First', "Take the first sample for each frame", 0),
    ('last', 'Last', "Take the last sample for each frame", 1),
    ('average', 'Average', "Average samples within a frame", 2)
]

class YerFaceBlenderProperties(bpy.types.PropertyGroup):
    translationTargetObject = bpy.props.StringProperty(
        name = "Object",
        default = "")
    translationTargetBone = bpy.props.StringProperty(
        name = "Bone",
        default = "")
    translationShowAdvanced = bpy.props.BoolProperty(default=False)
    translationScale = bpy.props.FloatProperty(
        name = "Scale",
        default = 0.00328084, # millimeters to feet
        min = 0.0)
    translationScaleX = bpy.props.FloatProperty(
        name = "X",
        default = 1.0,
        min = 0.0)
    translationScaleY = bpy.props.FloatProperty(
        name = "Y",
        default = 1.0,
        min = 0.0)
    translationScaleZ = bpy.props.FloatProperty(
        name = "Z",
        default = 1.0,
        min = 0.0)
    translationAxisMapX = bpy.props.EnumProperty(
        items = yerFaceAxisMapEnumItems,
        name = "Map X",
        default = "p.x")
    translationAxisMapY = bpy.props.EnumProperty(
        items = yerFaceAxisMapEnumItems,
        name = "Map Y",
        default = "p.y")
    translationAxisMapZ = bpy.props.EnumProperty(
        items = yerFaceAxisMapEnumItems,
        name = "Map Z",
        default = "p.z")
    translationAnticipationFrames = bpy.props.IntProperty(
        name = "Anticipate Motion N Frames Ago",
        description = "If we're holding a property via deduplicated keyframes, but the property is about to change, how many frames ago should we anticipate this.",
        min = 1,
        default = 15)

    rotationTargetObject = bpy.props.StringProperty(
        name = "Object",
        default = "")
    rotationTargetBone = bpy.props.StringProperty(
        name = "Bone",
        default = "")
    rotationShowAdvanced = bpy.props.BoolProperty(default=False)
    rotationScale = bpy.props.FloatProperty(
        name = "Scale",
        default = 1.0,
        min = 0.0)
    rotationScaleX = bpy.props.FloatProperty(
        name = "X",
        default = 1.0,
        min = 0.0)
    rotationScaleY = bpy.props.FloatProperty(
        name = "Y",
        default = 1.0,
        min = 0.0)
    rotationScaleZ = bpy.props.FloatProperty(
        name = "Z",
        default = 1.0,
        min = 0.0)
    rotationAxisMapX = bpy.props.EnumProperty(
        items = yerFaceAxisMapEnumItems,
        name = "Map X",
        default = "p.x")
    rotationAxisMapY = bpy.props.EnumProperty(
        items = yerFaceAxisMapEnumItems,
        name = "Map Y",
        default = "p.y")
    rotationAxisMapZ = bpy.props.EnumProperty(
        items = yerFaceAxisMapEnumItems,
        name = "Map Z",
        default = "p.z")
    rotationAnticipationFrames = bpy.props.IntProperty(
        name = "Anticipate Motion N Frames Ago",
        description = "If we're holding a property via deduplicated keyframes, but the property is about to change, how many frames ago should we anticipate this.",
        min = 1,
        default = 15)

    faceArmatureObject = bpy.props.StringProperty(
        name = "Rig",
        default = "")
    faceBoneTranslationScale = bpy.props.FloatProperty(
        name = "Scale",
        default = 0.01,
        min = 0.0)
    faceShowAdvanced = bpy.props.BoolProperty(default=False)
    faceBoneAxisMapX = bpy.props.EnumProperty(
        items = yerFaceAxisMapEnumItems,
        name = "Map X",
        default = "p.x")
    faceBoneAxisMapY = bpy.props.EnumProperty(
        items = yerFaceAxisMapEnumItems,
        name = "Map Y",
        default = "p.y")
    faceBoneAxisMapZ = bpy.props.EnumProperty(
        items = yerFaceAxisMapEnumItems,
        name = "Map Z",
        default = "p.z")
    faceAnticipationFrames = bpy.props.IntProperty(
        name = "Anticipate Motion N Frames Ago",
        description = "If we're holding a property via deduplicated keyframes, but the property is about to change, how many frames ago should we anticipate this.",
        min = 1,
        default = 15)

    phonemesTargetObject = bpy.props.StringProperty(
        name = "Object",
        default = "")
    phonemesShowAdvanced = bpy.props.BoolProperty(default=False)
    phonemesScale = bpy.props.FloatProperty(
        name = "Scale",
        default = 1.0,
        min = 0.0)
    phonemesAnticipationFrames = bpy.props.IntProperty(
        name = "Anticipate Motion N Frames Ago",
        description = "If we're holding a property via deduplicated keyframes, but the property is about to change, how many frames ago should we anticipate this.",
        min = 1,
        default = 1)

    tickCallback = bpy.props.StringProperty(
        name = "Tick Callback",
        default = "")
    tickUserData = bpy.props.StringProperty(
        name = "User Data",
        default = "")

    inputMode = bpy.props.EnumProperty(
        items = yerFaceInputModeItems,
        name = "Active Input Mode",
        default = "live")
    samplingMode = bpy.props.EnumProperty(
        items = yerFaceSamplingModeItems,
        name = "Keyframe Sampling Mode",
        default = "average")
    websocketURI = bpy.props.StringProperty(
        name = "Websocket URI",
        default = "ws://localhost:9002")
    inputFilePath = bpy.props.StringProperty(
        name="Perfcap JSON File",
        description="Exported performance capture data from YerFace!",
        subtype="FILE_PATH")
    importStartFrame = bpy.props.IntProperty(
        name = "Start Frame",
        default = 1)
