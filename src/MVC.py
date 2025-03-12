import numpy as np

def compare(x1, x2):
    EPSILON = 1e-8
    difference = x1-x2
    if difference < -EPSILON:
        return -1
    if difference > EPSILON:
        return 1
    return 0

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
    index2 = (index1 + 1) % n
    dist = distance1 + distance2
    for i in range(n):
        if i == index1:
            arr.append(distance1 / dist)
        elif i == index2:
            arr.append(distance2 / dist)
        else:
            arr.append(0)
    return arr

def mvcPointWeight(polygon, point):
    distances = []
    tan_thetas = []

    for i in range(len(polygon)):
        vertex = polygon[i]
        v1 = np.array(vertex) - np.array(point)
        v1_dist = np.linalg.norm(v1)

        if compare(v1_dist, 0) == 0:
            return mvcPointOnVertex(len(polygon), i)

        nextVertex = polygon[(i+1) % len(polygon)]
        v2 = np.array(nextVertex) - np.array(point)
        v2_dist = np.linalg.norm(v2)

        if compare(v2_dist, 0) == 0:
            return mvcPointOnVertex(len(polygon), (i+1) % len(polygon))
        cos = np.dot(v1, v2) / (v1_dist * v2_dist)

        if compare(cos, -1) == 0:
            return mvcPointOnEdgeWeight(len(polygon), v1_dist, v2_dist, i)

        theta = np.arccos(round(np.dot(v1, v2) / (v1_dist * v2_dist), 6))

        distances.append(v1_dist)
        tan_thetas.append(np.tan(theta / 2))

    weight = []
    for i in range(len(polygon)):
        prev_tan = tan_thetas[(i-1) % len(tan_thetas)]
        tan = tan_thetas[i]
        w = (prev_tan + tan) / distances[i]
        weight.append(round(w, 6))

    return normalise(weight)

def mvcWeights(polygon, points):
    weights = []
    for point in points:
        weights.append(mvcPointWeight(polygon, point))

    return weights

def applyMvcWeights(polygon, weights):
    new_positions = []
    
    for i in range(len(weights)):
        new_x = 0
        new_y = 0
        
        for j in range(len(polygon)):
            weight = weights[i][j]
            vertex_x, vertex_y = polygon[j]
            
            new_x += weight * vertex_x
            new_y += weight * vertex_y
        
        new_positions.append((new_x, new_y))
    
    return new_positions

def roundList(arr):
    newArr = []
    for a in arr:
        try:
            newArr.append(float(round(a, 8)))
        except:
            newArr.append(roundList(a))
    return newArr

polygon = [(0, 0), (0, 3), (10, 3), (10, 2), (1, 2), (1, 1), (10, 1), (10, 0)]
points = [(0.5, 1.5), (0.5, 2.5), (5, 0.8), (5, 2.2)]

weights = mvcWeights(polygon, points)
print(f"MVC Weights for points:")
for i in range(len(weights)):
    print(f"{roundList(points[i])}: {roundList(weights[i])}")

newPolygon = [(0, 0), (0, 10), (10, 10), (10, 9), (1, 9), (1, 1), (10, 1), (10, 0)]

newPositions = applyMvcWeights(newPolygon, weights)
rounded = roundList(newPositions)
print(f"Rounded points: {rounded}")

weights = mvcWeights(newPolygon, newPositions)
print(f"MVC Weights for points:")
for i in range(len(weights)):
    print(f"{roundList(newPositions[i])}: {roundList(weights[i])}")