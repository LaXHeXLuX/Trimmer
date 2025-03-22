import bpy
import bmesh
import math
from mathutils import Vector
from .utils import *
from .multiple_face_unwrap import unwrap
from .utils2D import boundaryVertices, mvcWeights, applyMvcWeights

class Trimmer():
    currentApply = None
    currentFaces = None
    currentUV = None
    currentBoundary = None

    @classmethod
    def clear(cls, context):
        cls.currentApply = None
        cls.currentFaces = None
        cls.currentUV = None
        cls.currentBoundary = None

    @staticmethod
    def apply(faces, uvCoords, uvLayer):
        for i in range(len(faces)):
            for j in range(len(faces[i].loops)):
                UVLoop = faces[i].loops[j][uvLayer]
                coord = uvCoords[i][j]
                print(f"applying UV: {UVLoop.uv} = {coord}")
                UVLoop.uv = coord

    @classmethod
    def applyFaces(cls, context, faces, trim, uvLayer, operator):
        # Get adjusted UV coordinates
        meshCoords = Trim.parseMeshCoordinates(faces)

        #for i in range(len(faces)):
        #    if len(faces[i].loops) != len(meshCoords[i]):
        #        operator.report({'ERROR'}, f"Selected face ({len(face.loops)} vertices) must have the same number of vertices as the saved face ({len(uvCoords)} vertices)!")
        #        return

        flatMeshCoords = unwrap(meshCoords)
        boundary = boundaryVertices(meshCoords)
        print(f"flatMeshCoords: {flatMeshCoords}\n")

        fitOption = context.scene.trim_options.fitOptions
        uvCoords = None
        if fitOption == 'FIT':
            uvCoords = Trim.uvCoordsForFit(trim.getUvCoords(), flatMeshCoords)
        elif fitOption == 'FIT_X':
            uvCoords = Trim.uvCoordsForFit(trim.getUvCoords(), flatMeshCoords, boundByY=False)
        elif fitOption == 'FIT_Y':
            uvCoords = Trim.uvCoordsForFit(trim.getUvCoords(), flatMeshCoords, boundByX=False)
        elif fitOption == 'FILL':
            uvCoords = Trim.uvCoordsForFill(trim.getUvCoords(), flatMeshCoords)
        else:
            raise Exception(f"Invalid fit option: {fitOption}")
        
        print(f"trim.getUvCoords(): {trim.getUvCoords()}\n")
        print(f"uvCoords: {uvCoords}\n")

        apply(faces, uvCoords, uvLayer)

        currentApply = fitOption
        currentFaces = faces
        currentUV = uvCoords
        currentBoundary = boundary(uvCoords)

    @classmethod
    def apply_texture(cls, context, operator):
        print("\n--------------------------------------------")
        print("apply texture")
        # Run checks
        obj = context.object
        if obj is None or obj.type != 'MESH' or obj.mode != 'EDIT':
            operator.report({'ERROR'}, "You must be in Edit Mode with a mesh object selected!")
            return

        if not obj.data.uv_layers:
            operator.report({'ERROR'}, "The object does not have any UV maps!")
            return

        bm = bmesh.from_edit_mesh(obj.data)
        
        uvLayer = bm.loops.layers.uv.active
        if uvLayer is None:
            operator.report({'ERROR'}, "The object does not have an active UV map!")
            return

        selectedFaces = [face for face in bm.faces if face.select]
        if selectedFaces is None or selectedFaces == []:
            operator.report({'ERROR'}, "No face selected!")
            return

        trim = context.scene.trim_collection[operator.index]
        if trim is None:
            operator.report({'ERROR'}, "Trim is null!")
            return

        Trimmer.applyFaces(context, selectedFaces, trim, uvLayer, operator)
        
        bmesh.update_edit_mesh(obj.data)

    @classmethod
    def add_trim(cls, context, operator):
        # Run checks
        obj = context.object
        if obj is None or obj.type != 'MESH' or obj.mode != 'EDIT':
            operator.report({'ERROR'}, "You must be in Edit Mode with a mesh object selected!")
            return False

        bm = bmesh.from_edit_mesh(obj.data)
        uvLayer = bm.loops.layers.uv.active
        if uvLayer is None:
            operator.report({'ERROR'}, "The object does not have an active UV map!")
            return False

        selectedFaces = [face for face in bm.faces if face.select]
        if selectedFaces is None or selectedFaces == []:
            operator.report({'ERROR'}, "No face selected!")
            return False
            
        face = selectedFaces[0]

        uvCoords = [loop[uvLayer].uv.copy() for loop in face.loops]
        trim = context.scene.trim_collection.add()
        trim.init(uvCoords, len(context.scene.trim_collection))

    @classmethod
    def delete_trim(cls, context, operator):
        context.scene.trim_collection.remove(operator.index)

class UVCoord(bpy.types.PropertyGroup):
    uv: bpy.props.FloatVectorProperty(size=2)

    def getVector(self):
        return Vector(self.uv)

class Trim(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    uvCoords: bpy.props.CollectionProperty(type=UVCoord)

    def init(self, uvCoords, index):
        self.name = f"Trim {index}"
        self.setUvCoords(compactPoints(uvCoords))

    def __init__(self, uvCoords, index=1):
        self.init(uvCoords, index)

    def setUvCoords(self, uvCoords):
        self.uvCoords.clear()
        
        for coord in uvCoords:
            uvCoordItem = self.uvCoords.add()
            uvCoordItem.uv = coord.copy()

    def getUvCoords(self):
        arr = []

        for coord in self.uvCoords:
            arr.append(coord.getVector())
        
        return arr

    @staticmethod
    def uvCoordsForFill(uvCoords, meshCoords):
        print("uvCoordsForFill(uvCoords, meshCoords)")
        print(uvCoords)
        print(meshCoords)

        boundary = boundaryVertices(meshCoords)
        weights = mvcWeights(boundary, meshCoords)
        weighted = applyMvcWeights(uvCoords, weights)

        return weighted

    @staticmethod
    def uvCoordsForFit(uvCoords, meshCoords, boundByX = True, boundByY = True):
        print("uvCoordsForFit(uvCoords, meshCoords)")
        print(uvCoords)
        print(meshCoords)
        from .utils2D import containedPolygons

        return containedPolygons(meshCoords, uvCoords, boundByX, boundByY)

    @staticmethod
    def parseMeshCoordinates(faces):
        mesh = []

        for face in faces:
            mesh.append([loop.vert.co for loop in face.loops])

        return mesh