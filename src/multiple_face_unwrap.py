import numpy as np
import copy

if __name__ == '__main__':
    from utils import *
else:
    from .utils import *

class UnwrapException(Exception):
    pass

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

def rotationMatrixToFlattenFace(face, indexIncreasing):
    normal1 = faceNormal(face, indexIncreasing)
    normal2 = np.array((0, 0, 1))
    return rotationMatrixFromNormals(normal1, normal2)

def getPerpendicularVector(v):
    pv = (1, 0, 0)
    if v[0] != 0:
        pv = (-v[1], v[0], 0)
    elif v[1] != 0:
        pv = (v[2], 0, -v[0])

    return pv

def antiParallelRotationMatrix(v1):        
    axis = getPerpendicularVector(v1)
    R = 2 * np.outer(np.array(axis), np.array(axis)) - np.eye(3)
    return R

def rotationMatrixFromNormals(v1, v2):
    v1, v2 = normalise(v1), normalise(v2)
    v = crossProduct(v1, v2)

    if distance(v) == 0:
        if np.dot(np.array(v1), np.array(v2)) > 0:
            return np.eye(3)
        
        return antiParallelRotationMatrix(v1)

    K = np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0]
    ])

    cosTheta = np.dot(v1, v2)
    R = np.eye(3) + K + np.dot(K, K) / (1 + cosTheta)
    return R

def faceNormal(face, indexIncreasing):
    P1, P2, P3 = face[0], face[1], face[2]
    if not indexIncreasing:
        P1, P3 = face[2], face[0]
    return normal(P1, P2, P3)

def flatFaceCoordinates(face, indexIncreasing):
    R = rotationMatrixToFlattenFace(face, indexIncreasing)
    return np.dot(np.array(face), R.T)

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

def dfs(matrix, visited, node):
    visited[node] = True
    for neighbor in range(len(matrix)):
        if matrix[node][neighbor] is not None and not visited[neighbor]:
            dfs(matrix, visited, neighbor)

def countIslands(matrix):
    visited = []
    for i in range(len(matrix)):
        visited.append(False)

    islandCount = 0
    for node in range(len(matrix)):
        if not visited[node]:
            dfs(matrix, visited, node)
            islandCount += 1
    
    return islandCount

def vertexIndexIncreasing(mesh, f1Index, f2Index, face1Increasing, graph):
    f1 = mesh[f1Index]
    f2 = mesh[f2Index]
    f1Edge = graph[f1Index][f2Index]
    f2Edge = graph[f2Index][f1Index]
    f1EdgeValues = (f1[f1Edge[0]], f1[f1Edge[1]])
    f2EdgeValues = (f2[f2Edge[0]], f2[f2Edge[1]])
    return (f1EdgeValues[0] == f2EdgeValues[0]) ^ face1Increasing

def translationRotationMatrix(o1, o2, t1, t2):
    vectorO = np.array(subtract(o1, o2))
    vectorT = np.array(subtract(t1, t2))
    vOnorm = np.linalg.norm(vectorO)
    vTnorm = np.linalg.norm(vectorT)
    product = vOnorm * vTnorm

    cosTheta = np.dot(vectorO, vectorT) / product
    sinTheta = np.cross(vectorO, vectorT) / product

    R = np.array([
        [cosTheta, -sinTheta],
        [sinTheta,  cosTheta]
    ])

    T = np.eye(3)
    T[:2, :2] = R
    T[:2, 2] = t1 - (R @ o1)

    return T

def transformFace(face, matrix):
    paddedFace = padPoints(face, len(matrix[0]))
    newFace = []
    for vertex in paddedFace:
        newFace.append(deepToList(matrix @ np.array(vertex)))
    return padPoints(newFace, len(matrix[0]) - 1)

