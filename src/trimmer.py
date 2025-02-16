import bpy
import bmesh

class Trimmer():
    @classmethod
    def test(cls, context, operator):
        operator.report({'INFO'}, "Test button is clicked!")

    @classmethod
    def apply_texture(cls, context, operator):
        trim = context.scene.trim_collection[operator.index]
        if not trim:
            operator.report({'ERROR'}, "Trim is null!")
            return

        uv_coords = trim.get_uv_coords()

        if not uv_coords:
            operator.report({'ERROR'}, "No UV data saved on this Trim!")
            return

        obj = context.object
        if obj is None or obj.type != 'MESH' or obj.mode != 'EDIT':
            operator.report({'ERROR'}, "You must be in Edit Mode with a mesh object selected!")
            return

        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            operator.report({'ERROR'}, "The object does not have an active UV map!")
            return

        selected_faces = [face for face in bm.faces if face.select]
        if not selected_faces:
            operator.report({'ERROR'}, "No face selected!")
            return

        face = selected_faces[0]
        if len(face.loops) != len(uv_coords):
            operator.report({'ERROR'}, f"Selected face ({len(face.loops)} vertices) must have the same number of vertices as the saved face ({len(trim.uv_coords)} vertices)!")
            return

        # Apply UV coordinates
        for loop, uv in zip(face.loops, uv_coords):
            loop[uv_layer].uv = uv

        bmesh.update_edit_mesh(obj.data)

    @staticmethod
    def uv_coords(context, operator):
        # Run checks
        obj = context.object
        if obj is None or obj.type != 'MESH' or obj.mode != 'EDIT':
            operator.report({'ERROR'}, "You must be in Edit Mode with a mesh object selected!")
            return False

        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            operator.report({'ERROR'}, "The object does not have an active UV map!")
            return False

        selected_faces = [face for face in bm.faces if face.select]
        if not selected_faces:
            operator.report({'ERROR'}, "No face selected!")
            return False

        # Save UV coordinates
        face = selected_faces[0]
        return [loop[uv_layer].uv.copy() for loop in face.loops]

    @classmethod
    def add_trim(cls, context, operator):
        uv_coords = cls.uv_coords(context, operator)
        if not uv_coords: 
            return

        trim = context.scene.trim_collection.add()
        trim.init(uv_coords)

    @classmethod
    def delete_trim(cls, context, operator):
        context.scene.trim_collection.remove(operator.index)

class UVCoord(bpy.types.PropertyGroup):
    uv: bpy.props.FloatVectorProperty(size=2)

class Trim(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    uv_coords: bpy.props.CollectionProperty(type=UVCoord)

    def init(self, uv_coords):
        self.name = "NewTrim"
        self.set_uv_coords(self.compact_points(uv_coords))

    def __init__(self, uv_coords):
        self.init(uv_coords)

    def set_uv_coords(self, uv_coords):
        self.uv_coords.clear()
        
        for coord in uv_coords:
            uv_coord_item = self.uv_coords.add()
            uv_coord_item.uv = coord

    def get_uv_coords(self):
        arr = []

        for coord in self.uv_coords:
            arr.append(coord.uv)
        
        return arr

    @staticmethod
    def compact_points(points):
        def is_collinear(p1, p2, p3):
            return (p2[0] - p1[0]) * (p3[1] - p2[1]) == (p2[1] - p1[1]) * (p3[0] - p2[0])

        if len(points) < 3:
            return points

        compacted = []

        for i in range(len(points)):
            # Get the three points to check
            p1 = points[(i - 1) % len(points)]  # Previous point (wrap around using modulo)
            p2 = points[i]
            p3 = points[(i + 1) % len(points)]  # Next point (wrap around using modulo)

            # Include the point if it's not collinear with its neighbors
            if not is_collinear(p1, p2, p3):
                compacted.append(p2)

        return compacted