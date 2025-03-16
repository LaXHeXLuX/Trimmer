import numpy as np

# standard utilities

coefficient = 6

def compare(x1, x2):
    try:
        EPSILON = 10 ** -coefficient
        difference = x1-x2
        if abs(difference) < EPSILON:
            return 0
        if difference < -EPSILON:
            return -1
        if difference > EPSILON:
            return 1
        raise ArithmeticError(f"Values {x1}, {x2} don't respond to our laws of math!")
    except:
        if x1 == x2:
            return 0
        else:
            return 1

def deepCompare(a1, a2):
    try:
        if len(a1) != len(a2):
            return -1
        
        for i in range(len(a1)):
            elementCompare = deepCompare(a1[i], a2[i])
            if elementCompare > 0:
                return 1
            if elementCompare < 0:
                return -1
        return 0
    except:
        return compare(a1, a2)

def deepToList(arr):
    try:
        arrToList = []
        for a in arr:
            try:
                arrToList.append(a.tolist())
            except:
                arrToList.append(deepToList(a))
        return arrToList
    except:
        return arr

def roundList(arr):
    newArr = []
    for a in arr:
        try:
            newArr.append(round(a, coefficient))
        except:
            newArr.append(roundList(a))
    return newArr

def isCollinear(p1, p2, p3):
    v1 = p2 - p1
    v2 = p3 - p2

    for i in range(len(v1)):
        if v1[i] != 0 or v2[i] != 0:
            return deepCompare(v1 * v2[i], v2 * v1[i]) == 0

    return deepCompare(v1, v2) == 0

def pointIsCollinear(points, index):
    p1 = points[(index - 1) % len(points)]
    p2 = points[index]
    p3 = points[(index + 1) % len(points)]

    return isCollinear(p1, p2, p3)

def compactPoints(points):
    if len(points) < 3:
        return points

    compacted = []

    for i in range(len(points)):
        if not pointIsCollinear(points, i):
            compacted.append(points[i])
    
    return compacted

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

def boundaryVertices(polygons):
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
        boundary.append(list(current))
        current = nextVertex

    return deepToList(compactPoints(np.array(boundary)))

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
        v1 = np.array(vertex) - np.array(point)
        v1Dist = np.linalg.norm(v1)

        if compare(v1Dist, 0) == 0:
            return mvcPointOnVertex(len(polygon), i)

        nextVertex = polygon[(i+1) % len(polygon)]
        v2 = np.array(nextVertex) - np.array(point)
        v2Dist = np.linalg.norm(v2)

        if compare(v2Dist, 0) == 0:
            return mvcPointOnVertex(len(polygon), (i+1) % len(polygon))
        cos = np.dot(v1, v2) / (v1Dist * v2Dist)

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

# Testing

def test(operation, inputs, output):
    result = operation(*inputs)
    if deepCompare(result, output) != 0:
        raise Exception(f"Test failed with {operation.__name__}({inputs}) = {result} != {output}")

def testMVC(oldPolygon, inputPoints, newPolygon, outputPoints):
    weights = mvcWeights(oldPolygon, inputPoints)
    result = applyMvcWeights(newPolygon, weights)
    if deepCompare(result, outputPoints) != 0:
        raise Exception(f"Equals test failed: {result} != {outputPoints}")

def runBoundaryVerticesTest():
    test(
        boundaryVertices, 
        [[[[0, 0], [0, 1], [1, 1], [1, 0]]]], 
        [[0, 0], [0, 1], [1, 1], [1, 0]]
    )
    test(
        boundaryVertices, 
        [[
            [[0, 0], [0, 1], [1, 0]],
            [[0, 1], [1, 1], [1, 0]]
        ]], 
        [[0, 0], [0, 1], [1, 1], [1, 0]]
    )
    test(
        boundaryVertices, 
        [[
            [[0, 0], [0, 1], [1, 1], [1, 0]],
            [[1, 1], [2, 1], [2, 0], [1, 0]]
        ]], 
        [[0, 0], [0, 1], [2, 1], [2, 0]]
    )

def runMVCTest():
    testMVC(
        [[0, 0], [0, 1], [1, 1], [1, 0]],
        [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0.5], [0.5, 1], [1, 0.5], [0.5, 0], [0.5, 0.5], [0.2, 0.8], [0.7, 0.3]],
        [[0, 0], [0, 1], [1, 1], [1, 0]],
        [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0.5], [0.5, 1], [1, 0.5], [0.5, 0], [0.5, 0.5], [0.2, 0.8], [0.7, 0.3]]
    )
    testMVC(
        [[-2, -1], [-2, 1], [2, 1], [2, -1]],
        [[-1, 0], [0, 0], [1, 0]],
        [[-2, -1], [-2, 3], [2, 3], [2, -1]],
        [[-1, 1], [0, 1], [1, 1]]
    )
    testMVC(
        [[0, 0], [0, 2], [5, 2], [5, 0]],
        [[[0, 0], [0, 2], [1, 1], [2, 2], [2, 0]], [[2, 2], [5, 2], [5, 0], [2, 0]]],
        [[0, 0], [0, 4], [15, 4], [15, 0]],
        [[[0, 0], [0, 4], [3, 2], [6, 4], [6, 0]], [[6, 4], [15, 4], [15, 0], [6, 0]]]
    )

def runTests():
    # compare
    test(compare, [1, 1], 0)
    test(compare, [-10e100, 10e100], -1)
    test(compare, [2, 0], 1)

    # deepCompare
    test(deepCompare, [0, 0], 0)
    test(deepCompare, [[1, 2, 3], [1, 2, 3]], 0)
    test(deepCompare, [[1, 2, 3], [1, 2, 4]], -1)
    test(deepCompare, [[[], 2, [[0], 5]], [[], 2, [[0], 5]]], 0)
    test(deepCompare, [[[], 2, [[1], 5]], [[], 2, [[0], 5]]], 1)

    # roundList
    test(roundList, [[1]], [1])
    test(roundList, [[0, 0.999999999, 2.000000001]], [0, 1, 2])

    polygon = [[0, 0], [1, 2], [2, 4], [2, 3], [2, 1], [2, 0], [1, 0]]

    # pointIsCollinear
    test(pointIsCollinear, [np.array(polygon), 0], False)
    test(pointIsCollinear, [np.array(polygon), 1], True)

    # compactPoints
    test(
        compactPoints, 
        [np.array([[0, 0], [2, 4], [2, 0]])], 
        [[0, 0], [2, 4], [2, 0]]
    )
    test(
        compactPoints, 
        [np.array([[0, 0], [1, 2], [2, 4], [2, 3], [2, 1], [2, 0], [1, 0]])], 
        [[0, 0], [2, 4], [2, 0]]
    )

    runBoundaryVerticesTest()

    runMVCTest()


if __name__ == "__main__":
    runTests()