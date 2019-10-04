
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

        props = context.scene.yerFaceBlenderProperties

        fps = context.scene.render.fps / context.scene.render.fps_base
        time_step = 1/fps

        isPreviewRunning = True
        myReader = yerface_blender.WebsocketReader.YerFaceWebsocketReader(props.websocketURI)
        myReader.openWebsocket()
        myUpdater = yerface_blender.SceneUtilities.YerFaceSceneUpdater(context, myReader, fps)

        if props.tickCallback != "":
            tickProps = {
                'userData': props.tickUserData,
                'resetState': True,
                'perfcapPacket': {},
                'insertKeyframes': False,
                'currentFrameNumber': None,
                'flushLastFrame': False,
                'framesPerSecond': fps
            }
            bpy.app.driver_namespace[props.tickCallback](tickProps)

        context.window_manager.modal_handler_add(self)

        myPreviewTimer = context.window_manager.event_timer_add(time_step, context.window)
        print("STARTED TIMER w/Time Step: ", time_step)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        global isPreviewRunning
        global myPreviewTimer
        global myReader
        if isPreviewRunning:
            isPreviewRunning = False
            context.window_manager.event_timer_remove(myPreviewTimer)
            myReader.closeWebsocket()
            myReader = None
            print("CANCELLED TIMER")
        return {'CANCELLED'}

    def isPreviewRunning(self):
        global isPreviewRunning
        return isPreviewRunning

class YerFacePreviewStopOperator(bpy.types.Operator):
    bl_idname = "wm.yerface_preview_stop"
    bl_label = "YerFace Preview Stop"
    bl_description = "Stop previewing data from the Yer Face performance capture tool."
    bl_options = {'REGISTER'}

    def execute(self, context):
        YerFacePreviewStartOperator.cancel(None, context)
        return {'FINISHED'}
