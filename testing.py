from src.utils import add, subtract, multiply, applyMatrix, compare, roundList, pointIsCollinear, compactPoints, padPoints
from src.utils2D import boundaryVertices, mvcWeights, applyMvcWeights, containedPolygon, containedPolygons, mirrorPoints, rotatePointsFill, rotatePointsFit
from src.multiple_face_unwrap import unwrap, UnwrapException

# Testing utilities

def test(operation, inputs, output):
    if operation == None:
        result = inputs
        messagePart = f"{inputs} "
    else:
        result = operation(*inputs)
        messagePart = f"{operation.__name__}({inputs}) = \n{result} "

    if compare(result, output) != 0:
        raise Exception(f"Test failed with {messagePart}\n!= \n{output}")

# utils

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

def runApplyMatrixTest():
    import numpy as np
    identity = np.array([[1, 0], [0, 1]])
    rightAngle = np.array([[0, -1], [1, 0]])
    scale3 = np.array([[3, 0], [0, 3]])
    translation = np.array([[1, 0, 1], [0, 1, 1], [0, 0, 1]])

    origin = [0, 0]
    test(applyMatrix, [origin, identity], origin)
    test(applyMatrix, [origin, rightAngle], origin)
    test(applyMatrix, [origin, scale3], origin)
    test(applyMatrix, [origin, translation, True], [1, 1])

    oneOne = [1, 1]
    test(applyMatrix, [oneOne, identity], oneOne)
    test(applyMatrix, [oneOne, rightAngle], [-1, 1])
    test(applyMatrix, [oneOne, scale3], [3, 3])
    test(applyMatrix, [oneOne, translation, True], [2, 2])

    square = [[0, 0], [0, 1], [1, 1], [1, 0]]
    test(applyMatrix, [square, identity], square)
    test(applyMatrix, [square, rightAngle], [[0, 0], [-1, 0], [-1, 1], [0, 1]])
    test(applyMatrix, [square, scale3], [[0, 0], [0, 3], [3, 3], [3, 0]])
    test(applyMatrix, [square, translation, True], [[1, 1], [1, 2], [2, 2], [2, 1]])

    polygon = [
        [[0, 0], [0, 1], [1, 1]],
        [[0, 0], [-1, 0], [0, 1]]
    ]
    test(applyMatrix, [polygon, identity], polygon)
    test(applyMatrix, [polygon, rightAngle], [[[0, 0], [-1, 0], [-1, 1]], [[0, 0], [0, -1], [-1, 0]]])
    test(applyMatrix, [polygon, scale3], [[[0, 0], [0, 3], [3, 3]], [[0, 0], [-3, 0], [0, 3]]])
    test(applyMatrix, [polygon, translation, True], [[[1, 1], [1, 2], [2, 2]], [[1, 1], [0, 1], [1, 2]]])

    combinedMatrix = np.array([
        [0, -3, 1],
        [3, 0, 1],
        [0, 0, 1]
    ])
    test(applyMatrix, [polygon, combinedMatrix, True], [[[1, 1], [-2, 1], [-2, 4]], [[1, 1], [1, -2], [-2, 1]]])

def testUtils():
    runListOperationTest()

    # compare
    test(compare, ["a", "b"], -1)
    test(compare, (1, 1), 0)
    test(compare, [-10e100, 10e100], -1)
    test(compare, (2, 0), 1)
    test(compare, [[1, 2, 3], [1, 2, 3]], 0)
    test(compare, [[1, 2, 3], [1, 2, 4]], -1)
    test(compare, [[[], 2, [[0], 5]], [[], 2, [[0], 5]]], 0)
    test(compare, [[[], 2, [[1], 5]], [[], 2, [[0], 5]]], 1)

    # roundList
    test(roundList, [1], 1)
    test(roundList, [[1]], [1])
    test(roundList, [[0, 0.99999999999, 2.00000000001]], [0, 1, 2])

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

    runApplyMatrixTest()

# utils2D

