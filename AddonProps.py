
import bpy

class YerFaceBlenderProperties(bpy.types.PropertyGroup):
    websocketURI = bpy.props.StringProperty(
        name = "Websocket URI",
        default = "ws://localhost:9002"
    )
