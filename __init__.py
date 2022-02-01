
bl_info = {
    'name': 'YerFace: Blender Plugin',
    'author': 'Alex Markley',
    'version': (0, 1, 0),
    'blender': (2, 80, 0),
    'location': 'FIXME',
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

from . import AddonProps
reload(AddonProps)
from . import DriverUtilities
reload(DriverUtilities)
from . import FIFOReader
reload(FIFOReader)
from . import ImportOperator
reload(ImportOperator)
from . import PanelInterface
reload(PanelInterface)
from . import PreviewModal
reload(PreviewModal)
from . import SceneUtilities
reload(SceneUtilities)
from . import WebsocketReader
reload(WebsocketReader)

classes = (
    ImportOperator.YERFACE_OT_ImportFromFile,
    PreviewModal.YERFACE_OT_PreviewStartOperator,
    PreviewModal.YERFACE_OT_PreviewStopOperator,
    PanelInterface.YERFACE_PT_ToolsPanel,
)

def register():
    bpy.utils.register_class(AddonProps.YerFaceBlenderProperties)
    bpy.types.Scene.yerFaceBlenderProperties = bpy.props.PointerProperty(type=AddonProps.YerFaceBlenderProperties)
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.yerFaceBlenderProperties
    bpy.utils.unregister_class(AddonProps.YerFaceBlenderProperties)
