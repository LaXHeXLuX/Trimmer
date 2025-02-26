import numpy as np

class Face:
    def __init__(self, vertices):
        self.vertices = vertices
    
    @classmethod
    def initEdges(cls, edges):
        return cls(cls.vertsFromEdges(edges))

    def getNumpyVertices(self):
        verts = []
        for v in self.vertices:
            verts.append(np.array(v))
        return verts

    @staticmethod
    def sortEdges(edges):
        edgesCopy = []
        for edge in edges:
            edgesCopy.append(edge)

        newEdges = [edgesCopy.pop(0)]
        while edgesCopy != []:
            v = newEdges[len(newEdges) - 1][1]
            i = 0
            while edgesCopy[i][0] != v:
                i += 1
            newEdges.append(edgesCopy.pop(i))
        
        if newEdges[0][0] != newEdges[len(newEdges) - 1][1]:
            raise Exception(f"Last edge {newEdges[len(newEdges) - 1]} should connect to first edge {newEdges[0]}")

        return newEdges

    @staticmethod
    def vertsFromEdges(edges):
        sortedEdges = Face.sortEdges(edges)
        vertices = []
        for edge in edges:
            vertices.append(edge[0])
        return vertices

def compare(x1, x2):
    EPSILON = 1e-8
    difference = x1-x2
    if difference < -EPSILON:
        return -1
    if difference > EPSILON:
        return 1
    return 0

def deepCompare(a1, a2):
    try:
        for i in range(len(a1)):
            elementCompare = deepCompare(a1[i], a2[i])
            if elementCompare > 0:
                return 1
            if elementCompare < 0:
                return -1
        return 0
    except:
        return compare(a1, a2)

def rotationMatrixToFlattenFace(face, indexIncreasing):
    normal1 = faceNormal(face, indexIncreasing)
    normal2 = np.array([0, 0, 1])
    return rotationMatrixFromNormals(normal1, normal2)

def rotationMatrixFromNormals(v1, v2):
    v1, v2 = v1 / np.linalg.norm(v1), v2 / np.linalg.norm(v2)
    v = np.cross(v1, v2)
    v_norm = np.linalg.norm(v)

    if v_norm == 0:
        return np.eye(3) 

    K = np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0]
    ])

    cos_theta = np.dot(v1, v2)
    R = np.eye(3) + K + np.dot(K, K) / (1 + cos_theta)
    return R

def faceNormal(face, indexIncreasing):
    vertices = face.getNumpyVertices()
    P1, P2, P3 = vertices[0], vertices[1], vertices[2]
    if not indexIncreasing:
        P1, P3 = vertices[2], vertices[0]
    return normal(P1, P2, P3)

def normal(P1, P2, P3):
    V1 = P2 - P1
    V2 = P3 - P2
    normal = np.cross(V1, V2)
    return normal / np.linalg.norm(normal)

def flatFaceCoordinates(face, indexIncreasing):
    R = rotationMatrixToFlattenFace(face, indexIncreasing)
    return np.dot(face.getNumpyVertices(), R.T)

def roundList(arr):
    newArr = []
    for a in arr:
        try:
            newArr.append(float(round(a, 8)))
        except:
            newArr.append(roundList(a))
    return newArr

def sharedEdge(f1, f2):
    for i in range(len(f1)):
        for j in range(len(f2)):
            if f1[i] == f2[j]:
                prevI = (i - 1) % len(f1)
                nextI = (i + 1) % len(f1)
                prevJ = (j - 1) % len(f2)
                nextJ = (j + 1) % len(f2)

                if f1[prevI] == f2[prevJ] or f1[prevI] == f2[nextJ]:
                    return (prevI, i)
                if f1[nextI] == f2[prevJ] or f1[nextI] == f2[nextJ]:
                    return (i, nextI)
    return None

def emptyMatrix(n, m):
    matrix = []
    for i in range(n):
        matrix.append([])
        for j in range(m):
            matrix[i].append(None)

    return matrix

