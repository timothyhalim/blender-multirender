import bpy
from bpy.types import Panel, UIList
from bpy.utils import register_class, unregister_class

class MultiRender_PT_Panel(Panel):
    """Creates a Panel in the Properties window"""
    bl_label = "Multi Render"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render"

    @classmethod
    def poll(cls, context):
        registered_scenes = sorted((scene.scene for scene in context.window_manager.render_property if scene != None), key= lambda k: k.name if k else "")
        file_scenes = sorted((scene for scene in bpy.data.scenes), key= lambda k: k.name)
        if registered_scenes != file_scenes:
            # Update Scene List
            context.window_manager.render_property.clear()
            for scene in bpy.data.scenes:
                render = context.window_manager.render_property.add()
                render.scene = scene
        
        return True

    def draw(self, context):
        layout = self.layout
        
        layout.template_list(
                "MultiRender_UL_List", 
                "", 
                context.window_manager , 
                "render_property", 
                context.window_manager , 
                "render_index")
                
        layout.prop(context.window_manager, "save_image", text="Save Image")
        row = layout.row()
        row.operator('renderutils.renderscenes', text="Render Scenes")
        row.operator('render.view_show', text="", icon="WINDOW")

class MultiRender_UL_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=f"{item.name}")
            layout.prop(item, "renderable", text="", toggle=True, icon="RESTRICT_RENDER_OFF" if item.renderable else "RESTRICT_RENDER_ON")

        elif self.layout_type in {'GRID'}:
            pass

def register():
    register_class(MultiRender_PT_Panel)
    register_class(MultiRender_UL_List)

def unregister():
    unregister_class(MultiRender_PT_Panel)
    unregister_class(MultiRender_UL_List)