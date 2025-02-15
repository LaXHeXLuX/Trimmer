import bpy
from .trimmer import Trimmer

class TrimmerSettings(bpy.types.Panel):
    bl_label = "Trimmer Settings"
    bl_idname = "TRIMMER_SETTINGS"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Trimmer"

    @classmethod
    def get_instance(self):
        return self

    def draw(self, context):
        layout = self.layout
        layout.operator("object.ao", text="Test").button_action = "TEST"

class TrimmerUI(bpy.types.Panel):
    bl_label = "Trimmer"
    bl_idname = "TRIMMER"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Trimmer"

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

    button_action: bpy.props.StringProperty(default="TEST")

    def execute(self, context):
        if self.button_action == "TEST":
            Trimmer.test(context, self)
        elif self.button_action == "SET_TEXTURE":
            Trimmer.set_texture(context, self)
        elif self.button_action == "APPLY_TEXTURE":
            Trimmer.apply_texture(context, self)
        return {'FINISHED'}
