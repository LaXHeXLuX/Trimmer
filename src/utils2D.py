import numpy as np
import copy

if __name__ == '__main__':
    from utils import *
else:
    from .utils import *

# Boundary vertices

def polygonsToEdges(polygons):
    edges = {}

    for poly in polygons:
        for i in range(len(poly)):
            edge = tuple(sorted((tuple(poly[i]), tuple(poly[(i + 1) % len(poly)]))))
            if edge in edges:
                edges[edge] += 1
            else:
                edges[edge] = 1

    return edges

def boundaryVertices(polygons, edges = None):
    if edges == None:
        edges = polygonsToEdges(polygons)
    
    boundaryEdges = [edge for edge in edges if edges[edge] == 1]
    edgeMap = {}
    for a, b in boundaryEdges:
        edgeMap.setdefault(a, []).append(b)
        edgeMap.setdefault(b, []).append(a)

    # verify edge map
    for key in edgeMap:
        if len(edgeMap[key]) != 2:
            raise Exception(f"Vertex {key} has {len(edgeMap[key])} unique sides, must be 2!")

    # Order the boundary edges into a continuous loop
    first = next(iter(edgeMap))
    boundary = []
    current = first
    nextVertex = -1

    while nextVertex != first:
        nextVertex = edgeMap[current][0]
        edgeMap[nextVertex].remove(current)
        boundary.append(current)
        current = nextVertex
    
    boundary = compactPoints(boundary)
    firstFace = compactPoints(polygons[0])
    firstFaceNormal = normal(firstFace[0], firstFace[1], firstFace[2])
    boundaryNormal = normal(boundary[0], boundary[1], boundary[2])
    if boundaryNormal != firstFaceNormal:
        boundary.reverse()
    return boundary

def borderingEdges(point, edges):
    borderingEdges = []
    for edge in edges:
        if point in edge:
            borderingEdges.append(edge)
    return borderingEdges

def tips(polygons, edges = None, boundary = None):
    if edges == None:
        edges = polygonsToEdges(polygons)
    if boundary == None:
        boundary = boundaryVertices(polygons, edges)
    
    tipPoints = []
    for point in boundary:
        bordering = borderingEdges(point, edges)
        if len(bordering) < 2:
            raise Exception(f"Vertex {point} only connected by {bordering}!")
        elif len(bordering) == 2:
            tipPoints.append(point)
    
    return tipPoints

# MVC

def normalise(arr):
    newArr = []
    s = sum(arr)
    for a in arr:
        newArr.append(a / s)
    return newArr

def mvcPointOnVertex(n, index):
    arr = []
    for i in range(n):
        arr.append(float(0))
    arr[index] = float(1)
    return arr

def mvcPointOnEdgeWeight(n, distance1, distance2, index1):
    arr = []
    for i in range(n):
        arr.append(0)
    
    index2 = (index1 + 1) % n
    dist = distance1 + distance2
    arr[index1] = distance2 / dist
    arr[index2] = distance1 / dist
    return arr

def mvcPointWeight(polygon, point):
    distances = []
    tanThetas = []

    for i in range(len(polygon)):
        vertex = polygon[i]
        v1 = subtract(vertex, point)
        v1Dist = distance(v1)

        if compare(v1Dist, 0) == 0:
            return mvcPointOnVertex(len(polygon), i)

        nextVertex = polygon[(i+1) % len(polygon)]
        v2 = subtract(nextVertex, point)
        v2Dist = distance(v2)

        if compare(v2Dist, 0) == 0:
            return mvcPointOnVertex(len(polygon), (i+1) % len(polygon))
        cos = np.dot(np.array(v1), np.array(v2)) / (v1Dist * v2Dist)

        if compare(cos, -1) == 0:
            return mvcPointOnEdgeWeight(len(polygon), v1Dist, v2Dist, i)

        theta = np.arccos(round(np.dot(v1, v2) / (v1Dist * v2Dist), 6))

        distances.append(v1Dist)
        tanThetas.append(np.tan(theta / 2))

    weight = []
    for i in range(len(polygon)):
        prevTan = tanThetas[(i-1) % len(tanThetas)]
        tan = tanThetas[i]
        w = (prevTan + tan) / distances[i]
        weight.append(round(w, 6))

    return normalise(weight)

def mvcWeights(polygon, points):
    weights = []
    for point in points:
        try:
            iterator = iter(point[0])
            weights.append(mvcWeights(polygon, point))
        except:
            weights.append(mvcPointWeight(polygon, point))

    return deepToList(weights)

def applyMvcWeight(polygon, weights):
    newX = 0
    newY = 0
    
    for i in range(len(polygon)):
        x, y = polygon[i]
        
        newX += weights[i] * x
        newY += weights[i] * y

    return [newX, newY]

def applyMvcWeights(polygon, weights):
    if not hasattr(weights[0], '__iter__'):
        return applyMvcWeight(polygon, weights)

    newPositions = []    
    for i in range(len(weights)):
        newPositions.append(applyMvcWeights(polygon, weights[i]))
    
    return newPositions

# Polygon containment

