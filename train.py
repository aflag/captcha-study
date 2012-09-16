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

import sys
import random

from models import *
from sklearn.externals import joblib
from image_processing import DigitSeparator

from dataset import load_captcha_dataset

def generate_datasets(base_dir):
    dataset = load_captcha_dataset(base_dir)
    ziped_dataset = zip(*dataset)
    random.shuffle(ziped_dataset)
    dataset = zip(*ziped_dataset)
    train_size = int(0.4*len(ziped_dataset))
    train_dataset = (dataset[0][:train_size], dataset[1][:train_size])
    test_dataset = (dataset[0][train_size:], dataset[1][train_size:])
    print "Number of trains:", len(train_dataset), "Number of tests:", len(test_dataset)
    return train_dataset, test_dataset

def largest_label_size(dataset):
    return max(map(len, dataset.values()))

def main():
    if len(sys.argv) > 2:
        train_dataset = load_captcha_dataset(sys.argv[1])
    else:
        train_dataset, test_dataset = generate_datasets(sys.argv[1])
    t0 = time.time()
    model = CaptchaDecoder(train_dataset[0], train_dataset[1])
    print 'Train time:', time.time() - t0
    if len(sys.argv) > 2:
        joblib.dump(model, sys.argv[2])
    else:
        t0 = time.time()
        print 'Matches:', model.score(test_dataset[0], test_dataset[1])
        print 'Test time:', time.time() - t0

if __name__ == '__main__':
    main()
