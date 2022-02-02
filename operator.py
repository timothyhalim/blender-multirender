import bpy
from bpy.utils import register_class, unregister_class
import time
from datetime import timedelta
import logging


log = logging.getLogger("Render")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

class MultiRender_OT_GetScenes(bpy.types.Operator):
    bl_idname = "renderutils.getscenes"
    bl_label = "Get Scenes"
    bl_description = "Get Scenes"

    def execute(self, context):
        context.window_manager.render_property.clear()
        for scene in bpy.data.scenes:
            render = context.window_manager.render_property.add()
            render.scene = scene

        return {'FINISHED'}

class MultiRender_OT_RenderScenes(bpy.types.Operator):
    bl_idname = "renderutils.renderscenes"
    bl_label = "Render Scenes"
    bl_description = "Render Scenes"

    _timer = None
    scene = None
    stop = None
    rendering = None
    original_output = None
    use_file_extension = None
    render_job = []

    def registerCallback(self, context):
        # log.info("Render | Registering Callback")
        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)

        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)

    def unregisterCallback(self, context):
        # log.info("Render | Removing Callback")
        bpy.app.handlers.render_pre.remove(self.pre)
        bpy.app.handlers.render_post.remove(self.post)
        bpy.app.handlers.render_cancel.remove(self.cancelled)
        context.window_manager.event_timer_remove(self._timer)

    def restore(self):
        if self.save_image:
            self.scene.render.filepath = self.original_output
            self.scene.render.use_file_extension = self.use_file_extension

    def backup(self):
        if self.save_image:
            log.info(f"{self.scene.name} | Original Output Path: {self.scene.render.filepath}")
            self.original_output = self.scene.render.filepath
            self.use_file_extension = self.scene.render.use_file_extension

    def pre(self, x, y, **kwargs):
        self.renderStart = time.time()
        self.rendering = True
        self.restore()

        log.info(f"{self.scene.name} | Rendering ")

    def post(self, x, y, **kwargs):
        self.render_job.remove(self.scene)
        self.rendering = False

        log.info(f"{self.scene.name} | Rendering Complete in {timedelta(seconds=round(time.time()-self.renderStart))}")
        
    def cancelled(self, x, y, **kwargs):
        self.stop = True

        log.info(f"Render | Cancelled")

    def execute(self, context):
        print("\n")
        log.info(f"Render | Started")
        self.stop = False
        self.rendering = False
        self.processStartTime = time.time()

        self.registerCallback(context)

        scenes = context.window_manager.render_property
        self.render_job = [scene.scene for scene in scenes if scene.renderable]
        self.frame = context.scene.frame_current
        self.save_image = context.window_manager.save_image

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == 'TIMER':
            if self.stop or len(self.render_job) == 0: 
                self.unregisterCallback(context)
                log.info(f"Render | Job Done in {timedelta(seconds=round(time.time()-self.processStartTime))}")
                print("\n")
                return {"FINISHED"} 

            elif not self.rendering: 
                log.info(f'Render | Job Left: {[scene.name for scene in self.render_job]}')

                self.scene = self.render_job[0]

                self.backup()

                # Set Frame and filepath
                self.scene.frame_set(self.frame)
                context.scene.frame_set(self.frame)

                if self.save_image:
                    render_output = self.scene.render.frame_path(frame=self.frame)
                    log.info(f"{self.scene.name} | Output File: {render_output}")
                    self.scene.render.filepath = render_output
                    self.scene.render.use_file_extension = False
                
                bpy.ops.render.view_show("INVOKE_DEFAULT")
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=self.save_image, scene=self.scene.name)
        
        return {"PASS_THROUGH"}

        
def register():
    register_class(MultiRender_OT_GetScenes)
    register_class(MultiRender_OT_RenderScenes)

def unregister():
    unregister_class(MultiRender_OT_GetScenes)
    unregister_class(MultiRender_OT_RenderScenes)