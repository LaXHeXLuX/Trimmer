import numpy as np
import math

def compare(x1, x2):
    EPSILON = 1e-6
    difference = x1-x2
    if abs(difference) < EPSILON:
        return 0
    if difference < -EPSILON:
        return -1
    if difference > EPSILON:
        return 1
    raise ArithmeticError(f"Values {x1}, {x2} don't respond to our laws of math!")

def vectorAreEqual(v1, v2):
    if len(v1) != len(v2):
        return False

    for i in range(len(v1)):
        if compare(v1[i], v2[i]) != 0:
            return False
    
    return True

def is_collinear(p1, p2, p3):
    v1 = p2 - p1
    v2 = p3 - p2

    scaled_v1 = v1 * v2[0]
    scaled_v2 = v2 * v1[0]
    return vectorAreEqual(scaled_v1, scaled_v2)

def point_is_collinear(points, index):
    # Get the three points to check
    p1 = np.array(points[(index - 1) % len(points)])  # Previous point (wrap around using modulo)
    p2 = np.array(points[index])
    p3 = np.array(points[(index + 1) % len(points)])  # Next point (wrap around using modulo)

    # Include the point if it's not collinear with its neighbors
    return is_collinear(p1, p2, p3)

def compact_points(points):
    if len(points) < 3:
        return points

    compacted = []

    for i in range(len(points)):
        if not point_is_collinear(points, i):
            compacted.append(p2)
    
    return compacted

def toDeepNumpy(arr):
    newArr = []
    for a in arr:
        newArr.append(np.array(a))
    return newArr

def get_uv_coords_for_face(uv_coords, face_coords):
    noncollinear_indexes = []
    collinear_indexes_neighbours = []
    collinearity = []

    # Sort points by collinearity
    for i in range(len(face_coords)):
        if point_is_collinear(face_coords, i):
            collinearity.append(True)
        else:
            collinearity.append(False)
            noncollinear_indexes.append(i)

    new_uv_coords = []
    for coord in uv_coords:
        new_uv_coords.append(coord)

    if len(noncollinear_indexes) == len(collinearity):
        return new_uv_coords

    print(f"collinearity: {collinearity}, noncollinear_indexes: {noncollinear_indexes}")

    # Find each point's noncollinear neighbours
    noncollinear_neighbours = []
    prevI = len(noncollinear_indexes)-1
    nextI = 0
    for i in range(len(face_coords)):
        if not collinearity[i]:
            nextI = (nextI + 1) % len(noncollinear_indexes)
            noncollinear_neighbours.append([prevI, nextI])
            prevI = (prevI + 1) % len(noncollinear_indexes)
        else:
            noncollinear_neighbours.append([prevI, nextI])
    
    print(f"noncollinear_neighbours: {noncollinear_neighbours}")

    inserted = 0
    firstEdge = True
    for i in range(len(face_coords)):
        prevI, nextI = noncollinear_neighbours[i]
        print(f"\nimportant neighbours: {noncollinear_neighbours[i]}")
        if nextI != 0: 
            firstEdge = False
        
        if not collinearity[i]:
            continue

        smallDist = math.dist(face_coords[noncollinear_indexes[prevI]], face_coords[i])
        fullDist = math.dist(face_coords[noncollinear_indexes[prevI]], face_coords[noncollinear_indexes[nextI]])
        print(f"smallDist: {smallDist}, fullDist: {fullDist}")

        uv_vector = uv_coords[nextI] - uv_coords[prevI]
        print(f"uv_vector: {uv_vector}")

        newPoint = uv_coords[prevI] + uv_vector * (smallDist / fullDist)
        print(f"newPoint: {newPoint}")
        index = (prevI + inserted + 1)
        if firstEdge and index == len(new_uv_coords): index = inserted
        print(f"index: {index}")

        new_uv_coords.insert(index, newPoint)

        inserted += 1

    return new_uv_coords

uv_coords = [
    [0, 0], 
    [4, 0], 
    [2, 3], 
    [0, 3]
]
face_coords = [
    [-2, -1, 0],
    [-1, -1, 0],
    [-0.5, -1, 0],
    [0, -1, 0], 
    [0, -1, 3],  
    [-4, -1, 3], 
    [-4, -1, 0],
    [-3, -1, 0],
    [-2.5, -1, 0]
]

arr = get_uv_coords_for_face(toDeepNumpy(uv_coords), toDeepNumpy(face_coords))
for a in arr:
    print(a)
