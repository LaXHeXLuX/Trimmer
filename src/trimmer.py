import bpy
import bmesh
import math
from mathutils import Vector
from .utils import *
from .multiple_face_unwrap import unwrap
from .utils2D import boundaryVertices, mvcWeights, applyMvcWeights, mirrorPoints

class TrimmerException(Exception):
    pass

class Trimmer():
    currentApplyOption = None
    currentFaces = None
    flatMeshCoords = None
    currentBoundary = None
    currentUVLayer = None

    @classmethod
    def clear(cls, context):
        cls.currentApplyOption = None
        cls.currentFaces = None
        cls.flatMeshCoords = None
        cls.currentBoundary = None
        cls.currentUVLayer = None

    @staticmethod
    def getObject(context):
        obj = context.object
        if obj is None or obj.type != 'MESH' or obj.mode != 'EDIT':
            raise TrimmerException("You must be in Edit Mode with a mesh object selected!")

        return obj

    @staticmethod
    def getUvLayer(bm):
        if not bm.loops.layers.uv.items():
            raise TrimmerException("The object does not have any UV maps!")
        
        uvLayer = bm.loops.layers.uv.active
        if uvLayer is None:
            raise TrimmerException("The object does not have an active UV map!")

        return uvLayer

    @staticmethod
    def apply(faces, uvCoords, uvLayer):
        for i in range(len(faces)):
            for j in range(len(faces[i].loops)):
                UVLoop = faces[i].loops[j][uvLayer]
                coord = uvCoords[i][j]
                print(f"applying UV: {UVLoop.uv} = {coord}")
                UVLoop.uv = coord

    @classmethod
    def applyFaces(cls, context, faces, trim, uvLayer):
        meshCoords = Trim.parseMeshCoordinates(faces)

        flatMeshCoords = unwrap(meshCoords)
        boundary = boundaryVertices(flatMeshCoords)
        print(f"flatMeshCoords: {flatMeshCoords}\n")

        fitOption = context.scene.trim_options.fitOptions
        uvCoords = Trim.uvCoords(trim.getUvCoords(), flatMeshCoords, fitOption)
        
        print(f"trim.getUvCoords(): {trim.getUvCoords()}\n")
        print(f"uvCoords: {uvCoords}\n")

        cls.apply(faces, uvCoords, uvLayer)

        cls.currentApplyOption = fitOption
        cls.currentFaces = faces
        cls.flatMeshCoords = flatMeshCoords
        cls.currentBoundary = boundaryVertices(uvCoords)
        cls.currentUVLayer = uvLayer

    @classmethod
    def apply_texture(cls, context, operator):
        print("\n--------------------------------------------")
        print("apply texture")

        try:
            obj = cls.getObject(context)
            bm = bmesh.from_edit_mesh(obj.data)
            uvLayer = cls.getUvLayer(bm)
        except TrimmerException as error:
            operator.report({'ERROR'}, error)
            return

        selectedFaces = [face for face in bm.faces if face.select]
        if selectedFaces is None or selectedFaces == []:
            operator.report({'ERROR'}, "No face selected!")
            return

        trim = context.scene.trim_collection[operator.index]
        if trim is None:
            operator.report({'ERROR'}, "Trim is null!")
            return

        Trimmer.applyFaces(context, selectedFaces, trim, uvLayer)
        
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
    def uvCoords(uvCoords, flatMeshCoords, fitOption):
        if fitOption == 'FIT':
            return Trim.uvCoordsForFit(uvCoords, flatMeshCoords)
        elif fitOption == 'FIT_X':
            return Trim.uvCoordsForFit(uvCoords, flatMeshCoords, boundByY=False)
        elif fitOption == 'FIT_Y':
            return Trim.uvCoordsForFit(uvCoords, flatMeshCoords, boundByX=False)
        elif fitOption == 'FILL':
            return Trim.uvCoordsForFill(uvCoords, flatMeshCoords)
        else:
            raise Exception(f"Invalid fit option: {fitOption}")

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