def unwrap(mesh):
    mappedFaces = []
    mappedBy = []
    for i in range(len(mesh)):
        mappedFaces.append(None)
        mappedBy.append([])

    graph = graphOfFaces(mesh)
    islandCount = countIslands(graph)
    if islandCount == 0:
        raise UnwrapException("Mesh is empty!")
    if islandCount > 1:
        raise UnwrapException(f"Can't unwrap mesh with more than 1 ({islandCount}) islands!")

    stack = []
    stack.append((0, True, None)) # (<faceIndex>, <vertexIndexIncreasing>, <neighbourIndex>)

    while len(stack) > 0:
        index, indexIncreasing, neighbourIndex = stack.pop()

        if neighbourIndex in mappedBy[index]:
            continue

        for i in range(len(graph[index])):
            if graph[index][i] == None or i == neighbourIndex:
                continue
            neighbourIndexIncreasing = vertexIndexIncreasing(mesh, index, i, indexIncreasing, graph)
            stack.append((i, neighbourIndexIncreasing, index))

        F = copy.deepcopy(mesh[index])
        rotatedFace = deepToList(flatFaceCoordinates(F, indexIncreasing))
        rotatedFace = padPoints(rotatedFace, 2)

        origin1 = rotatedFace[0]
        origin2 = rotatedFace[1]
        target1 = rotatedFace[0]
        target2 = rotatedFace[1]
        if neighbourIndex != None:
            origin1 = rotatedFace[graph[index][neighbourIndex][0]]
            origin2 = rotatedFace[graph[index][neighbourIndex][1]]
            target1 = mappedFaces[neighbourIndex][graph[neighbourIndex][index][0]]
            target2 = mappedFaces[neighbourIndex][graph[neighbourIndex][index][1]]
            if indexIncreasing:
                target1, target2 = target2, target1
        
        matrix = translationRotationMatrix(origin1, origin2, target1, target2)
        transformedFace = transformFace(rotatedFace, matrix)

        if mappedFaces[index] != None:
            if compare(mappedFaces[index], transformedFace) != 0:
                raise UnwrapException("Shape is not unwrappable without distorion")
        else:
            mappedFaces[index] = transformedFace
            mappedBy[index].append(neighbourIndex)
            if neighbourIndex != None: mappedBy[neighbourIndex].append(index)

    return roundList(deepToList(mappedFaces))

# Testing

def testMethod(operation, inputs, output):
    result = operation(*inputs)
    if compare(result, output) != 0:
        raise Exception(f"Test failed with {operation.__name__}({inputs}) = {result} != {output}")

def test(inputArr, outputArr):
    result = unwrap(inputArr)
    if compare(result, outputArr) != 0:
        raise Exception(f"Equals test failed: {result} != {outputArr}")
    
def testFail(inputArr):
    try:
        result = unwrap(inputArr)
        raise Exception(f"Error test failed: {inputArr}")
    except UnwrapException as ue:
        pass

def runTests():
    test(
        [[(-1, -1, 0), (-1, 1, 0), (1, 1, 0), (1, -1, 0)]], 
        [[(-1, 1), (-1, -1), (1, -1), (1, 1)]]
    )
    test(
        [[(1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1)]], 
        [[(1, -1), (1, 1), (-1, 1), (-1, -1)]]
    )
    test(
        [
            [(-1, 1, 1), (-1, -1, 1), (1, -1, 1)], 
            [(-1, -1, 1), (1, -1, 1), (1, -1, -1)]
        ], 
        [
            [(-1, 1), (-1, -1), (1, -1)], 
            [(-1, -1), (1, -1), (1, -3)]
        ]
    )
    testFail(
        [
            [(-1, 1, 1), (-1, -1, 1), (1, -1, 1), (1, 1, 1)], 
            [(-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1)],
            [(-1, 1, 1), (-1, -1, 1), (-1, -1, -1), (1, 1, -1)]
        ]
    )
    test(
        [
            [(-1, 1, 1), (-1, -1, 1), (1, -1, 1), (1, 1, 1)], 
            [(-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1)],
            [(-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1)]
        ], 
        [
            [(-1, 1), (-1, -1), (1, -1), (1, 1)], 
            [(-1, -1), (1, -1), (1, -3), (-1, -3)], 
            [(-1, 1), (1, 1), (1, 3), (-1, 3)]
        ]
    )
    test(
        [
            [(1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1)], 
            [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)]
        ], 
        [
            [(1, -1), (1, 1), (-1, 1), (-1, -1)], 
            [(-1, -1), (-1, 1), (-3, 1), (-3, -1)]
        ]
    )
    test(
        [
            [(-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1)], 
            [(1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1)]
        ], 
        [
            [(-1, -1), (1, -1), (1, 1), (-1, 1)], 
            [(1, -1), (3, -1), (3, 1), (1, 1)]
        ]
    )
    test(
        [
            [(1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1)], 
            [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)], 
            [(1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1)]
        ],
        [
            [(1, -1), (1, 1), (-1, 1), (-1, -1)],
            [(-1, -1), (-1, 1), (-3, 1), (-3, -1)],
            [(3, -1), (3, 1), (1, 1), (1, -1)]
        ]
    )
    test(
        [
            [(2, 1, 1), (-1, 1, 1), (-1, 0, 1), (-1, -1, 1), (1, -1, 1)], 
            [(2, 1, -1), (2, 1, 1), (1, -1, 1), (1, -1, -1)]
        ],
        [
            [(2, 1), (-1, 1), (-1, 0), (-1, -1), (1, -1)],
            [(3.788854382, 0.105572809), (2, 1), (1, -1), (2.788854382, -1.894427191)]
        ]
    )
    testFail(
        [
            [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)],
            [(0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1)]
        ]
    )

if __name__ =="__main__":
    runTests()
    print("\nTests done.\n")