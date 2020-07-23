import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def Distance(self, p2):
        if p2 is None:
            return 0
        return math.sqrt((self.x-p2.x)*(self.x-p2.x) +
                         (self.y-p2.y)*(self.y-p2.y))

