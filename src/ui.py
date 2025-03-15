import bpy
from .trimmer import Trimmer

class TrimmerUI(bpy.types.Panel):
    bl_label = "Trimmer"
    bl_idname = "TRIMMER_PT_UI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Trimmer"

    @classmethod
    def get_instance(self):
        return self

    def draw(self, context):
        layout = self.layout
        layout.operator("object.ao", text="Test").button_action = "TEST"
        layout.row()

        for index, trim in enumerate(context.scene.trim_collection):
            row = layout.row()
            row.prop(trim, "name", text="")
            
            op = row.operator("object.ao", text="Apply")
            op.index = index
            op.button_action = "APPLY_TEXTURE"
            
            op = row.operator("object.ao", text="", icon="X")
            op.index = index
            op.button_action = "DELETE_TRIM"

        op = layout.operator("object.ao", text="Add trim")
        op.button_action = "ADD_TRIM"

class AbstractOperator(bpy.types.Operator):
    bl_idname = "object.ao"
    bl_label = "Abstract Operator"

    button_action: bpy.props.StringProperty(default="TEST")
    index: bpy.props.IntProperty()

    def execute(self, context):
        if self.button_action == "TEST":
            Trimmer.test(context, self)
        elif self.button_action == "APPLY_TEXTURE":
            Trimmer.apply_texture(context, self)
        elif self.button_action == "ADD_TRIM":
            Trimmer.add_trim(context, self)
        elif self.button_action == "DELETE_TRIM":
            Trimmer.delete_trim(context, self)
        return {'FINISHED'}
