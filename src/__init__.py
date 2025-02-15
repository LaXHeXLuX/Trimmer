bl_info = {
    "name": "Trimmer",
    "author": "Laas Hendrik Lumberg",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Tool Panel",
    "description": "Allows easier positioning of UVs on texture atlas and trim-sheet based texture sheets",
    "category": "UV"
}

import bpy
from . import ui

def register():
    bpy.utils.register_class(ui.AbstractOperator)
    bpy.utils.register_class(ui.TrimmerSettings)
    bpy.utils.register_class(ui.TrimmerUI)

def unregister():
    bpy.utils.unregister_class(ui.AbstractOperator)
    bpy.utils.unregister_class(ui.TrimmerSettings)
    bpy.utils.unregister_class(ui.TrimmerUI)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()