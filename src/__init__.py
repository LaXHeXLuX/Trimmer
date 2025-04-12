bl_info = {
    "name": "Trimmer",
    "author": "Laas Hendrik Lumberg",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Tool Panel",
    "description": "Allows easier positioning of UVs on texture atlas and trim-sheet based texture sheets",
    "category": "UV"
}

import bpy
from . import ui
from . import trimmer

classes1 = [trimmer.UVCoord, trimmer.Trim, ui.AbstractOperator, ui.TrimOptions]
classes2 = [ui.TrimmerUI, ui.ApplyTrimSettings]

def register():
    for c in classes1:
        bpy.utils.register_class(c)
        
    bpy.types.Scene.trim_collection = bpy.props.CollectionProperty(type=trimmer.Trim)
    bpy.types.Scene.trim_options = bpy.props.PointerProperty(type=ui.TrimOptions)

    for c in classes2:
        bpy.utils.register_class(c)

def unregister():
    for c in classes2[::-1]:
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.trim_options
    del bpy.types.Scene.trim_collection

    for c in classes1[::-1]:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()