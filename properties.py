from bpy.types import PropertyGroup, Scene, WindowManager
from bpy.props import PointerProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty
from bpy.utils import register_class, unregister_class

class Render_Property(PropertyGroup):
    def get_name(self):
        return getattr(self.scene, "name", "")
        
    def get_renderable(self):
        return getattr(self.scene, "renderable", True)

    def set_renderable(self, value):
        self.scene.renderable = value

    scene : PointerProperty(type=Scene)
    name : StringProperty(get=get_name)
    renderable : BoolProperty(default=True, get=get_renderable, set=set_renderable)

def register():
    register_class(Render_Property)
    
    Scene.renderable = BoolProperty(default=True)
    WindowManager.render_property = CollectionProperty(type=Render_Property)
    WindowManager.render_index = IntProperty()
    WindowManager.save_image = BoolProperty(default=True)

def unregister():
    unregister_class(Render_Property)

    del Scene.renderable
    del WindowManager.render_property
    del WindowManager.render_index
        