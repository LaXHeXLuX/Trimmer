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
from . import trimmer

def register():
    bpy.utils.register_class(ui.AbstractOperator)
    bpy.utils.register_class(ui.TrimmerSettings)
    bpy.utils.register_class(ui.TrimmerUI)
    bpy.utils.register_class(trimmer.Trim)
    bpy.types.Scene.trim_collection = bpy.props.CollectionProperty(type=trimmer.Trim)

def unregister():
    bpy.utils.unregister_class(ui.AbstractOperator)
    bpy.utils.unregister_class(ui.TrimmerSettings)
    bpy.utils.unregister_class(ui.TrimmerUI)
    del bpy.types.Scene.trim_collection
    bpy.utils.unregister_class(trimmer.Trim)

if __name__ == "__main__":
    register()