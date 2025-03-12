import numpy as np
import math

if __name__ == "__main__":
    x = 4
    o1 = 343 * x ** 6
    o2 = 2 * x ** 7 * math.log2(2*x)
    print(f"O1: {o1}")
    print(f"O2: {o2}")
    print(f"O2 / O1 = {o2 / o1}")