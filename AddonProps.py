
import bpy

class YerFaceBlenderProperties(bpy.types.PropertyGroup):
    translationTargetObject = bpy.props.StringProperty(
        name = "Motion Target Object",
        default = "")
    translationTargetBone = bpy.props.StringProperty(
        name = "Motion Target Bone",
        default = "")
    rotationTargetObject = bpy.props.StringProperty(
        name = "Rotation Target Object",
        default = "")
    rotationTargetBone = bpy.props.StringProperty(
        name = "Rotation Target Bone",
        default = "")
    faceArmatureObject = bpy.props.StringProperty(
        name = "Face Armature",
        default = "")
    websocketURI = bpy.props.StringProperty(
        name = "Websocket URI",
        default = "ws://localhost:9002")
