import bpy
from .trimmer import Trimmer

class TrimmerUI(bpy.types.Panel):
    bl_label = "Trimmer"
    bl_idname = "TRIMMER_PT_UI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Trimmer"

    def draw(self, context):
        layout = self.layout

        trims = context.scene.trim_collection

        if len(trims) > 0:
            row = layout.row()
            row.label(text="Trims:")

        for index, trim in enumerate(trims):
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

class TrimOptions(bpy.types.PropertyGroup):
    items = [
        ('FILL', "Fill", "Fill the trim"),
        ('FIT_X', "Fit X", "Fit inside the trim horisontally"),
        ('FIT_Y', "Fit Y", "Fit inside the trim vertically"),
        ('FIT', "Fit", "Fit inside the trim"),
    ]

    fitOptions: bpy.props.EnumProperty(
        name = "",
        description = "Select how to map the selected face(s) to the trim",
        items = items,
        default = 'FILL'
    )

    rotation: bpy.props.FloatProperty(
        name = "Rotation",
        description = "Rotate the UV",
        default = 0.0,
        min = 0.0,
        max =360.0,
        update = lambda self, context: print("rotation lambda")#update_position(self, context, 'x')
    )

    posX: bpy.props.FloatProperty(
        name = "X Position",
        description = "Move the UV along X-axis",
        default = 0.0,
        min = -10.0,
        max = 10.0,
        update = lambda self, context: print("posX lambda")#update_position(self, context, 'x')
    )

    posY: bpy.props.FloatProperty(
        name = "Y Position",
        description = "Move the UV along Y-axis",
        default = 0.0,
        min = -10.0,
        max = 10.0,
        update = lambda self, context: print("posY lambda")#update_position(self, context, 'y')
    )

class ApplyTrimSettings(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "TRIMMER_PT_APPLY_TRIM_SETTINGS"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Trimmer"

    def drawFillSettings(self, context):
        pass

    def drawFitSettings(self, context):
        pass

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text="Trim fitting options:")
        layout.prop(scene.trim_options, "fitOptions")
        layout.row()

        fitOption = scene.trim_options.fitOptions
        if fitOption == 'FIT_X' or fitOption == 'FIT':
            layout.label(text="posY:")
            layout.prop(scene.trim_options, "posY")
        if fitOption == 'FIT_Y' or fitOption == 'FIT':
            layout.label(text="posX:")
            layout.prop(scene.trim_options, "posX")

class AbstractOperator(bpy.types.Operator):
    bl_idname = "object.ao"
    bl_label = "Abstract Operator"

    button_action: bpy.props.StringProperty(default="TEST")
    index: bpy.props.IntProperty()

    def execute(self, context):
        if self.button_action == 'APPLY_TEXTURE':
            Trimmer.apply_texture(context, self)
        elif self.button_action == 'ADD_TRIM':
            Trimmer.add_trim(context, self)
        elif self.button_action == 'DELETE_TRIM':
            Trimmer.delete_trim(context, self)
        elif self.button_action == 'MIRROR_COORDS':
            Trimmer.mirror_coords(context, self)
        elif self.button_action == 'CONFIRM_TRIM':
            ApplyTrimSettings.confirmTrim()
        else:
            raise Exception(f"Unknown button action: {self.button_action}")
        return {'FINISHED'}
