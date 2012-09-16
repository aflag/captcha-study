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

import Image
import ImageOps
import numpy
from vector import EasyVector
from image_processing import border_detection, reduce_noise

class FeatureHandler(object):
    def __init__(self, strategy, training_dataset):
        self.strategy = strategy
        self.dataset = {}
        self.feature_names = set()
        for label, values in training_dataset.items():
            self.dataset[label] = self.__extract_vectors(values)
            for features in self.dataset[label]:
                self.feature_names.update(features)
        self.feature_names = list(self.feature_names)
        self.inverted_feature_names = {}
        for i,name in enumerate(self.feature_names):
            self.inverted_feature_names[name] = i

    def __extract_vectors(self, values):
        return map(self.strategy, values)

    def __format_vector(self, vector):
        new_item = [0.0]*len(self.feature_names)
        for feature_name,feature_value in vector.items():
            feature_position = self.inverted_feature_names.get(feature_name)
            if feature_position is not None:
                new_item[feature_position] = feature_value
        return new_item

    def sklearn_format_train(self):
        labels = []
        vectors = []
        for label,values in self.dataset.items():
            for vector in values:
                vectors.append(self.__format_vector(vector))
                labels.append(label)
        return vectors,labels

    def sklearn_format_test(self, items):
        vecs = self.__extract_vectors(items)
        vectors = []
        for vector in vecs:
            vectors.append(self.__format_vector(vector))
        return vectors

def border(callback):
    return lambda digit,features: callback(border_detection(digit), features, prefix='border-')

def noiseless(callback):
    return lambda digit,features: callback(reduce_noise(digit), features, prefix='noiseless-')

def is_white(color):
    return color > 230

def x_histogram(digit, features, prefix=''):
    width,height = digit.image.size
    for x in range(width):
        for y in range(height):
            features[prefix+"x-histogram-"+str(x)] += digit.pix[x,y]

def y_histogram(digit, features, prefix=''):
    width,height = digit.image.size
    for y in range(height):
        for x in range(width):
            features[prefix+'y-histogram-'+str(y)] += digit.pix[x,y]

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


class use_features(object):
    def __init__(self, features_to_use):
        self.features_to_use = features_to_use

    def __call__(self, arg):
        features = EasyVector()
        if isinstance(arg, str):
            file_path = arg
            with open(file_path) as f:
                image = Image.open(f).convert("L")
        else:
            image = arg
        for feature in self.features_to_use:
            feature(image, features)
        return features
