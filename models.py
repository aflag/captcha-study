from features import *
from functools import partial
from sklearn import naive_bayes
from sklearn import tree
from sklearn import linear_model
from sklearn.neighbors.nearest_centroid import NearestCentroid

class ScikitWrapper(object):
    def __init__(self, engine, features_to_use, dataset):
        self.feature_handler = FeatureHandler(
                use_features(features_to_use),
                dataset)
        self.engine = engine
        self.engine.fit(*self.feature_handler.sklearn_format_train())

    def predict(self, items):
        return self.engine.predict(self.feature_handler.sklearn_format_test(items))

def NaiveBayes(dataset):
    return ScikitWrapper(naive_bayes.MultinomialNB(), [positions], dataset)

def DecisionTree(dataset):
    return ScikitWrapper(tree.DecisionTreeRegressor(), [positions], dataset)

def SGD(dataset):
    return ScikitWrapper(linear_model.SGDClassifier(loss="hinge", penalty="l2"), [positions], dataset)

def NN(dataset):
    return ScikitWrapper(NearestCentroid(), [positions, number_of_pixels, number_of_whites], dataset)
