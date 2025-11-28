import math

def distance(obj1, obj2):
    return math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)
