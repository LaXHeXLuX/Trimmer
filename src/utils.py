import numpy as np

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

    return deepCompare(scaled_v1, scaled_v2) == 0

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

    return compactPoints(np.array(boundary))