def minMaxCoords(points):
    minX, minY = points[0]
    maxX, maxY = points[0]
    for point in points:
        if point[0] < minX:
            minX = point[0]
        elif point[0] > maxX:
            maxX = point[0]
        if point[1] < minY:
            minY = point[1]
        elif point[1] > maxY:
            maxY = point[1]
    return [minX, minY, maxX, maxY]

def minMaxCoordsPolygons(polygons):
    minX, minY = polygons[0][0]
    maxX, maxY = polygons[0][0]

    for polygon in polygons:
        currentMinMax = minMaxCoords(polygon)
        if currentMinMax[0] < minX:
            minX = currentMinMax[0]
        if currentMinMax[1] < minY:
            minY = currentMinMax[1]
        if currentMinMax[2] > maxX:
            maxX = currentMinMax[2]
        if currentMinMax[3] > maxY:
            maxY = currentMinMax[3]

    return [minX, minY, maxX, maxY]

def containmentMatrix(innerPolygons, outerPolygon, boundByX = True, boundByY = True):
    if not boundByX and not boundByY:
        raise Exception("Cannot contain without bounds!")

    innerPolygonCoords = minMaxCoordsPolygons(innerPolygons)
    outerPolygonCoords = minMaxCoords(outerPolygon)

    innerDistanceX = innerPolygonCoords[2] - innerPolygonCoords[0]
    innerDistanceY = innerPolygonCoords[3] - innerPolygonCoords[1]
    outerDistanceX = outerPolygonCoords[2] - outerPolygonCoords[0]
    outerDistanceY = outerPolygonCoords[3] - outerPolygonCoords[1]

    innerWidthRatio = innerDistanceX / innerDistanceY
    outerWidthRatio = outerDistanceX / outerDistanceY

    if not boundByX or innerWidthRatio < outerWidthRatio:
        scale = outerDistanceY / innerDistanceY
    else:
        scale = outerDistanceX / innerDistanceX

    S = np.array([
        [scale, 0],
        [0,  scale]
    ])

    scaledOrigin = S @ innerPolygonCoords[0:2]

    T = np.eye(3)
    T[:2, :2] = S
    T[:2, 2] = outerPolygonCoords[0] - scaledOrigin[0], outerPolygonCoords[1] - scaledOrigin[1]

    return T

def transformPolygons(polygons, matrix):
    paddedPolygons = padPoints(polygons, len(matrix[0]))
    newPolygons = []
    for i in range(len(paddedPolygons)):
        newPolygons.append([])
        for vertex in paddedPolygons[i]:
            newPolygons[i].append(deepToList(matrix @ np.array(vertex)))
    return padPoints(newPolygons, len(matrix[0]) - 1)

def containedPolygons(innerPolygons, outerPolygon, boundByX = True, boundByY = True):
    matrix = containmentMatrix(innerPolygons, outerPolygon, boundByX, boundByY)
    return roundList(deepToList(transformPolygons(innerPolygons, matrix)))

def containedPolygon(innerPolygon, outerPolygon, boundByX = True, boundByY = True):
    return containedPolygons([innerPolygon], outerPolygon, boundByX, boundByY)[0]

# Mirror points

def mirrorPoints(points):
    mirroredPoints = copy.deepcopy(points)
    for i in range(len(mirroredPoints)):
        for j in range(len(mirroredPoints[i])):
            point = list(mirroredPoints[i][j])
            point[0] *= -1
            mirroredPoints[i][j] = type(mirroredPoints[i][j])(point)
    return mirroredPoints

# Testing

def runBoundaryVerticesTest():
    def testBoundaryVertices(inputPolygons, output):
        result = boundaryVertices(inputPolygons)
        if compare(result, output) != 0:
            raise Exception(f"Boundary vertice test failed: \nboundaryVertices({inputPolygons}) = {result} \nis not similar to \n{output}")

    def testTips(inputPolygons, output):
        result = tips(inputPolygons)
        if not arraysAreSimilar(result, output):
            raise Exception(f"Tips test failed: \ntips({inputPolygons}) = {result} \nis not similar to \n{output}")

    # Boundary vertices
    testBoundaryVertices(
        [[(0, 0), (0, 1), (1, 1), (1, 0)]], 
        [(0, 0), (0, 1), (1, 1), (1, 0)]
    )
    testBoundaryVertices(
        [
            [(0, 0), (0, 1), (1, 0)],
            [(0, 1), (1, 1), (1, 0)]
        ], 
        [(0, 0), (0, 1), (1, 1), (1, 0)]
    )
    testBoundaryVertices(
        [
            [(0, 0), (0, 1), (1, 1), (1, 0)],
            [(1, 1), (2, 1), (2, 0), (1, 0)]
        ], 
        [(0, 0), (0, 1), (2, 1), (2, 0)]
    )
    testBoundaryVertices(
        [
            [(2, 1), (-1, 1), (-1, 0), (-1, -1), (1, -1)], 
            [(3.7888, 0.1055), (2, 1), (1, -1), (2.7888, -1.8944)]
        ], 
        [(2, 1), (-1, 1), (-1, -1), (1, -1), (2.7888, -1.8944), (3.7888, 0.1055)]
    )

    # Tips
    testTips(
        [[(0, 0), (0, 1), (1, 1), (1, 0)]],
        [(0, 0), (0, 1), (1, 1), (1, 0)]
    )
    testTips(
        [
            [(0, 0), (0, 1), (1, 1), (1, 0)],
            [(0, 1), (0, 2), (1, 2), (1, 1)],
            [(1, 1), (1, 2), (2, 2), (2, 1)],
            [(1, 0), (1, 1), (2, 1), (2, 0)],
        ],
        [(0, 0), (0, 2), (2, 2), (2, 0)]
    )
    testTips(
        [
            [(1, 0), (0, 1), (2, 1), (2, 0)],
            [(0, 1), (0, 2), (1, 2), (2, 1)]
        ],
        [(1, 0), (0, 2), (1, 2), (2, 0)]
    )

