import bpy
from . import trimmer

class TrimmerSettings(bpy.types.Panel):
    bl_label = "Trimmer Settings"
    bl_idname = "TRIMMER_SETTINGS"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Trimmer"

    @classmethod
    def get_instance(self):
        """Get the instance of the panel (singleton)."""
        return self

    def draw(self, context):
        layout = self.layout
        layout.operator("object.ao", text="Test").button_action = "TEST"

class Trimmer(bpy.types.Panel):
    bl_label = "Trimmer"
    bl_idname = "TRIMMER"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Trimmer"

    # Shared data for the panel
    saved_uv_coords = []
    saved_image_path = ""

    @classmethod
    def get_instance(cls):
        """Get the instance of the panel (singleton)."""
        return cls

    def draw(self, context):
        layout = self.layout
        layout.label(text="Set Trims")
        layout.operator("object.ao", text="Set Texture").button_action = "SET_TEXTURE"
        layout.label(text="Alternative Set Trims")
        row = layout.row() 
        row.operator("object.ao", text="Trim 0").button_action = "SET_TEXTURE"
        row.operator("object.ao", text="", icon='GREASEPENCIL').button_action = "TEST"
        row.operator("object.ao", text="", icon='X').button_action = "TEST"
        layout.operator("object.ao", text="Apply Texture").button_action = "APPLY_TEXTURE"


class AbstractOperator(bpy.types.Operator):
    bl_idname = "object.ao"
    bl_label = "Abstract Operator"

    button_action: bpy.props.StringProperty()

    def execute(self, context):
        t = Trimmer.get_instance()
        if self.button_action == "TEST":
            trimmer.test(self, context, t)
        elif self.button_action == "SET_TEXTURE":
            trimmer.set_texture(self, context, t)
        elif self.button_action == "APPLY_TEXTURE":
            trimmer.apply_texture(self, context, t)
        return {'FINISHED'}
