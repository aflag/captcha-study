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
from image_processing import DigitSeparator
from dataset import load_captcha_dataset

from sklearn.externals import joblib
from sklearn import cross_validation

import numpy

def main():
    dataset = load_captcha_dataset(sys.argv[1])
    model = CaptchaDecoder()
    if len(sys.argv) > 2:
        t0 = time.time()
        model.fit(dataset[0], dataset[1])
        print 'Train time:', time.time() - t0
        joblib.dump(model, sys.argv[2])
    else:
        t0 = time.time()
        scores = cross_validation.cross_val_score(model, numpy.array(dataset[0], dtype=object), dataset[1], cv=100)
        print 'Accuracy: %0.2f (+/- %0.2f)' % (scores.mean(), scores.std()/2)
        print 'Validation time:', time.time() - t0

if __name__ == '__main__':
    main()