def runMVCTest():
    def testMVC(oldPolygon, inputPoints, newPolygon, outputPoints):
        weights = mvcWeights(oldPolygon, inputPoints)
        result = applyMvcWeights(newPolygon, weights)
        if deepCompare(result, outputPoints) != 0:
            raise Exception(f"Equals test failed: {result} != {outputPoints}")

    testMVC(
        [(0, 0), (0, 1), (1, 1), (1, 0)],
        [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0.5), (0.5, 1), (1, 0.5), (0.5, 0), (0.5, 0.5), (0.2, 0.8), (0.7, 0.3)],
        [(0, 0), (0, 1), (1, 1), (1, 0)],
        [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0.5), (0.5, 1), (1, 0.5), (0.5, 0), (0.5, 0.5), (0.2, 0.8), (0.7, 0.3)]
    )
    testMVC(
        [(-2, -1), (-2, 1), (2, 1), (2, -1)],
        [(-1, 0), (0, 0), (1, 0)],
        [(-2, -1), (-2, 3), (2, 3), (2, -1)],
        [(-1, 1), (0, 1), (1, 1)]
    )
    testMVC(
        [(0, 0), (0, 2), (5, 2), (5, 0)],
        [[(0, 0), (0, 2), (1, 1), (2, 2), (2, 0)], [(2, 2), (5, 2), (5, 0), (2, 0)]],
        [(0, 0), (0, 4), (15, 4), (15, 0)],
        [[(0, 0), (0, 4), (3, 2), (6, 4), (6, 0)], [(6, 4), (15, 4), (15, 0), (6, 0)]]
    )

def runPolygonContainmentTest():
    test(
        containedPolygon, 
        [[(0, 0), (0, 1), (1, 1), (1, 0)], [(0, 0), (0, 1), (1, 1), (1, 0)]],
        [(0, 0), (0, 1), (1, 1), (1, 0)]
    )
    test(
        containedPolygon, 
        [[(0, 0), (0, 1), (1, 1), (1, 0)], [(0, 0), (0, 2), (2, 2), (2, 0)]],
        [(0, 0), (0, 2), (2, 2), (2, 0)]
    )
    test(
        containedPolygon, 
        [[(3, 0), (3, 3), (6, 3), (6, 0)], [(0, 0), (0, 1), (5, 1), (5, 0)]],
        [(0, 0), (0, 1), (1, 1), (1, 0)]
    )
    test(
        containedPolygon, 
        [[(0, 1), (1, 2), (0, 4), (3, 2), (3, 3), (4, 2), (6, 2), (5, 1), (3, 1), (2, 2), (1, 1)], [(-3, -4), (-3, 0), (0, 0), (0, -4)]],
        [(-3, -4), (-2.5, -3.5), (-3, -2.5), (-1.5, -3.5), (-1.5, -3), (-1, -3.5), (0, -3.5), (-0.5, -4), (-1.5, -4), (-2, -3.5), (-2.5, -4)]
    )
    test(
        containedPolygons, 
        [[[(2, 1), (-1, 1), (-1, 0), (-1, -1), (1, -1)], [(3.78885438, 0.10557281), (2, 1), (1, -1), (2.78885438, -1.89442719)]], [(0, 0), (0, 1), (1, 1), (1, 0)]],
        [[(0.626455, 0.604409), (0, 0.604409), (0, 0.395591), (0, 0.186773), (0.417636, 0.186773)], [(1, 0.417636), (0.626455, 0.604409), (0.417636, 0.186773), (0.791182, 0)]]
    )

def runTests():
    runBoundaryVerticesTest()

    runMVCTest()

    runPolygonContainmentTest()

    test(mirrorPoints, [[[[0]]]], [[[0]]])
    test(mirrorPoints, [[[[1, 2]]]], [[[-1, 2]]])
    test(mirrorPoints, [[[[0, 0], [0, 1], [1, 1], [1, 0]]]], [[[0, 0], [0, 1], [-1, 1], [-1, 0]]])
    test(mirrorPoints, [[[(-1, -1), (0, 1), (0, -1)], [(0, 1), (1, 1), (0, -1)]]], [[(1, -1), (0, 1), (0, -1)], [(0, 1), (-1, 1), (0, -1)]])

if __name__ == "__main__":
    runTests()