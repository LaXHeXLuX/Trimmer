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

classes = [ui.AbstractOperator, ui.TrimOptions, ui.TrimmerUI, ui.ApplyTrimSettings, trimmer.UVCoord, trimmer.Trim]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.trim_collection = bpy.props.CollectionProperty(type=trimmer.Trim)
    bpy.types.Scene.trim_options = bpy.props.PointerProperty(type=ui.TrimOptions)

def unregister():
    del bpy.types.Scene.trim_options
    del bpy.types.Scene.trim_collection
    for c in classes[::-1]:
        bpy.utils.register_class(c)

if __name__ == "__main__":
    register()