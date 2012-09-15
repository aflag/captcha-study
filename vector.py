# Copyright (C) 2012 Rafael Cunha de Almeida <rafael@kontesti.me>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X
# CONSORTIUM BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import math

def img2vec(image):
    vec = EasyVector()
    width, height = image.size
    pix = image.load()
    for x in range(width):
        for y in range(height):
            vec[x*height + y] += pix[x,y]
    return vec

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

    def __str__(self):
        return str(self.vec)

    def __repr__(self):
        return repr(self.vec)

    def euclidean_distance(self, other):
        result = 0
        for x, value in other.vec.items():
            result += (self[x] - value)**2
        return math.sqrt(result)
