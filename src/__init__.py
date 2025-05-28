bl_info = {
    "name": "Trimmer",
    "author": "Laas Hendrik Lumberg",
    "version": (0, 2, 5),
    "blender": (4, 2, 0),
    "location": "3D View > Tool Panel",
    "description": "Allows easier positioning of UVs on texture atlas and trim-sheet based texture sheets",
    "category": "UV"
}

def _get_registration_data():
    import bpy
    from . import ui
    from . import trimmer

    classes1 = [trimmer.UVCoord, trimmer.Trim, ui.AbstractOperator, ui.TrimOptions]
    classes2 = [ui.TrimmerUI, ui.ApplyTrimSettings]

    return bpy, trimmer, ui, classes1, classes2

def register():
    bpy, trimmer, ui, classes1, classes2 = _get_registration_data()

    for c in classes1:
        bpy.utils.register_class(c)
        
    bpy.types.Scene.trim_collection = bpy.props.CollectionProperty(type=trimmer.Trim)
    bpy.types.Scene.trim_options = bpy.props.PointerProperty(type=ui.TrimOptions)

    for c in classes2:
        bpy.utils.register_class(c)

def unregister():
    bpy, _, _, classes1, classes2 = _get_registration_data()
    
    for c in (classes1 + classes2)[::-1]:
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.trim_options
    del bpy.types.Scene.trim_collection

if __name__ == "__main__":
    register()