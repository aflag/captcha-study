import sys
import random
import os
from models import *

def make_datasets():
    base_dir = sys.argv[1]
    train_dataset = {}
    test_dataset = {}
    for i in range(10):
        files = os.listdir(os.path.join(base_dir, str(i)))
        files = map(lambda name: os.path.join(base_dir, str(i), name), files)
        random.shuffle(files)
        if files:
            # the largest label has 63 objects
            train_dataset[i] = files[:20]
            test_dataset[i] = files[20:63]
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
    train_dataset, test_dataset = make_datasets()
    model = NN(train_dataset)
    test(model, test_dataset)

if __name__ == '__main__':
    main()