def runBoundaryVerticesTest():
    def testBoundaryVertices(inputPolygons, output):
        result = boundaryVertices(inputPolygons)
        if compare(result, output) != 0:
            raise Exception(f"Boundary vertice test failed: \nboundaryVertices({inputPolygons}) = {result} \nis not similar to \n{output}")
    
    testBoundaryVertices(
        [[[0, 0], [0, 1], [1, 1], [1, 0]]],
        [[0, 0], [0, 1], [1, 1], [1, 0]]
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
    testBoundaryVertices(
        [
            [(2, 1), (1, -1), (-1, -1), (-1, 0), (-1, 1)],
            [(3.7888, 0.1055), (2, 1), (1, -1), (2.7888, -1.8944)]
        ],
        [(2, 1), (3.7888, 0.1055), (2.7888, -1.8944), (1, -1), (-1, -1), (-1, 1)]
    )
    testBoundaryVertices(
        [
            [(1, 1), (1, 2), (2, 2), (2, 1)],
            [(0, 0), (0, 3), (1, 3), (1, 2),  (1, 1), (2, 1), (2, 0)],
            [(1, 2), (1, 3), (3, 3), (3, 0), (2, 0), (2, 1), (2, 2)]
        ],
        [(0, 0), (0, 3), (3, 3), (3, 0)]
    )
    testBoundaryVertices(
        [
            [(1, 1), (2, 1), (2, 2), (1, 2)],
            [(0, 0), (0, 3), (1, 3), (1, 2),  (1, 1), (2, 1), (2, 0)],
            [(1, 2), (1, 3), (3, 3), (3, 0), (2, 0), (2, 1), (2, 2)]
        ],
        [(0, 0), (3, 0), (3, 3), (0, 3)]
    )

def runMVCTest():
    def testMVC(oldPolygon, inputPoints, newPolygon, outputPoints):
        weights = mvcWeights(oldPolygon, inputPoints)
        result = applyMvcWeights(newPolygon, weights)
        if compare(result, outputPoints) != 0:
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
        [[(0.6264546303, 0.604409105), (0, 0.604409105), (0, 0.395590895), (0, 0.1867726849), (0.4176364202, 0.1867726849)], [(1, 0.4176364202), (0.6264546303, 0.604409105), (0.4176364202, 0.1867726849), (0.7911817899, 0)]]
    )
    test(
        containedPolygons,
        [[[[0, 0], [1, 0], [1, 1], [0, 1]]], [[0, 0], [5, 0], [5, 1], [0, 1]], True, False],
        [[[0, 0], [5, 0], [5, 5], [0, 5]]]
    )

def testUtils2D():
    runBoundaryVerticesTest()

    runMVCTest()

    runPolygonContainmentTest()

    test(mirrorPoints, [[]], [])
    test(mirrorPoints, [[[[0]]]], [[[0]]])
    test(mirrorPoints, [[[[1, 2]]]], [[[-1, 2]]])
    test(mirrorPoints, [[[[0, 0], [0, 1], [1, 1], [1, 0]]]], [[[0, 0], [0, 1], [-1, 1], [-1, 0]]])
    test(mirrorPoints, [[[(-1, -1), (0, 1), (0, -1)], [(0, 1), (1, 1), (0, -1)]]], [[(1, -1), (0, 1), (0, -1)], [(0, 1), (-1, 1), (0, -1)]])

    test(rotatePointsFill, [[]], [])
    test(rotatePointsFill, [[[[0, 0], [1, 0], [1, 1], [0, 1]]]], [[[1, 0], [1, 1], [0, 1], [0, 0]]])
    test(rotatePointsFill, [[[[0, 0], [0, 2], [1, 1], [2, 0], [1, 0]]]], [[[0, 2], [2, 0], [1, 0], [0, 0], [0, 1]]])
    test(rotatePointsFill, [[[[0, 0], [0, 2], [2, 2], [2, 0]], [[0, 2], [2, 4], [2, 2]]]], [[[0, 2], [2, 4], [1, 0], [0, 0]], [[2, 4], [2, 0], [1, 0]]])
    test(rotatePointsFill, [[[[0, 0], [0, 2], [2, 2], [2, 0]], [[0, 2], [2, 4], [2, 2]]], -1], [[[2, 0], [0, 0], [1, 3], [2, 4]], [[0, 0], [0, 2], [1, 3]]])

    test(rotatePointsFit, [[[[0, 0], [1, 0], [1, 1], [0, 1]]], 0], [[[0, 0], [1, 0], [1, 1], [0, 1]]])
    test(rotatePointsFit, [[[[0, 0], [1, 0], [1, 1], [0, 1]]], 90], [[[0, 0], [0, 1], [-1, 1], [-1, 0]]])
    polygon = [
        [[0, 0], [0, 1], [1, 1]],
        [[0, 0], [-1, 0], [0, 1]]
    ]
    sqrt2 = 2 ** 0.5
    expected = [
        [[0, 0], [-1 / sqrt2, 1 / sqrt2], [0, sqrt2]],
        [[0, 0], [-1 / sqrt2, -1 / sqrt2], [-1 / sqrt2, 1 / sqrt2]]
    ]
    test(rotatePointsFit, [polygon, 45], expected)

# multiple_face_unwrap

def testUnwrap(inputArr, outputArr, seams = []):
    result = unwrap(inputArr, seams)
    if compare(result, outputArr) != 0:
        raise Exception(f"Equals test failed: {result} != {outputArr}")
    
def testUnwrapFail(inputArr):
    try:
        result = unwrap(inputArr)
        raise Exception(f"Error test failed: {inputArr}")
    except UnwrapException as ue:
        pass

