
import bpy

import yerface_blender.SceneUtilities
import yerface_blender.WebsocketReader

isPreviewRunning = False
myPreviewTimer = None
myReader = None
myUpdater = None

class YerFacePreviewStartOperator(bpy.types.Operator):
    bl_idname = "wm.yerface_preview_start"
    bl_label = "YerFace Preview Start"
    bl_description = "Start previewing data from the Yer Face performance capture tool."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        global isPreviewRunning
        global myUpdater
        if event.type == 'ESC' or not isPreviewRunning:
            return self.cancel(context)
        if event.type == 'TIMER':
            myUpdater.runUpdate()
        return {'PASS_THROUGH'}

    def execute(self, context):
        global isPreviewRunning
        global myPreviewTimer
        global myReader
        global myUpdater
        isPreviewRunning = True
        if myReader is None:
            myReader = yerface_blender.WebsocketReader.YerFaceWebsocketReader()
        myReader.openWebsocket()
        myUpdater = yerface_blender.SceneUtilities.YerFaceSceneUpdater(context, myReader)
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
            myReader.closeWebsocket()
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
