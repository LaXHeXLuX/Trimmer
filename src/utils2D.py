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

def boundaryEdgeMap(boundaryEdges):
    edgeMap = {}
    for a, b in boundaryEdges:
        if a not in edgeMap:
            edgeMap[a] = []
        if b not in edgeMap:
            edgeMap[b] = []
        
        edgeMap[a].append(b)
        edgeMap[b].append(a)

    # verify edge map
    for key in edgeMap:
        if len(edgeMap[key]) != 2:
            raise Exception(f"Vertex {key} has {len(edgeMap[key])} unique sides ({edgeMap[key]}), must be 2!")

    return edgeMap

def nextBoundaryPoint(prev, current, edgeMap):
    neighbours = edgeMap[tuple(current)]
    for point in neighbours:
        if compare(point, prev) != 0:
            return point
    raise Exception(f"No next point for {current}")

def firstBoundaryPoint(polygons, edgeMap):
    for i in range(len(polygons)):
        for j in range(len(polygons[i])):
            if tuple(polygons[i][j]) in edgeMap:
                return [i, j]

def nextPolygonPoint(polygons, polygonIndex, polygonPointIndex, positiveStep = True):
    step = 1 if positiveStep else -1
    
    polygon = polygons[polygonIndex]
    return polygon[(polygonPointIndex + step) % len(polygon)]
    
def boundaryVertices(polygons, edges = None):
    if edges == None:
        edges = polygonsToEdges(polygons)
    
    boundaryEdges = [edge for edge in edges if edges[edge] == 1]
    edgeMap = boundaryEdgeMap(boundaryEdges)

    firstPolygonIndex, firstPolygonPointIndex = firstBoundaryPoint(polygons, edgeMap)
    first = tuple(polygons[firstPolygonIndex][firstPolygonPointIndex])
    boundary = [first]
    prev = first
    
    second = tuple(nextPolygonPoint(polygons, firstPolygonIndex, firstPolygonPointIndex))
    if second in edgeMap[tuple(first)]:
        current = second
    else:
        beforeFirst = nextPolygonPoint(polygons, firstPolygonIndex, firstPolygonPointIndex, positiveStep=False)
        current = nextBoundaryPoint(beforeFirst, first, edgeMap)

    while compare(current, first) != 0:
        boundary.append(current)
        prev, current = current, nextBoundaryPoint(prev, current, edgeMap)

    boundary = compactPoints(boundary)

    if len(boundary) < 3:
        raise Exception(f"Boundary {boundary} is not a polygon!")

    firstFace = compactPoints(polygons[0])
    firstFaceNormal = normal(firstFace[0], firstFace[1], firstFace[2])
    boundaryNormal = normal(boundary[0], boundary[1], boundary[2])
    if boundaryNormal != firstFaceNormal:
        boundary = [boundary[0]] + boundary[1:][::-1]
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
        arr.append(0)
    arr[index] = 1
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
    p = np.array(point)

    distances = []
    tanThetas = []

    for i in range(len(polygon)):
        vertex = np.array(polygon[i])
        v1 = vertex - p
        v1Dist = np.linalg.norm(v1)

        if compare(v1Dist, 0) == 0:
            return mvcPointOnVertex(len(polygon), i)

        nextVertex = polygon[(i+1) % len(polygon)]
        v2 = nextVertex - p
        v2Dist = np.linalg.norm(v2)

        if compare(v2Dist, 0) == 0:
            return mvcPointOnVertex(len(polygon), (i+1) % len(polygon))
        cos = np.dot(np.array(v1), np.array(v2)) / (v1Dist * v2Dist)

        if compare(cos, -1) == 0:
            return mvcPointOnEdgeWeight(len(polygon), v1Dist, v2Dist, i)

        theta = np.arccos(np.dot(v1, v2) / (v1Dist * v2Dist))

        distances.append(v1Dist)
        tanThetas.append(np.tan(theta / 2))

    weight = []
    for i in range(len(polygon)):
        prevTan = tanThetas[(i-1) % len(tanThetas)]
        tan = tanThetas[i]
        w = (prevTan + tan) / distances[i]
        weight.append(w)

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
        
        newX += weights[i] * np.array(x)
        newY += weights[i] * np.array(y)

    return [float(newX), float(newY)]

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

    if not boundByX or (boundByY and innerWidthRatio < outerWidthRatio):
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
    if len(points) == 0:
        return []

    mirroredPoints = copy.deepcopy(points)
    for i in range(len(mirroredPoints)):
        for j in range(len(mirroredPoints[i])):
            point = list(mirroredPoints[i][j])
            point[0] *= -1
            mirroredPoints[i][j] = type(mirroredPoints[i][j])(point)
    return mirroredPoints

# Rotate points

def rotatePointsFill(points, step=1):
    if len(points) == 0:
        return []
    
    boundary = boundaryVertices(points)
    step = step % len(boundary)
    weights = mvcWeights(boundary, points)
    rotatedBoundary = boundary[step:] + boundary[0:step]
    return applyMvcWeights(rotatedBoundary, weights)

def rotatePointsFit(points, degrees):
    radians = np.radians(degrees)
    sinTheta = np.sin(radians)
    cosTheta = np.cos(radians)

    R = np.array([
        [cosTheta, -sinTheta],
        [sinTheta,  cosTheta]
    ])

    return applyMatrix(points, R)