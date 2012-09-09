import math

class EasyVector(object):
    def __init__(self):
        self.vec = {}

    def __setitem__(self, x, value):
        self.vec[x] = value

    def __getitem__(self, x):
        return self.vec.get(x, 0)

    def __add__(self, other):
        new_vec = EasyVector()
        new_vec.vec.update(self.vec)
        for x in other.vec:
            new_vec[x] += other.vec[x]
        return new_vec

    def __div__(self, num):
        new_vec = EasyVector()
        new_vec.vec.update(self.vec)
        for x in new_vec.vec:
            new_vec[x] /= num
        return new_vec

    def __iter__(self):
        return sorted(self.vec.keys()).__iter__()

    def __len__(self):
        return len(self.vec)

    def euclidean_distance(self, other):
        result = 0
        for x, value in other.vec.items():
            result += (self[x] - value)**2
        return math.sqrt(result)
