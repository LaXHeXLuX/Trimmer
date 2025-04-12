import bpy
import bmesh
from mathutils import Vector
from .utils import *
from .multiple_face_unwrap import unwrap, UnwrapException
from .utils2D import boundaryVertices, mvcWeights, applyMvcWeights, mirrorPoints, rotatePointsFill, rotatePointsFit

class TrimmerException(Exception):
    pass

class Trimmer():
    currentApplyOption = None
    currentFaceIndexes = None
    flatMeshCoords = None
    currentReferenceCoords = None
    currentTrim = None

    @classmethod
    def clear(cls):
        cls.currentApplyOption = None
        cls.currentFaceIndexes = None
        cls.flatMeshCoords = None
        cls.currentReferenceCoords = None
        cls.currentTrim = None

    @classmethod
    def getFacesFromIndexes(cls, bm):
        return [bm.faces[faceIndex] for faceIndex in cls.currentFaceIndexes]

    @staticmethod
    def uvCoordsFromFaces(faces, uvLayer, single = False):
        if single:
            return [loop[uvLayer].uv[:] for loop in faces.loops]
        else:
            return [[loop[uvLayer].uv[:] for loop in face.loops] for face in faces]

    @staticmethod
    def getObject(context):
        obj = context.object
        if obj is None or obj.type != 'MESH' or obj.mode != 'EDIT':
            raise TrimmerException("You must be in Edit Mode with a mesh object selected!")

        return obj

    @staticmethod
    def getNewBm(obj):
        return bmesh.from_edit_mesh(obj.data)

    @staticmethod
    def getUvLayer(bm):
        if not bm.loops.layers.uv.items():
            raise TrimmerException("The object does not have any UV maps!")

        uvLayer = bm.loops.layers.uv.active
        if uvLayer is None:
            raise TrimmerException("The object does not have an active UV map!")

        return uvLayer

    @classmethod
    def apply(cls, context, faces, uvCoords, uvLayer, temporary = False):
        for i in range(len(faces)):
            for j in range(len(faces[i].loops)):
                UVLoop = faces[i].loops[j][uvLayer]
                coord = uvCoords[i][j]
                UVLoop.uv = coord

        if not temporary: 
            cls.currentReferenceCoords = uvCoords
            context.scene.trim_options.clear()

    @classmethod
    def applyFaces(cls, context, faces, trim, uvLayer):
        meshCoords = Trim.parseMeshCoordinates(faces)

        flatMeshCoords = unwrap(meshCoords)

        fitOption = context.scene.trim_options.fitOptions
        uvCoords = Trim.uvCoords(trim.getUvCoords(), flatMeshCoords, fitOption)

        cls.apply(context, faces, uvCoords, uvLayer)

        cls.currentApplyOption = fitOption
        cls.currentFaceIndexes = [f.index for f in faces]
        cls.flatMeshCoords = flatMeshCoords
        cls.currentTrim = trim

    @classmethod
    def apply_texture(cls, context, index):
        print("\n--------------------------------------------")
        print("apply texture")

        obj = cls.getObject(context)
        bm = cls.getNewBm(obj)
        uvLayer = cls.getUvLayer(bm)

        selectedFaces = [face for face in bm.faces if face.select]
        if selectedFaces is None or selectedFaces == []:
            raise TrimmerException("No face selected!")

        trim = context.scene.trim_collection[index]
        if trim is None:
            raise TrimmerException("Trim is null!")

        try:
            cls.applyFaces(context, selectedFaces, trim, uvLayer)
        except UnwrapException as ue:
            raise TrimmerException(str(ue))

        bmesh.update_edit_mesh(obj.data)

    @classmethod
    def add_trim(cls, context):
        obj = cls.getObject(context)
        bm = cls.getNewBm(obj)
        uvLayer = cls.getUvLayer(bm)

        selectedFaces = [face for face in bm.faces if face.select]
        if selectedFaces is None or selectedFaces == []:
            raise TrimmerException("No face selected!") # Error handling

        face = selectedFaces[0]

        uvCoords = cls.uvCoordsFromFaces(face, uvLayer, single=True)
        uvCoords = compactPoints(uvCoords)
        trim = context.scene.trim_collection.add()
        trim.init(uvCoords, len(context.scene.trim_collection))

    @classmethod
    def delete_trim(cls, context, index):
        trims = context.scene.trim_collection
        if 0 <= index < len(trims):
            trims.remove(index)
        else:
            raise IndexError(f"Index {index} is out of range for the trim collection (length {len(trims)}).")

    @classmethod
    def mirror_trim(cls, context):
        obj = cls.getObject(context)
        bm = cls.getNewBm(obj)
        uvLayer = cls.getUvLayer(bm)

        faces = cls.getFacesFromIndexes(bm)
        mirroredPoints = mirrorPoints(cls.uvCoordsFromFaces(faces, uvLayer))
        mirroredUV = Trim.uvCoords(cls.currentTrim.getUvCoords(), mirroredPoints, cls.currentApplyOption)
        cls.apply(context, faces, mirroredUV, uvLayer)

        bmesh.update_edit_mesh(obj.data)

    @classmethod
    def rotate_trim(cls, context, degrees = None):
        obj = cls.getObject(context)
        bm = cls.getNewBm(obj)
        uvLayer = cls.getUvLayer(bm)
        faces = cls.getFacesFromIndexes(bm)

        if cls.currentApplyOption == 'FILL':
            rotatedUV = rotatePointsFill(cls.uvCoordsFromFaces(faces, uvLayer))
        else:
            if degrees == None:
                raise TrimmerException(f"Parameter degrees for fit option {cls.currentApplyOption} can not be null!")
            rotatedUnfitUV = rotatePointsFit(cls.currentReferenceCoords, degrees)
            rotatedUV = Trim.uvCoords(cls.currentTrim.getUvCoords(), rotatedUnfitUV, cls.currentApplyOption)

        cls.apply(context, faces, rotatedUV, uvLayer, temporary=True)
        bmesh.update_edit_mesh(obj.data)

class UVCoord(bpy.types.PropertyGroup):
    uv: bpy.props.FloatVectorProperty(size=2) # type: ignore

    def getVector(self):
        return Vector(self.uv)

class Trim(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty() # type: ignore
    uvCoords: bpy.props.CollectionProperty(type=UVCoord) # type: ignore

    def init(self, uvCoords, index):
        self.name = f"Trim {index}"
        self.setUvCoords(compactPoints(uvCoords))

    def __init__(self, uvCoords, index=1):
        self.init(uvCoords, index)

    def setUvCoords(self, uvCoords):
        self.uvCoords.clear()

        for coord in uvCoords:
            uvCoordItem = self.uvCoords.add()
            uvCoordItem.uv = coord[:]

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
        boundary = boundaryVertices(meshCoords)

        boundaryNormal = normal(*boundary[0:3])
        uvCoordsNormal = normal(*uvCoords[0:3])
        if compare(boundaryNormal, uvCoordsNormal) != 0:
            boundary.reverse()

        weights = mvcWeights(boundary, meshCoords)
        weighted = applyMvcWeights(uvCoords, weights)

        return weighted

    @staticmethod
    def uvCoordsForFit(uvCoords, meshCoords, boundByX = True, boundByY = True):
        from .utils2D import containedPolygons

        return containedPolygons(meshCoords, uvCoords, boundByX, boundByY)

    @staticmethod
    def parseMeshCoordinates(faces):
        mesh = []

        for face in faces:
            mesh.append([loop.vert.co[:] for loop in face.loops])

        return mesh