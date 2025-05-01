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
    normal1 = faceNormal(compactPoints(face), indexIncreasing)
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

def sharedEdges(f1, f2):
    sharedEdges = []
    for i in range(len(f1)):
        for j in range(len(f2)):
            if f1[i] == f2[j]:
                prevI = (i - 1) % len(f1)
                nextI = (i + 1) % len(f1)
                prevJ = (j - 1) % len(f2)
                nextJ = (j + 1) % len(f2)

                if f1[prevI] == f2[prevJ] or f1[prevI] == f2[nextJ]:
                    sharedEdges.append((prevI, i))
    return sharedEdges

def emptyMatrix(n, m):
    matrix = []
    for i in range(n):
        matrix.append([])
        for j in range(m):
            matrix[i].append([])

    return matrix

def graphOfFaces(mesh, seams = []):
    graphMatrix = emptyMatrix(len(mesh), len(mesh))

    for i in range(len(mesh)-1):
        for j in range(i+1, len(mesh)):
            if (i, j) in seams:
                continue

            edges = sharedEdges(mesh[i], mesh[j])
            graphMatrix[i][j] = edges
            edges = sharedEdges(mesh[j], mesh[i])
            graphMatrix[j][i] = edges
    
    return graphMatrix

def dfs(matrix, visited, node):
    visited[node] = True
    for neighbor in range(len(matrix)):
        if len(matrix[node][neighbor]) > 0 and not visited[neighbor]:
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
    f1Edge = graph[f1Index][f2Index][0]
    f2Edge = graph[f2Index][f1Index][0]
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

def validateSeams(seams, numberOfFaces):
    validated = []
    for seam in seams:
        if max(seam) >= numberOfFaces:
            raise Exception(f"Invalid seam parameter: seam {seam} is referencing indexes larger than the number of faces ({numberOfFaces})")
        validated.append(tuple(sorted(seam)))

    return validated

def unwrap(mesh, seams = []):
    seams = validateSeams(seams, len(mesh))
 
    mappedFaces = []
    mappedBy = []
    for i in range(len(mesh)):
        mappedFaces.append(None)
        mappedBy.append([])

    graph = graphOfFaces(mesh, seams)
    islandCount = countIslands(graph)
    if islandCount == 0:
        raise UnwrapException("Mesh is empty!")
    if islandCount > 1:
        raise UnwrapException(f"Can't unwrap mesh with more than 1 islands (currently {islandCount})!")

    stack = []
    stack.append((0, True, None, None)) # (<faceIndex>, <vertexIndexIncreasing>, <neighbourIndex>, <neighbourEdgeIndex>)

    while len(stack) > 0:
        index, indexIncreasing, neighbourIndex, neighbourEdgeIndex = stack.pop()

        if (neighbourIndex, neighbourEdgeIndex) in mappedBy[index]:
            continue

        for i in range(len(graph[index])):
            for edgeIndex in range(len(graph[index][i])):
                if i == neighbourIndex and edgeIndex == neighbourEdgeIndex:
                    continue

                neighbourIndexIncreasing = vertexIndexIncreasing(mesh, index, i, indexIncreasing, graph)
                stack.append((i, neighbourIndexIncreasing, index, edgeIndex))

        F = copy.deepcopy(mesh[index])
        rotatedFace = deepToList(flatFaceCoordinates(F, indexIncreasing))
        rotatedFace = padPoints(rotatedFace, 2)

        origin1 = rotatedFace[0]
        origin2 = rotatedFace[1]
        target1 = rotatedFace[0]
        target2 = rotatedFace[1]
        if neighbourIndex != None:
            origin1 = rotatedFace[graph[index][neighbourIndex][0][0]]
            origin2 = rotatedFace[graph[index][neighbourIndex][0][1]]
            target1 = mappedFaces[neighbourIndex][graph[neighbourIndex][index][0][0]]
            target2 = mappedFaces[neighbourIndex][graph[neighbourIndex][index][0][1]]
            if indexIncreasing:
                target1, target2 = target2, target1
        
        matrix = translationRotationMatrix(origin1, origin2, target1, target2)
        transformedFace = applyMatrix(rotatedFace, matrix, True)

        if mappedFaces[index] != None:
            if compare(mappedFaces[index], transformedFace) != 0:
                raise UnwrapException("Shape is not unwrappable without distorion!\n(hint: consider marking some edges as seams)")
        else:
            mappedFaces[index] = transformedFace
            mappedBy[index].append((neighbourIndex, neighbourEdgeIndex))
            if neighbourIndex != None: mappedBy[neighbourIndex].append((index, edgeIndex))

    return roundList(deepToList(mappedFaces))