def graphOfFaces(mesh):
    graphMatrix = emptyMatrix(len(mesh), len(mesh))

    for i in range(len(mesh)):
        for j in range(len(mesh)):
            if i == j:
                continue
            edge = sharedEdge(mesh[i], mesh[j])
            graphMatrix[i][j] = edge
    
    return graphMatrix

def indexIncreasing(i1, i2):
    if i2 - i1 == 1:
        return True
    if i1 - i2 == 1:
        return False
    if i2 == 0:
        return True
    if i1 == 0:
        return False
    raise Exception(f"Illegal arguments: {i1}, {i2}")

def vertexIndexIncreasing(f1Index, f2Index, face1Increasing, graph):
    f1 = mesh[f1Index]
    f2 = mesh[f2Index]
    f1Edge = graph[f1Index][f2Index]
    f2Edge = graph[f2Index][f1Index]
    f1EdgeValues = (f1[f1Edge[0]], f1[f1Edge[1]])
    f2EdgeValues = (f2[f2Edge[0]], f2[f2Edge[1]])
    return (f1EdgeValues[0] == f2EdgeValues[0]) ^ face1Increasing

def moveFace(face, vector):
    newFace = []
    for vertex in face:
        newFace.append(vertex + vector)
    return newFace

def unwrap(mesh):
    print("unwrap. mesh:")
    for f in mesh:
        print(f)
    print()

    import copy

    mappedFaces = []
    mappedBy = []
    for i in range(len(mesh)):
        mappedFaces.append(None)
        mappedBy.append([])

    graph = graphOfFaces(mesh)
    stack = []
    stack.append((0, True, None)) # (<faceIndex>, <vertexIndexIncreasing>, <neighbourIndex>)
    
    for i in range(len(graph)):
        print(graph[i])
    print()

    while len(stack) > 0:
        index, indexIncreasing, neighbourIndex = stack.pop()
        print(f"new loop. stack size: {len(stack)}")
        print(f"index {index}, indexIncreasing {indexIncreasing}, neighbourIndex {neighbourIndex}")

        if neighbourIndex in mappedBy[index]:
            print(f"{index} already mapped from {neighbourIndex}")
            continue

        for i in range(len(graph[index])):
            if graph[index][i] == None:
                continue
            neighbourIndexIncreasing = vertexIndexIncreasing(index, i, indexIncreasing, graph)
            stack.append((i, neighbourIndexIncreasing, index))
            print(f"adding {(i, neighbourIndexIncreasing, index)} to stack")

        F = Face(copy.deepcopy(mesh[index]))
        rotatedFace = Face(flatFaceCoordinates(F, indexIncreasing)).getNumpyVertices()

        vector = -1 * rotatedFace[0]
        if neighbourIndex != None:
            origin = rotatedFace[graph[index][neighbourIndex][0]]
            target = mappedFaces[neighbourIndex][graph[neighbourIndex][index][0]]
            vector = np.array(target) - np.array(origin)
        
        movedFace = moveFace(rotatedFace, vector)

        if mappedFaces[index] != None:
            if deepCompare(mappedFaces[index], movedFace) != 0:
                print(f"Face {index} is not unwrappable: {movedFace}, {mappedFaces[index]}. Neighbour {neighbourIndex}")
                raise Exception("Shape is not unwrappable without distorion")
        else:
            mappedFaces[index] = movedFace
            mappedBy[index].append(neighbourIndex)
    
    return mappedFaces

mesh = [
    [[0, 0, 0], [2, 0, 0], [0, 0, 2], [-2, 0, 2]],
    [[-2, 0, 2], [-2, -1, 3], [0, -1, 3], [0, 0, 2]],
    [[-2, 2, -2], [0, 0, 0], [2, 0, 0]]
]

graph = graphOfFaces(mesh)

unwrapped = unwrap(mesh)

for face in unwrapped:
    print(face)