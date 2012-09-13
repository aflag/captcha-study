import sys
import random
import os
import pickle
from models import *
from sklearn.externals import joblib

# the largest label has 80 objects
def make_datasets(train_size=20, test_size=50):
    base_dir = sys.argv[1]
    train_dataset = {}
    test_dataset = {}
    for i in range(10):
        files = os.listdir(os.path.join(base_dir, str(i)))
        files = map(lambda name: os.path.join(base_dir, str(i), name), files)
        random.shuffle(files)
        if files:
            train_dataset[i] = files[:train_size]
            test_dataset[i] = files[train_size:test_size+train_size]
    return train_dataset, test_dataset

def test(model, test_dataset):
    matches = 0
    population = 0
    per_label_matches = {}
    per_label_pop = {}
    for label, values in test_dataset.items():
        labels = model.predict(values) 
        for pred_l in labels:
            pred_l = int(pred_l)
            if pred_l == label:
                per_label_matches[pred_l] = per_label_matches.get(pred_l, 0) + 1
            per_label_pop[pred_l] = per_label_pop.get(pred_l, 0) + 1
        matches += len(filter(lambda x: x==label, labels))
        population += len(values)

    for label in sorted(per_label_matches):
        print label, float(per_label_matches[label])/per_label_pop[label]

    print 'total:', float(matches)/population

def main():
    if len(sys.argv) > 2:
        train_dataset, test_dataset = make_datasets(train_size=70, test_size=0)
    else:
        train_dataset, test_dataset = make_datasets()
    model = RandomForest(train_dataset)
    if len(sys.argv) > 2:
        joblib.dump(model, sys.argv[2])
    else:
        test(model, test_dataset)

if __name__ == '__main__':
    main()
