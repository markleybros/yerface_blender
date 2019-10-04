
bl_info = {
    'name': 'YerFace: Blender Plugin',
    'author': 'Alex Markley',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': 'TBD',
    'description': 'Blender integration with the YerFace performance capture tool.',
    'category': 'Animation'
}

import bpy
import sys
import os
from importlib import reload

def syspathMunge(newpath):
    if newpath not in sys.path:
        sys.path.append(newpath)

syspathMunge(os.path.abspath(os.path.dirname(__file__) + "/vendor"))

import yerface_blender.AddonProps
reload(yerface_blender.AddonProps)
import yerface_blender.DriverUtilities
reload(yerface_blender.DriverUtilities)
import yerface_blender.FIFOReader
reload(yerface_blender.FIFOReader)
import yerface_blender.ImportOperator
reload(yerface_blender.ImportOperator)
import yerface_blender.PanelInterface
reload(yerface_blender.PanelInterface)
import yerface_blender.PreviewModal
reload(yerface_blender.PreviewModal)
import yerface_blender.SceneUtilities
reload(yerface_blender.SceneUtilities)
import yerface_blender.WebsocketReader
reload(yerface_blender.WebsocketReader)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.yerFaceBlenderProperties = bpy.props.PointerProperty(type=yerface_blender.AddonProps.YerFaceBlenderProperties)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.yerFaceBlenderProperties
