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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import Image
import ImageOps
import ImageFilter
import numpy

class compose_extractors(object):
    def __init__(self, extractors):
        self.extractors = extractors

    def __call__(self, arg):
        image_features = {}
        if isinstance(arg, str):
            file_path = arg
            with open(file_path) as f:
                image = Image.open(f).convert("L")
        else:
            image = arg
        for extractor in self.extractors:
            extractor(image, image_features)
        return image_features

class border(object):
    def __init__(self, callback):
        self.callback = callback

    def __border_detection(self, digit):
        digit.image = digit.image.filter(ImageFilter.FIND_EDGES)
        digit.pix = digit.image.load()
        return digit

    def __call__(self, digit, features):
        return callback(self.__border_detection(digit), features, prefix='border-')

class scale_image_down(object):
    def __init__(self, callback):
        self.callback = callback

    def __scale_down(self, digit):
        digit.image = digit.image.resize((16,16), Image.BICUBIC)
        digit.pix = digit.image.load()
        return digit

    def __call__(self, digit, features):
        return self.callback(self.__scale_down(digit), features, prefix='scaled-')

def is_white(color):
    return color > 230

def x_histogram(digit, features, prefix=''):
    width,height = digit.image.size
    pix = numpy.asarray(digit.image).transpose()
    for x in range(width):
        features[prefix+'x-histogram-'+str(x)] = numpy.add.reduce(pix[x])

def y_histogram(digit, features, prefix=''):
    width,height = digit.image.size
    pix = numpy.asarray(digit.image)
    for y in range(height):
        features[prefix+'y-histogram-'+str(y)] = numpy.add.reduce(pix[y])

def positions(digit, features, prefix=''):
    width,height = digit.image.size
    for x in range(width):
        for y in range(height):
            features[prefix+'pos-'+str(x*height + y)] = digit.pix[x,y]

def number_of_whites(digit, features, prefix=''):
    width,height = digit.image.size
    counter = 0
    for x in range(width):
        for y in range(height):
            if is_white(digit.pix[x,y]):
                counter += 1
    features[prefix+'number_of_whites'] = counter

def number_of_pixels(digit, features, prefix=''):
    width,height = digit.image.size
    features[prefix+'number_of_pixels'] = width * height

def horizontal_silhouette(digit, features, prefix=''):
    width,height = digit.image.size
    for y in range(height):
        for x in range(width):
            if is_white(digit.get((x,y))):
                  features[prefix+'horizontal_silhouette'+str(y)] = x/float(width)

def reversed_horizontal_silhouette(digit, features, prefix=''):
    width,height = digit.image.size
    for y in range(height):
        for x in reversed(range(width)):
            if is_white(digit.get((x,y))):
                  features[prefix+'reversed_horizontal_silhouette'+str(y)] = x/float(width)

def vertical_silhouette(digit, features, prefix=''):
    width,height = digit.image.size
    for x in range(width):
        for y in range(height):
            if is_white(digit.get((x,y))):
                  features[prefix+'vertical_silhouette'+str(x)] = y/float(height)

def reversed_vertical_silhouette(digit, features, prefix=''):
    width,height = digit.image.size
    for x in range(width):
        for y in reversed(range(height)):
            if is_white(digit.get((x,y))):
                  features[prefix+'reversed_vertical_silhouette'+str(x)] = y/float(height)

def middle_silhouette(digit, features, prefix=''):
    width,height = digit.image.size
    x = width / 2
    for i,y in enumerate(reversed(range(height/2))):
        if is_white(digit.get((x,y))):
            features[prefix+'middle_silhouette_a'] = i
    for i,y in enumerate(range(height/2, height)):
        if is_white(digit.get((x,y))):
            features[prefix+'middle_silhouette_b'] = i
    y = height/2
    for i,x in enumerate(reversed(range(width/2))):
        if is_white(digit.get((x,y))):
            features[prefix+'middle_silhouette_c'] = i
    for i,x in enumerate(range(width/2, width)):
        if is_white(digit.get((x,y))):
            features[prefix+'middle_silhouette_d'] = i

def vertical_symmetry(digit, features, prefix=''):
    width,height = digit.image.size
    first_half = numpy.array(digit.image.crop((0, 0, width/2, height)).getdata())
    second_half = numpy.array(ImageOps.mirror(digit.image.crop((width/2, 0, width, height)).getdata()))
    second_half = second_half[:len(first_half)]
    features[prefix+'vertical_symmetry'] = numpy.linalg.norm(first_half-second_half)

def horizontal_symmetry(digit, features, prefix=''):
    width,height = digit.image.size
    first_half = numpy.array(digit.image.crop((0, 0, width, height/2)).getdata())
    second_half = numpy.array(ImageOps.flip(digit.image.crop((0, height/2, width, height))).getdata())
    second_half = second_half[:len(first_half)]
    features[prefix+'horizontal_symmetry'] = numpy.linalg.norm(first_half-second_half)
