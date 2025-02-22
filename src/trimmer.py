import bpy
import bmesh
import math
from mathutils import Vector

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
        
        # Get adjusted UV coordinates
        face_coords = [loop.vert.co for loop in face.loops]
        uv_coords = Trim.get_uv_coords_for_face(trim.get_uv_coords(), face_coords)

        if len(face.loops) != len(uv_coords):
            operator.report({'ERROR'}, f"Selected face ({len(face.loops)} vertices) must have the same number of vertices as the saved face ({len(uv_coords)} vertices)!")
            return

        # Apply UV coordinates
        for loop, uv in zip(face.loops, uv_coords):
            loop[uv_layer].uv = uv

        bmesh.update_edit_mesh(obj.data)

    @classmethod
    def add_trim(cls, context, operator):
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

        uv_coords = [loop[uv_layer].uv.copy() for loop in face.loops]
        trim = context.scene.trim_collection.add()
        trim.init(uv_coords)

    @classmethod
    def delete_trim(cls, context, operator):
        context.scene.trim_collection.remove(operator.index)

class UVCoord(bpy.types.PropertyGroup):
    uv: bpy.props.FloatVectorProperty(size=2)

    def get_vector(self):
        return Vector(self.uv)

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
            uv_coord_item.uv = coord.copy()

    def get_uv_coords(self):
        arr = []

        for coord in self.uv_coords:
            arr.append(coord.get_vector())
        
        return arr

    @staticmethod 
    def compare(x1, x2):
        EPSILON = 1e-6
        difference = x1-x2
        if abs(difference) < EPSILON:
            return 0
        if difference < -EPSILON:
            return -1
        if difference > EPSILON:
            return 1
        raise ArithmeticError(f"Values {x1}, {x2} don't respond to our laws of math!")

    @staticmethod
    def vectorAreEqual(v1, v2):
        if len(v1) != len(v2):
            return False

        for i in range(len(v1)):
            if Trim.compare(v1[i], v2[i]) != 0:
                return False
        
        return True

    @staticmethod
    def is_collinear(p1, p2, p3):
        v1 = p2 - p1
        v2 = p3 - p2

        for i in range(len(v1)):
            if v1[i] != 0 or v2[i] != 0:
                return Trim.vectorAreEqual(v1 * v2[i], v2 * v1[i])

        return Trim.vectorAreEqual(scaled_v1, scaled_v2)

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
    def get_uv_coords_for_face(uv_coords, face_coords):
        noncollinear_indexes = []
        collinear_indexes_neighbours = []
        collinearity = []

        # Sort points by collinearity
        for i in range(len(face_coords)):
            if Trim.point_is_collinear(face_coords, i):
                collinearity.append(True)
            else:
                collinearity.append(False)
                noncollinear_indexes.append(i)

        new_uv_coords = []
        for coord in uv_coords:
            new_uv_coords.append(coord)

        if len(noncollinear_indexes) == len(collinearity):
            return new_uv_coords

        # Find each point's noncollinear neighbours
        noncollinear_neighbours = []
        prevI = len(noncollinear_indexes)-1
        nextI = 0
        for i in range(len(face_coords)):
            if not collinearity[i]:
                nextI = (nextI + 1) % len(noncollinear_indexes)
                noncollinear_neighbours.append([prevI, nextI])
                prevI = (prevI + 1) % len(noncollinear_indexes)
            else:
                noncollinear_neighbours.append([prevI, nextI])

        inserted = 0
        firstEdge = True
        for i in range(len(face_coords)):
            prevI, nextI = noncollinear_neighbours[i]
            if nextI != 0: 
                firstEdge = False
            
            if not collinearity[i]:
                continue

            smallDist = math.dist(face_coords[noncollinear_indexes[prevI]], face_coords[i])
            fullDist = math.dist(face_coords[noncollinear_indexes[prevI]], face_coords[noncollinear_indexes[nextI]])

            uv_vector = uv_coords[nextI] - uv_coords[prevI]

            newPoint = uv_coords[prevI] + uv_vector * (smallDist / fullDist)
            index = (prevI + inserted + 1)
            if firstEdge and index == len(new_uv_coords): index = inserted

            new_uv_coords.insert(index, newPoint)

            inserted += 1

        return new_uv_coords
