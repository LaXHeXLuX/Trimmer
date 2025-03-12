import numpy as np
from utils import *

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

    return deepToList(weights)

def applyMvcWeights(polygon, weights):
    newPositions = []
    
    for i in range(len(weights)):
        newX = 0
        newY = 0
        
        for j in range(len(polygon)):
            weight = weights[i][j]
            x, y = polygon[j]
            
            newX += weight * x
            newY += weight * y
        
        newPositions.append((newX, newY))
    
    return deepToList(newPositions)

def test(oldPolygon, inputPoints, newPolygon, outputPoints):
    weights = mvcWeights(oldPolygon, inputPoints)
    result = applyMvcWeights(newPolygon, weights)
    if deepCompare(result, outputPoints) != 0:
        raise Exception(f"Equals test failed: {result} != {outputPoints}")

def runtests():
    test(
        [[0, 0], [0, 1], [1, 1], [1, 0]],
        [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0.5], [0.5, 1], [1, 0.5], [0.5, 0], [0.5, 0.5], [0.2, 0.8], [0.7, 0.3]],
        [[0, 0], [0, 1], [1, 1], [1, 0]],
        [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0.5], [0.5, 1], [1, 0.5], [0.5, 0], [0.5, 0.5], [0.2, 0.8], [0.7, 0.3]]
    )
    test(
        [[-2, -1], [-2, 1], [2, 1], [2, -1]],
        [[-1, 0], [0, 0], [1, 0]],
        [[-2, -1], [-2, 3], [2, 3], [2, -1]],
        [[-1, 1], [0, 1], [1, 1]]
    )

if __name__ == "__main__":
    runtests()
    print("\nTests done\n")
