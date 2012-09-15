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

import sys
import re
import random
import os
import pickle
from models import *
from sklearn.externals import joblib
from image_processing import DigitSeparator

def make_train_dataset(files):
    dataset = {}
    for file_path in files:
        file_name = os.path.basename(file_path)
        labels = re.findall(r'^([0-9]+)-[0-9]+\..*$', file_name)[0]
        with open(file_path) as f:
            digits = DigitSeparator(Image.open(f).convert("L")).get_digits()
        for i,digit in enumerate(digits):
            label = int(labels[i])
            dataset[label] = dataset.get(label, [])
            dataset[label].append(digit)
    return dataset

def make_test_dataset(files):
    dataset = []
    for file_path in files:
        file_name = os.path.basename(file_path)
        label = re.findall(r'^([0-9]+)-[0-9]+\..*$', file_name)[0]
        with open(file_path) as f:
            digits = DigitSeparator(Image.open(f).convert("L")).get_digits()
        dataset.append((label, digits))
    return dataset

def get_files(base_dir):
    return map(lambda x: os.path.join(base_dir, x), os.listdir(base_dir))

def generate_datasets(base_dir):
    files = get_files(base_dir)
    random.shuffle(files)
    train_size = int(0.4*len(files))
    train = files[:train_size]
    test = files[train_size:]
    print "Number of trains:", len(train), "Number of tests:", len(test)
    train_dataset = make_train_dataset(train)
    test_dataset = make_test_dataset(test)
    return train_dataset, test_dataset

def largest_label_size(dataset):
    return max(map(len, dataset.values()))

def test(model, test_dataset):
    matches = 0
    for labels,digits in test_dataset:
        pred_labels = model.predict(digits)
        if labels == ''.join(map(lambda x: str(int(x)), pred_labels)):
            matches += 1
    print 'Matches:', float(matches)/len(test_dataset)

def main():
    if len(sys.argv) > 2:
        train_dataset = make_train_dataset(get_files(sys.argv[1]))
    else:
        train_dataset, test_dataset = generate_datasets(sys.argv[1])
    model = RandomFlorest(train_dataset)
    if len(sys.argv) > 2:
        joblib.dump(model, sys.argv[2])
    else:
        test(model, test_dataset)

if __name__ == '__main__':
    main()
