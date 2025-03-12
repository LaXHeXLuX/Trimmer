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
            return False
        
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
