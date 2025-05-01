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

def compare(a1, a2, checkType = False):
    try:
        if checkType and type(a1) != type(a2):
            return -1

        if len(a1) != len(a2):
            return -1

        if type(a1) == str or type(a2) == str:
            raise TypeError("Going ahead with strings would introduce infinite recursion!")
        
        for i in range(len(a1)):
            elementCompare = compare(a1[i], a2[i])
            if elementCompare > 0:
                return 1
            if elementCompare < 0:
                return -1
        return 0
    except TypeError:
        x1, x2 = a1, a2
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
                return -1

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
    try:
        return [roundList(a) for a in arr]
    except TypeError:
        return round(arr, coefficient)

def isCollinear(p1, p2, p3):
    v1 = subtract(p2, p1)
    v2 = subtract(p3, p2)

    for i in range(len(v1)):
        if v1[i] != 0 or v2[i] != 0:
            return compare(multiply(v1, v2[i]), multiply(v2, v1[i])) == 0

    return compare(v1, v2) == 0

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

def applyMatrix(points, matrix, translation = False):
    if not hasattr(points, '__iter__'):
        raise Exception("Parameter points must be iterable!")

    if translation:
        points = padPoints(points, len(matrix[0]))
    
    if not any(hasattr(el, '__iter__') for el in points):
        result = deepToList(matrix @ points)
    else:
        result = ([applyMatrix(el, matrix) for el in points])

    if translation:
        result = padPoints(result, len(matrix[0]) - 1)
    
    return type(points)(result)

def normal(P1, P2, P3):
    V1 = subtract(P2, P1)
    V2 = subtract(P3, P2)
    normal = crossProduct(V1, V2)

    if distance(normal) > 0:
        normal = normalise(normal)
        
    return normal