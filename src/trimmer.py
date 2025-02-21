import bpy
import bmesh
import math

class Trimmer():
    @classmethod
    def test(cls, context, operator):
        operator.report({'INFO'}, "Test button is clicked!")

    @classmethod
    def apply_texture(cls, context, operator):
        # Run checks
        obj = context.object
        if obj is None or obj.type != 'MESH' or obj.mode != 'EDIT':
            operator.report({'ERROR'}, "You must be in Edit Mode with a mesh object selected!")
            return

        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.active
        if uv_layer is None:
            operator.report({'ERROR'}, "The object does not have an active UV map!")
            return

        selected_faces = [face for face in bm.faces if face.select]
        if selected_faces is None or selected_faces == []:
            operator.report({'ERROR'}, "No face selected!")
            return
            
        face = selected_faces[0]

        trim = context.scene.trim_collection[operator.index]
        if trim is None:
            operator.report({'ERROR'}, "Trim is null!")
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
        if uv_layer is None:
            operator.report({'ERROR'}, "The object does not have an active UV map!")
            return False

        selected_faces = [face for face in bm.faces if face.select]
        if selected_faces is None or selected_faces == []:
            operator.report({'ERROR'}, "No face selected!")
            return False
            
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
    def is_collinear(p1, p2, p3):
        return (p2[0] - p1[0]) * (p3[1] - p2[1]) == (p2[1] - p1[1]) * (p3[0] - p2[0])

    @staticmethod
    def point_is_collinear(points, index):
        # Get the three points to check
        p1 = points[(index - 1) % len(points)]  # Previous point (wrap around using modulo)
        p2 = points[index]
        p3 = points[(index + 1) % len(points)]  # Next point (wrap around using modulo)

        # Include the point if it's not collinear with its neighbors
        return Trim.is_collinear(p1, p2, p3)

    @staticmethod
    def compact_points(points):
        if len(points) < 3:
            return points

        compacted = []

        for i in range(len(points)):
            if not Trim.point_is_collinear(points, i):
                compacted.append(points[i])
        
        return compacted

    @staticmethod
    def get_uv_coords_for_face(uv_coords, face):
        not_collinear_indexes = []
        collinear_indexes = []

        for i in range(len(face)):
            if Trim.point_is_collinear(face, i):
                collinear_indexes.append(i)
            else:
                not_collinear_indexes.append(i)

        for i in collinear_indexes:
            # Get previous non-collinear neighbour
            prevIndex = 0
            while not_collinear_indexes[prevIndex] < i:
                prevIndex = (prevIndex + 1) % len(not_collinear_indexes)
            prevIndex -= 1
            prevI = not_collinear_indexes[prevIndex]

            # Get next non-collinear neighbour
            nextIndex = 0
            while not_collinear_indexes[nextIndex] < i:
                nextIndex = (nextIndex + 1) % len(not_collinear_indexes)
            nextI = not_collinear_indexes[nextIndex]

            dist1 = math.dist(face[prevI], face[i])
            dist2 = math.dist(face[i], face[nextI])
            
            uv_dist = math.dist(uv_coords[prevIndex], uv_coords[nextIndex])

