import bpy
from .trimmer import Trimmer, TrimmerException

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

        for i in range(len(trims)):
            row = layout.row()
            row.prop(trims[i], "name", text="")
            
            AbstractOperator.init(row, 'APPLY_TEXTURE', index=i)
            AbstractOperator.init(row, 'DELETE_TRIM', index=i)

        AbstractOperator.init(layout, 'ADD_TRIM')

    @classmethod
    def deleteTrim(cls, context, index):
        trims = context.scene.trim_collection
        if 0 <= index < len(trims):
            trims.remove(index)
        else:
            raise IndexError(f"Index {index} is out of range for the trim collection (length {len(trims)}).")

class TrimOptions(bpy.types.PropertyGroup):
    items = [
        ('FILL', "Fill", "Fill the trim"),
        ('FIT_X', "Fit X", "Fit inside the trim horisontally"),
        ('FIT_Y', "Fit Y", "Fit inside the trim vertically"),
        ('FIT', "Fit", "Fit inside the trim"),
    ]

    updatesOff: bpy.props.BoolProperty(default=False, options={'HIDDEN', 'SKIP_SAVE'}) # type: ignore

    def reset(self, prop):
        default = self.__class__.bl_rna.properties[prop].default
        self.updatesOff = True
        setattr(self, prop, default)
        self.updatesOff = False

    def clear(self):
        for prop in ['rotation']:
            if prop in self.__class__.bl_rna.properties:
                self.reset(prop)

    previousFitOptionValue: bpy.props.StringProperty(default='FILL') # type: ignore

    def show_error(self, context, message):
        def draw(self, context):
            self.layout.label(text=message)

        context.window_manager.popup_menu(draw, title="Error", icon='ERROR')

    def fitOptionUpdate(self, context):
        if self.previousFitOptionValue == self.fitOptions or Trimmer.currentTrim == None:
            self.previousFitOptionValue = self.fitOptions
            return
        try:
            Trimmer.apply_texture(context, Trimmer.currentTrim)
            self.previousFitOptionValue = self.fitOptions
        except TrimmerException as te:
            self.fitOptions = self.previousFitOptionValue
            self.show_error(context, str(te))

    fitOptions: bpy.props.EnumProperty(
        name = "",
        description = "Select how to map the selected face(s) to the trim",
        items = items,
        default = 'FILL',
        update = fitOptionUpdate
    ) # type: ignore

    def rotationUpdate(self, context):
        if self.updatesOff:
            return
        Trimmer.rotate_trim(context, degrees = self.rotation)

    rotation: bpy.props.FloatProperty(
        name = "Rotation",
        description = "Rotate the UV",
        default = 0.0,
        update = rotationUpdate
    ) # type: ignore

class ApplyTrimSettings(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "TRIMMER_PT_APPLY_TRIM_SETTINGS"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Trimmer"
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.trim_collection) > 0
    
    def drawFitOption(self, context):
        layout = self.layout
        layout.label(text="Trim fitting options:")
        layout.prop(context.scene.trim_options, "fitOptions")

    def drawFillSettings(self, context):
        layout = self.layout
        actionSettingsRow = layout.row()
        
        AbstractOperator.init(actionSettingsRow, 'MIRROR_TRIM')
        AbstractOperator.init(actionSettingsRow, 'ROTATE_TRIM')

        layout.row()
        AbstractOperator.init(layout, 'CONFIRM_TRIM')

    def drawFitSettings(self, context):
        layout = self.layout
        actionSettingsRow = layout.row()

        AbstractOperator.init(actionSettingsRow, 'MIRROR_TRIM')
        subRow = actionSettingsRow.row(align=True)
        AbstractOperator.init(subRow, 'ROTATE_TRIM_90')
        subRow.prop(context.scene.trim_options, "rotation")

        layout.row()
        AbstractOperator.init(layout, 'CONFIRM_TRIM')

    def draw(self, context):
        self.drawFitOption(context)
        if Trimmer.currentApplyOption == 'FILL':
            self.drawFillSettings(context)
        elif Trimmer.currentApplyOption in ['FIT', 'FIT_X', 'FIT_Y']:
            self.drawFitSettings(context)

    @staticmethod
    def confirmTrim():
        bpy.context.scene.trim_options.clear()
        Trimmer.clear()

class AbstractOperator(bpy.types.Operator):
    bl_idname = "trimmer.ao"
    bl_label = ""

    button_action: bpy.props.StringProperty(default="TEST") # type: ignore
    index: bpy.props.IntProperty() # type: ignore

    def init(layout, button_action, index=None):
        texts = {
            'APPLY_TEXTURE': "Apply",
            'ADD_TRIM': "Add trim",
            'DELETE_TRIM': None,
            'MIRROR_TRIM': "Mirror",
            'ROTATE_TRIM': "Rotate",
            'ROTATE_TRIM_90': '90°',
            'CONFIRM_TRIM': "Confirm trim"
        }
        icons = {
            'APPLY_TEXTURE': 'NONE',
            'ADD_TRIM': 'NONE',
            'DELETE_TRIM': 'X',
            'MIRROR_TRIM': 'MOD_MIRROR',
            'ROTATE_TRIM': 'FILE_REFRESH',
            'ROTATE_TRIM_90': 'FILE_REFRESH',
            'CONFIRM_TRIM': 'NONE'
        }

        if button_action in ['APPLY_TEXTURE', 'DELETE_TRIM']:
            if index == None:
                raise Exception(f"Button {button_action} needs an index!")

        ao_button = layout.operator("trimmer.ao", text=texts[button_action], icon=icons[button_action])
        ao_button.button_action = button_action

        if button_action in ['APPLY_TEXTURE', 'DELETE_TRIM']:
            ao_button.index = index

        return ao_button

    @classmethod
    def description(cls, context, properties):
        descriptions = {
            'APPLY_TEXTURE': "Apply the texture",
            'ADD_TRIM': "Add a new trim",
            'DELETE_TRIM': "Delete the trim",
            'MIRROR_TRIM': "Mirror the trim UV",
            'ROTATE_TRIM': "Rotate the trim UV",
            'ROTATE_TRIM_90': "Rotate the   UV by 90 degrees",
            'CONFIRM_TRIM': "Confirm trim placement"
        }

        return descriptions[properties.button_action]

    def execute(self, context):
        try:
            if self.button_action == 'APPLY_TEXTURE':
                ApplyTrimSettings.confirmTrim()
                Trimmer.apply_texture(context, context.scene.trim_collection[self.index])
            elif self.button_action == 'ADD_TRIM':
                Trimmer.add_trim(context)
            elif self.button_action == 'DELETE_TRIM':
                TrimmerUI.deleteTrim(context, self.index)
            elif self.button_action == 'MIRROR_TRIM':
                Trimmer.mirror_trim(context)
            elif self.button_action == 'ROTATE_TRIM':
                Trimmer.rotate_trim(context)
            elif self.button_action == 'ROTATE_TRIM_90':
                trim_options = context.scene.trim_options
                trim_options.rotation = (trim_options.rotation - 90) % 360 # wrap around after 360
            elif self.button_action == 'CONFIRM_TRIM':
                ApplyTrimSettings.confirmTrim()
            else:
                raise Exception(f"Unknown button action: {self.button_action}")
            return {'FINISHED'}
        except TrimmerException as te:
            self.report({'ERROR'}, str(te))
            return {'CANCELLED'}