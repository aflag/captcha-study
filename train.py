import sys
import random
import os
import pickle
from models import *
from sklearn.externals import joblib

def make_datasets(train_size=20, test_size=40):
    base_dir = sys.argv[1]
    train_dataset = {}
    test_dataset = {}
    for i in range(10):
        files = os.listdir(os.path.join(base_dir, str(i)))
        files = map(lambda name: os.path.join(base_dir, str(i), name), files)
        random.shuffle(files)
        if files:
            # the largest label has 63 objects
            train_dataset[i] = files[:train_size]
            test_dataset[i] = files[train_size:test_size+train_size]
    return train_dataset, test_dataset

def test(model, test_dataset):
    matches = 0
    population = 0
    for label, values in test_dataset.items():
        labels = model.predict(values) 
        label_matches = len(filter(lambda x: x==label, labels))
        label_population = len(values)
        print label, float(label_matches)/label_population
        matches += label_matches
        population += label_population

    print 'total:', float(matches)/population

def main():
    if len(sys.argv) > 2:
        train_dataset, test_dataset = make_datasets(train_size=60, test_size=0)
    else:
        train_dataset, test_dataset = make_datasets()
    model = SVM(train_dataset)
    if len(sys.argv) > 2:
        joblib.dump(model, sys.argv[2])
    else:
        test(model, test_dataset)

if __name__ == '__main__':
    main()
