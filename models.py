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

from features import *
from functools import partial
from sklearn import naive_bayes
from sklearn import tree
from sklearn import linear_model
from sklearn import svm
from sklearn import ensemble
from sklearn.neighbors.nearest_centroid import NearestCentroid
from sklearn import decomposition

class ScikitWrapper(object):
    def __init__(self, engine, features_to_use, dataset):
        self.feature_handler = FeatureHandler(
                use_features(features_to_use),
                dataset)
        self.engine = engine
        vector, labels = self.feature_handler.sklearn_format_train()
        self.engine.fit(vector, labels)

    def predict(self, items):
        return self.engine.predict(self.feature_handler.sklearn_format_test(items))

def NaiveBayes(dataset):
    return ScikitWrapper(naive_bayes.MultinomialNB(), [reversed_horizontal_silhouette, horizontal_silhouette], dataset)

def DecisionTree(dataset):
    return ScikitWrapper(tree.DecisionTreeRegressor(), [positions, reversed_horizontal_silhouette, horizontal_silhouette], dataset)

def SGD(dataset):
    return ScikitWrapper(linear_model.SGDClassifier(loss="hinge", penalty="l2"), [positions, reversed_horizontal_silhouette, horizontal_silhouette], dataset)

def SVM(dataset):
    return ScikitWrapper(svm.SVC(kernel='poly', degree=2), [positions, number_of_pixels], dataset)

def NN(dataset):
    return ScikitWrapper(NearestCentroid(), [positions, reversed_horizontal_silhouette, horizontal_silhouette], dataset)

def RandomFlorest(dataset):
    return ScikitWrapper(ensemble.RandomForestClassifier(n_estimators=300, n_jobs=8), [x_histogram, y_histogram, positions, number_of_whites, number_of_pixels, horizontal_silhouette, reversed_horizontal_silhouette, vertical_silhouette, reversed_vertical_silhouette, middle_silhouette, vertical_symmetry, horizontal_symmetry], dataset)
