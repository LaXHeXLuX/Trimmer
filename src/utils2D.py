import numpy as np

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
    print(f"firstFaceNormal: {firstFaceNormal}")
    print(f"boundaryNormal: {boundaryNormal}")
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
    
    for j in range(len(polygon)):
        x, y = polygon[j]
        
        newX += weights[j] * x
        newY += weights[j] * y

    return [newX, newY]

def applyMvcWeights(polygon, weights):
    newPositions = []
    
    for i in range(len(weights)):
        try:
            newPositions.append(applyMvcWeights(polygon, weights[i]))
        except:
            newPositions.append(applyMvcWeight(polygon, weights[i]))
    
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

def containmentMatrix(innerPolygon, outerPolygon):
    innerPolygonCoords = minMaxCoords(innerPolygon)
    outerPolygonCoords = minMaxCoords(outerPolygon)

    innerDistanceX = innerPolygonCoords[2] - innerPolygonCoords[0]
    innerDistanceY = innerPolygonCoords[3] - innerPolygonCoords[1]
    outerDistanceX = outerPolygonCoords[2] - outerPolygonCoords[0]
    outerDistanceY = outerPolygonCoords[3] - outerPolygonCoords[1]

    innerRatio = innerDistanceX / innerDistanceY
    outerRatio = outerDistanceX / outerDistanceY

    scale = outerDistanceX / innerDistanceX
    if innerRatio < outerRatio:
        scale = outerDistanceY / innerDistanceY

    S = np.array([
        [scale, 0],
        [0,  scale]
    ])

    scaledOrigin = S @ innerPolygonCoords[0:2]

    T = np.eye(3)
    T[:2, :2] = S
    T[:2, 2] = outerPolygonCoords[0] - scaledOrigin[0], outerPolygonCoords[1] - scaledOrigin[1]

    return T

def transformPolygon(polygon, matrix):
    paddedPolygon = padPoints(polygon, len(matrix[0]))
    newPolygon = []
    for vertex in paddedPolygon:
        newPolygon.append(matrix @ vertex)
    return padPoints(newPolygon, len(matrix[0]) - 1)

def containedPolygon(innerPolygon, outerPolygon):
    matrix = containmentMatrix(innerPolygon, outerPolygon)
    return deepToList(transformPolygon(innerPolygon, matrix))

# Testing

def arraysAreSimilar(arr1, arr2):
    if len(arr1) != len(arr2):
        return False

    if arr1 == arr2:
        return True

    for i in range(len(arr1)):
        testArr = arr1[i:] + arr1[:i]
        if testArr == arr2 or testArr[::-1] == arr2:
            return True
    
    return False

def test(operation, inputs, output):
    result = operation(*inputs)
    if deepCompare(result, output) != 0:
        raise Exception(f"Test failed with {operation.__name__}({inputs}) = {result} != {output}")

def runListOperationTest():
    test(add, [[], []], [])
    test(add, [[0], [0]], [0])
    test(add, [[1], [2]], [3])
    test(add, [[1, 2], [-1, 2]], [0, 4])

    test(subtract, [[], []], [])
    test(subtract, [[0], [0]], [0])
    test(subtract, [[3], [2]], [1])
    test(subtract, [[1, 2, 3], [3, 2, 1]], [-2, 0, 2])

    test(multiply, [[], 0], [])
    test(multiply, [[], 10], [])
    test(multiply, [[0], 10], [0])
    test(multiply, [[1], 10], [10])
    test(multiply, [[1, 2, 3], 2], [2, 4, 6])

def runBoundaryVerticesTest():
    def testBoundaryVertices(inputPolygons, output):
        result = boundaryVertices(inputPolygons)
        if not arraysAreSimilar(result, output):
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
            [(3.7888543819998324, 0.10557280900008403), (2, 1), (1, -1), (2.7888543819998324, -1.8944271909999164)]
        ], 
        [(2, 1), (-1, 1), (-1, -1), (1, -1), (2.7888543819998324, -1.8944271909999164), (3.7888543819998324, 0.10557280900008403)]
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

def runTests():
    # arraysAreSimilar
    test(arraysAreSimilar, [[], []], True)
    test(arraysAreSimilar, [[], [1]], False)
    test(arraysAreSimilar, [[1], [2]], False)
    test(arraysAreSimilar, [(1, 2), (2, 1)], True)
    test(arraysAreSimilar, [[1, 2, 3], [1, 3, 2]], True)
    test(arraysAreSimilar, [[1, 2, 3, 4], [1, 3, 2, 4]], False)

    runListOperationTest()

    # compare
    test(compare, (1, 1), 0)
    test(compare, [-10e100, 10e100], -1)
    test(compare, (2, 0), 1)

    # deepCompare
    test(deepCompare, (0, 0), 0)
    test(deepCompare, [[1, 2, 3], [1, 2, 3]], 0)
    test(deepCompare, [[1, 2, 3], [1, 2, 4]], -1)
    test(deepCompare, [[[], 2, [[0], 5]], [[], 2, [[0], 5]]], 0)
    test(deepCompare, [[[], 2, [[1], 5]], [[], 2, [[0], 5]]], 1)

    # roundList
    test(roundList, [[1]], [1])
    test(roundList, [[0, 0.999999999, 2.000000001]], [0, 1, 2])

    polygon = [(0, 0), (1, 2), (2, 4), (2, 3), (2, 1), (2, 0), (1, 0)]

    # pointIsCollinear
    test(pointIsCollinear, [polygon, 0], False)
    test(pointIsCollinear, [polygon, 1], True)

    # compactPoints
    test(
        compactPoints, 
        [[(0, 0), (2, 4), (2, 0)]], 
        [(0, 0), (2, 4), (2, 0)]
    )
    test(
        compactPoints, 
        [[(0, 0), (1, 2), (2, 4), (2, 3), (2, 1), (2, 0), (1, 0)]], 
        [(0, 0), (2, 4), (2, 0)]
    )

    # padPoints
    test(padPoints, [[[0, 1, 2, 3]], 0], [[]])
    test(padPoints, [[[0, 1, 2, 3]], 2], [(0, 1)])
    test(padPoints, [[[]], 2], [(1, 1)])

    runBoundaryVerticesTest()

    runMVCTest()

    runPolygonContainmentTest()

if __name__ == "__main__":
    runTests()