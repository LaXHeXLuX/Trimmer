import bpy
from .trimmer import Trimmer, TrimmerException, Trimsheet

class TrimmerUI(bpy.types.Panel):
    bl_label = "Trimmer"
    bl_idname = "TRIMMER_PT_UI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Trimmer"

    def draw(self, context):
        layout = self.layout

        trimsheets = context.scene.trimsheet_collection
        row = layout.row()

        if len(trimsheets) > 0:
            row = layout.row()
            row.label(text="Trimsheets:")

        for i in range(len(trimsheets)):
            self.draw_trimsheet(layout, i, trimsheets[i])

        AddTrimSheetButton.init(layout)

    def draw_trimsheet(self, layout, index, trimsheet):
        box = layout.box()
        row = box.row()
        row.label(text="Trimsheet:")
        row.prop(trimsheet, "name", text="")
        DeleteTrimSheetButton.init(row, index)
        box.separator()

        trims = trimsheet.trims
        for i in range(len(trims)):
            self.draw_trim(box, index, i, trims)

        AddTrimButton.init(box, index)

    def draw_trim(self, layout, index, i, trims):
        row = layout.row()
        row.prop(trims[i], "name", text="")
        
        ApplyTrimButton.init(row, index, i)

        innerRow = row.row(align=True)
        ReorderTrimButton.init(innerRow, index, i, up=True)
        ReorderTrimButton.init(innerRow, index, i, up=False)

        DeleteTrimButton.init(row, index, i)


    @staticmethod
    def delete_trim(context, trimsheet_index, trim_index):
        trimsheets = context.scene.trimsheet_collection 
        trimsheets[trimsheet_index].trims.remove(trim_index)

    @staticmethod
    def delete_trimsheet(context, trimsheet_index):
        context.scene.trimsheet_collection.remove(trimsheet_index)

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
        trimsheets = context.scene.trimsheet_collection
        for trimsheet in trimsheets:
            if len(trimsheet.trims) > 0:
                return True
        return False
    
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

class AddTrimButton(bpy.types.Operator):
    bl_idname = "trimmer.add_trim"
    bl_label = ""

    trimsheet_index: bpy.props.IntProperty() # type: ignore

    def init(layout, index=None):
        add_trim_button = layout.operator("trimmer.add_trim", text="Add trim", icon='NONE')
        add_trim_button.trimsheet_index = index

        return add_trim_button
    
    @classmethod
    def description(cls, context, properties):
        return "Add a new trim"
    
    def execute(self, context):
        try:
            Trimmer.add_trim(context, self.trimsheet_index)
            return {'FINISHED'}
        except TrimmerException as te:
            self.report({'ERROR'}, str(te))
            return {'CANCELLED'}

class DeleteTrimButton(bpy.types.Operator):
    bl_idname = "trimmer.delete_trim"
    bl_label = ""

    trimsheet_index: bpy.props.IntProperty() # type: ignore
    trim_index: bpy.props.IntProperty() # type: ignore

    def init(layout, trimsheet_index, trim_index):
        delete_trim_button = layout.operator("trimmer.delete_trim", text=None, icon='X')
        delete_trim_button.trimsheet_index = trimsheet_index
        delete_trim_button.trim_index = trim_index

        return delete_trim_button
    
    @classmethod
    def description(cls, context, properties):
        return "Delete the trim"
    
    def execute(self, context):
        try:
            TrimmerUI.delete_trim(context, self.trimsheet_index, self.trim_index)
            return {'FINISHED'}
        except TrimmerException as te:
            self.report({'ERROR'}, str(te))
            return {'CANCELLED'}

class ApplyTrimButton(bpy.types.Operator):
    bl_idname = "trimmer.apply_trim"
    bl_label = ""

    trimsheet_index: bpy.props.IntProperty() # type: ignore
    trim_index: bpy.props.IntProperty() # type: ignore

    def init(layout, trimsheet_index, trim_index):
        apply_trim_button = layout.operator("trimmer.apply_trim", text="Apply", icon='NONE')
        apply_trim_button.trimsheet_index = trimsheet_index
        apply_trim_button.trim_index = trim_index

        return apply_trim_button
    
    @classmethod
    def description(cls, context, properties):
        return "Apply the texture"
    
    def execute(self, context):
        try:
            ApplyTrimSettings.confirmTrim()
            Trimmer.apply_texture(context, context.scene.trimsheet_collection[self.trimsheet_index].trims[self.trim_index])
            return {'FINISHED'}
        except TrimmerException as te:
            self.report({'ERROR'}, str(te))
            return {'CANCELLED'}