def testUnwrapping():
    testUnwrap(
        [[(-1, -1, 0), (-1, 1, 0), (1, 1, 0), (1, -1, 0)]],
        [[(-1, 1), (-1, -1), (1, -1), (1, 1)]]
    )
    testUnwrap(
        [[(1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1)]],
        [[(1, -1), (1, 1), (-1, 1), (-1, -1)]]
    )
    testUnwrap(
        [
            [(-1, 1, 1), (-1, -1, 1), (1, -1, 1)],
            [(-1, -1, 1), (1, -1, 1), (1, -1, -1)]
        ],
        [
            [(-1, 1), (-1, -1), (1, -1)],
            [(-1, -1), (1, -1), (1, -3)]
        ]
    )
    testUnwrapFail(
        [
            [(-1, 1, 1), (-1, -1, 1), (1, -1, 1), (1, 1, 1)],
            [(-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1)],
            [(-1, 1, 1), (-1, -1, 1), (-1, -1, -1), (1, 1, -1)]
        ]
    )
    testUnwrap(
        [
            [(-1, 1, 1), (-1, -1, 1), (1, -1, 1), (1, 1, 1)],
            [(-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1)],
            [(-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1)]
        ],
        [
            [(-1, 1), (-1, -1), (1, -1), (1, 1)],
            [(-1, -1), (1, -1), (1, -3), (-1, -3)],
            [(-1, 1), (1, 1), (1, 3), (-1, 3)]
        ]
    )
    testUnwrap(
        [
            [(1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1)],
            [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)]
        ],
        [
            [(1, -1), (1, 1), (-1, 1), (-1, -1)],
            [(-1, -1), (-1, 1), (-3, 1), (-3, -1)]
        ]
    )
    testUnwrap(
        [
            [(-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1)],
            [(1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1)]
        ],
        [
            [(-1, -1), (1, -1), (1, 1), (-1, 1)],
            [(1, -1), (3, -1), (3, 1), (1, 1)]
        ]
    )
    testUnwrap(
        [
            [(1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1)],
            [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)],
            [(1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1)]
        ],
        [
            [(1, -1), (1, 1), (-1, 1), (-1, -1)],
            [(-1, -1), (-1, 1), (-3, 1), (-3, -1)],
            [(3, -1), (3, 1), (1, 1), (1, -1)]
        ]
    )
    testUnwrap(
        [
            [(2, 1, 1), (-1, 1, 1), (-1, 0, 1), (-1, -1, 1), (1, -1, 1)],
            [(2, 1, -1), (2, 1, 1), (1, -1, 1), (1, -1, -1)]
        ],
        [
            [(2, 1), (-1, 1), (-1, 0), (-1, -1), (1, -1)],
            [(3.788854382, 0.105572809), (2, 1), (1, -1), (2.788854382, -1.894427191)]
        ]
    )
    testUnwrapFail(
        [
            [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)],
            [(0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1)]
        ]
    )
    testUnwrap(
        [[(-1, -1, -1), (-1, -1, 0), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)]],
        [[(-1, -1), (0, -1), (1, -1), (1, 1), (-1, 1)]]
    )
    testUnwrap(
        [
            [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 1, 0), (2, 0, 0), (3, 0, 0), (3, 2, 0), (0, 2, 0)],
            [(0, 0, 0), (0, 0, -1), (3, 0, -1), (3, 0, 0), (2, 0, 0), (1, 0, 0)]
        ],
        [
            [(0, 0), (1, 0), (1, 1), (2, 1), (2, 0), (3, 0), (3, 2), (0, 2)],
            [(0, 0), (0, -1), (3, -1), (3, 0), (2, 0), (1, 0)]
        ]
    )
    testUnwrap(
        [
            [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
            [(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)],
            [(0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)]
        ],
        [
            [(0, 0), (1, 0), (1, 1), (0, 1)],
            [(0, 0), (0, 1), (-1, 1), (-1, 0)],
            [(0, 0), (0, -1), (1, -1), (1, 0)]
        ],
        [(1, 2)]
    )
    cube = [
        [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        [(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)],
        [(0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)],
        [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
        [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)],
        [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]
    ]
    unwrapped = [
        [(0, 0), (1, 0), (1, 1), (0, 1)],
        [(0, 0), (0, 1), (-1, 1), (-1, 0)],
        [(0, 0), (0, -1), (1, -1), (1, 0)],
        [(0, -1), (1, -1), (1, -2), (0, -2)],
        [(1, 0), (1, 1), (2, 1), (2, 0)],
        [(0, 1), (0, 2), (1, 2), (1, 1)]
    ]
    seams = [(1, 2), (1, 3), (1, 5), (2, 4), (3, 4), (3, 5), (4, 5)]
    testUnwrap(cube, unwrapped, seams)

# metadata matches

def initInfo():
    from src import bl_info
    return bl_info

def manifestInfo(path):
    import toml
    with open(path, encoding="utf-8") as f:
        return toml.load(f)

def tupleFromToml(tomlInfo):
    return tuple(int(digit) for digit in tomlInfo.split("."))

def testMetadataMatching():
    bl_info = initInfo()
    manifest = manifestInfo("src/blender_manifest.toml")

    test(None, bl_info["name"], manifest["name"])
    test(None, bl_info["author"], manifest["maintainer"])
    test(None, bl_info["version"], tupleFromToml(manifest["version"]))
    test(None, bl_info["blender"], tupleFromToml(manifest["blender_version_min"]))

# main

def runTests():
    testUtils()
    testUtils2D()
    testUnwrapping()

    testMetadataMatching()

if __name__ == '__main__':
    runTests()