# List operations

def distance(v):
    dist2 = 0
    for el in v:
        dist2 += el ** 2
    return dist2 ** 0.5

def multiply(v, scalar):
    if not hasattr(v, '__iter__'):
        return v * scalar
    
    scaledArr = []
    for el in v:
        scaledArr.append(multiply(el, scalar))

    return scaledArr

def add(v1, v2):
    if len(v1) > len(v2):
        v1, v2 = v2, v1
    
    v3 = []
    for i in range(len(v1)):
        v3.append(v1[i] + v2[i])
    for j in range(len(v1), len(v2)):
        v3.append(v2[j])

    return v3

def subtract(arr1, arr2):
    return add(arr1, multiply(arr2, -1))

def normalise(v):
    return multiply(v, 1 / distance(v))

def crossProduct(v1, v2):
    if len(v1) == 2 and len(v2) == 2:
        return [0, 0, v1[0] * v2[1] - v1[1] * v2[0]]

    if len(v1) != len(v2):
        raise Exception(f"Input arrays ({v1}, {v2}) must be of equal length!")

    if len(v1) != 3 or len(v2) != 3:
        raise Exception(f"Input arrays ({v1}, {v2}) must be length 2 or 3!")
    
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

# Standard utilities

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

def deepCompare(a1, a2, checkType = False):
    try:
        if checkType and type(a1) != type(a2):
            return -1

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
    v1 = subtract(p2, p1)
    v2 = subtract(p3, p2)

    for i in range(len(v1)):
        if v1[i] != 0 or v2[i] != 0:
            return deepCompare(multiply(v1, v2[i]), multiply(v2, v1[i])) == 0

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

def padPoints(points, limit):
    if not hasattr(points, '__iter__'):
        return points     
    
    if not any(hasattr(el, '__iter__') for el in points):
        padded = tuple(points[:limit]) + (1,) * max(0, limit - len(points))
        return type(points)(padded)

    return type(points)([padPoints(el, limit) for el in points])

def normal(P1, P2, P3):
    V1 = subtract(P2, P1)
    V2 = subtract(P3, P2)
    normal = crossProduct(V1, V2)

    if distance(normal) > 0:
        normal = normalise(normal)
        
    return normal

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
        raise Exception(f"Test failed with {operation.__name__}({inputs}) = \n{result} \n!= \n{output}")

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
    test(padPoints, [[[0, 1, 2, 3]], 2], [[0, 1]])
    test(padPoints, [[()], 2], [(1, 1)])
    test(padPoints, [[[(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]], 2], [[(0, 0), (0, 0), (0, 1), (0, 1)]])
    test(padPoints, [[[[], (0, 0), [1, 2, 3], (0, 2, 4, 6)]], 2], [[[1, 1], (0, 0), [1, 2], (0, 2)]])

if __name__ == "__main__":
    runTests()