class ReorderTrimButton(bpy.types.Operator):
    bl_idname = "trimmer.reorder_trim"
    bl_label = ""

    trimsheet_index: bpy.props.IntProperty() # type: ignore
    trim_index: bpy.props.IntProperty() # type: ignore
    up: bpy.props.BoolProperty() # type: ignore

    def init(layout, trimsheet_index, trim_index, up):
        icon = {
            True: 'TRIA_UP',
            False: 'TRIA_DOWN'
        }

        reorder_trim_button = layout.operator("trimmer.reorder_trim", text=None, icon=icon[up])
        reorder_trim_button.trimsheet_index = trimsheet_index
        reorder_trim_button.trim_index = trim_index
        reorder_trim_button.up = up

        return reorder_trim_button
    
    @classmethod
    def description(cls, context, properties):
        description = {
            True: "Move the trim up",
            False: "Move the trim down"
        }

        return description[properties.up]
    
    def execute(self, context):
        try:
            trimsheet = context.scene.trimsheet_collection[self.trimsheet_index]
            trimsheet.moveTrim(self.trim_index, up=self.up)
            return {'FINISHED'}
        except TrimmerException as te:
            self.report({'ERROR'}, str(te))
            return {'CANCELLED'}

class AddTrimSheetButton(bpy.types.Operator):
    bl_idname = "trimmer.add_trimsheet"
    bl_label = ""

    def init(layout):
        add_trimsheet_button = layout.operator("trimmer.add_trimsheet", text="Add trimsheet", icon='NONE')

        return add_trimsheet_button
    
    @classmethod
    def description(cls, context, properties):
        return "Add a new trimsheet"
    
    def execute(self, context):
        try:
            Trimmer.add_trimsheet(context)
            return {'FINISHED'}
        except TrimmerException as te:
            self.report({'ERROR'}, str(te))
            return {'CANCELLED'}

class DeleteTrimSheetButton(bpy.types.Operator):
    bl_idname = "trimmer.delete_trimsheet"
    bl_label = ""
    
    trimsheet_index: bpy.props.IntProperty() # type: ignore

    def init(layout, index=None):
        delete_trimsheet_button = layout.operator("trimmer.delete_trimsheet", text=None, icon='X')
        delete_trimsheet_button.trimsheet_index = index

        return delete_trimsheet_button
    
    @classmethod
    def description(cls, context, properties):
        return "Delete the trimsheet"
    
    def execute(self, context):
        try:
            TrimmerUI.delete_trimsheet(context, self.trimsheet_index)
            return {'FINISHED'}
        except TrimmerException as te:
            self.report({'ERROR'}, str(te))
            return {'CANCELLED'}

class AbstractOperator(bpy.types.Operator):
    bl_idname = "trimmer.ao"
    bl_label = ""

    button_action: bpy.props.StringProperty(default="TEST") # type: ignore

    def init(layout, button_action, index=None):
        texts = {
            'MIRROR_TRIM': "Mirror",
            'ROTATE_TRIM': "Rotate",
            'ROTATE_TRIM_90': '90°',
            'CONFIRM_TRIM': "Confirm trim"
        }
        icons = {
            'MIRROR_TRIM': 'MOD_MIRROR',
            'ROTATE_TRIM': 'FILE_REFRESH',
            'ROTATE_TRIM_90': 'FILE_REFRESH',
            'CONFIRM_TRIM': 'NONE'
        }

        if button_action in []:
            if index == None:
                raise Exception(f"Button {button_action} needs an index!")

        ao_button = layout.operator("trimmer.ao", text=texts[button_action], icon=icons[button_action])
        ao_button.button_action = button_action

        if button_action in []:
            ao_button.index = index

        return ao_button

    @classmethod
    def description(cls, context, properties):
        descriptions = {
            'MIRROR_TRIM': "Mirror the trim UV",
            'ROTATE_TRIM': "Rotate the trim UV",
            'ROTATE_TRIM_90': "Rotate the   UV by 90 degrees",
            'CONFIRM_TRIM': "Confirm trim placement"
        }

        return descriptions[properties.button_action]

    def execute(self, context):
        try:
            if self.button_action == 'MIRROR_TRIM':
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