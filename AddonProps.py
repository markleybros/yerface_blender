
import bpy

class YerFaceBlenderProperties(bpy.types.PropertyGroup):
    translationTargetObject = bpy.props.StringProperty(
        name = "Object",
        default = "")
    translationTargetBone = bpy.props.StringProperty(
        name = "Bone",
        default = "")
    rotationTargetObject = bpy.props.StringProperty(
        name = "Object",
        default = "")
    rotationTargetBone = bpy.props.StringProperty(
        name = "Bone",
        default = "")
    faceArmatureObject = bpy.props.StringProperty(
        name = "Rig",
        default = "")
    translationScale = bpy.props.FloatProperty(
        name = "Scale",
        default = 0.00328084, # millimeters to feet
        min = 0.0)
    websocketURI = bpy.props.StringProperty(
        name = "Websocket URI",
        default = "ws://localhost:9002")
