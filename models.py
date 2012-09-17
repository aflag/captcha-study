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

from features import *
from image_processing import DigitSeparator
from functools import partial

import time

from sklearn import svm
from sklearn import ensemble
from sklearn.feature_extraction import DictVectorizer


ALL_EXTRACTORS = [
        x_histogram,
        y_histogram,
        positions,
        number_of_whites,
        number_of_pixels,
        horizontal_silhouette,
        reversed_horizontal_silhouette,
        vertical_silhouette,
        reversed_vertical_silhouette,
        middle_silhouette,
        vertical_symmetry,
        horizontal_symmetry,
]

SVM_EXTRACTORS = [scale_image_down(positions)]
def svm_engine():
    return svm.SVC(kernel='poly', degree=2)

FOREST_EXTRACTORS = ALL_EXTRACTORS
def forest_engine():
    return ensemble.RandomForestClassifier(n_estimators=50, n_jobs=2)

class CaptchaDecoder(object):
    def __init__(self, *args, **kwargs):
        self.engine = svm_engine()
        self.feature_extractor = compose_extractors(SVM_EXTRACTORS)

    def fit(self, x, y):
        digits = []
        labels = []
        for image,param_labels in zip(x,y):
            separator = DigitSeparator(image)
            digits.extend(map(self.feature_extractor, separator.get_digits()))
            labels.extend(param_labels)
        self.vectorizer = DictVectorizer()
        train_array = self.vectorizer.fit_transform(digits).toarray()
        self.engine.fit(train_array, labels)

    def __make_prediction(self, image):
        separator = DigitSeparator(image) 
        features = map(self.feature_extractor, separator.get_digits())
        digits = self.vectorizer.transform(features).toarray()
        labels = self.engine.predict(digits)
        return ''.join(map(lambda x: '%d'%x, labels))

    def predict(self, x):
        if not hasattr(x, '__iter__'):
            return self.__make_prediction(x)
        else:
            prediction = []
            for image in x:
                prediction.append(self.__make_prediction(image))
            return prediction

    def score(self, data, labels):
        pred_labels = self.predict(data)
        matches = sum(map(lambda (x,y): x==y, zip(labels, pred_labels)))
        return float(matches)/len(labels)

    def get_params(self, *args, **kwargs):
        return self.engine.get_params(*args, **kwargs)
