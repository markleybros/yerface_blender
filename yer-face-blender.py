
bl_info = {
    'name': 'Yer Face: Blender Plugin',
    'author': 'Alex Markley',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': 'TBD',
    'description': 'Blender integration with the Yer Face performance capture tool.',
    'category': 'Animation'
}

import bpy

isPreviewRunning = False
myPreviewTimer = None

class YerFacePreviewStartOperator(bpy.types.Operator):
    bl_idname = "wm.yerface_preview_start"
    bl_label = "YerFace Preview Start"
    bl_description = "Start previewing data from the Yer Face performance capture tool."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        global isPreviewRunning
        if event.type == 'ESC' or not isPreviewRunning:
            return self.cancel(context)
        if event.type == 'TIMER':
            print("TICK")
        return {'PASS_THROUGH'}

    def execute(self, context):
        global isPreviewRunning
        global myPreviewTimer
        isPreviewRunning = True
        context.window_manager.modal_handler_add(self)
        myPreviewTimer = context.window_manager.event_timer_add(1/context.scene.render.fps, context.window)
        print("STARTED TIMER")
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        global isPreviewRunning
        global myPreviewTimer
        if isPreviewRunning:
            isPreviewRunning = False
            context.window_manager.event_timer_remove(myPreviewTimer)
            print("CANCELLED TIMER")
        return {'CANCELLED'}


class YerFacePreviewStopOperator(bpy.types.Operator):
    bl_idname = "wm.yerface_preview_stop"
    bl_label = "YerFace Preview Stop"
    bl_description = "Stop previewing data from the Yer Face performance capture tool."
    bl_options = {'REGISTER'}

    def execute(self, context):
        YerFacePreviewStartOperator.cancel(None, context)
        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    print("REGISTERED")


def unregister():
    bpy.utils.unregister_module(__name__)
    print("UNREGISTERED")
