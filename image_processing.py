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
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import Image
import ImageFilter
import ImageDraw
import ImageOps
import numpy

def _get(pix, (width,height), coord, default=0):
    x, y = coord
    if (x>=width) or (x<0) or (y>=height) or (y<0):
        return default
    else:
        return pix[x,y]

def reduce_noise(image):
    new_img = image.copy()
    width, height = image.size
    pix = image.load()
    pix2 = new_img.load()
    for x in range(width):
        for y in range(height):
            color = pix[x,y]
            if color < 127:
                pix2[x,y] = 0
            else:
                pix2[x,y] = 255
    return new_img

def reduce_lines(image):
    new_img = image.copy()
    width, height = image.size
    pix = image.load()
    pix2 = new_img.load()
    for x in range(width):
        for y in range(height):
            if x+1 >= width or pix[x+1,y] < 127:
                pix2[x,y] = 0
            elif x-1 < 0 or pix[x-1,y] < 127:
                pix2[x,y] = 0
            elif y+1 >= height or pix[x,y+1] < 127:
                pix2[x,y] = 0
            elif y-1 < 0 or pix[x,y-1] < 127:
                pix2[x,y] = 0
    return new_img

def smooth(image):
    return image.filter(ImageFilter.SMOOTH)

def thicken_lines(image):
    new_img = image.copy()
    width, height = image.size
    pix = image.load()
    pix2 = new_img.load()
    for x in range(width):
        for y in range(height):
            colors = []
            colors.append(_get(pix, image.size, (x+1,y)))
            colors.append(_get(pix, image.size, (x-1,y)))
            colors.append(_get(pix, image.size, (x,y+1)))
            colors.append(_get(pix, image.size, (x,y-1)))
            colors.append(_get(pix, image.size, (x+1,y+1)))
            colors.append(_get(pix, image.size, (x-1,y+1)))
            colors.append(_get(pix, image.size, (x+1,y-1)))
            colors.append(_get(pix, image.size, (x-1,y-1)))
            if any(map(lambda color: color > 20, colors)):
                pix2[x,y] = 255
    return new_img


class Digit(object):
    def __init__(self, image, range):
        self.image = image
        self.range = range
        self.pix = image.load()

    def get(self, coord, default=0):
        x, y = coord
        width, height = self.image.size
        if (x>=width) or (x<0) or (y>=height) or (y<0):
            return default
        else:
            return self.pix[x, y]

class DigitSeparator(object):
    EMPTY = False
    FILLED = True
    BLACK_THRESHOLD = 0.99
    NUMBER_OF_DIGITS = 4
    
    def __init__(self, image):
        self.image = image

    def __num_of_blacks(self, line):
        boundary = numpy.ndarray(len(line))
        boundary.fill(127)
        return numpy.add.reduce(numpy.greater(boundary, line))

    def __image_into_blocks(self, image):
        width, height = image.size
        blocks = []
        pix = numpy.asarray(image).transpose()
        for x in range(width):
            column = pix[x]
            if self.__num_of_blacks(column)/float(len(column)) > DigitSeparator.BLACK_THRESHOLD:
                blocks.append(DigitSeparator.EMPTY)
            else:
                blocks.append(DigitSeparator.FILLED)
        return blocks

    def __first_half(self, image, x_range):
        height = image.size[1]
        width = abs(x_range[1] - x_range[0])
        i1 = image.crop((x_range[0], 0, x_range[1], height))
        vec = numpy.zeros(image.size[0]*image.size[1])
        vec[0:i1.size[0]*i1.size[1]] = i1.getdata()
        return vec

    def __second_half(self, image, x_range):
        height = image.size[1]
        width = abs(x_range[1] - x_range[0])
        i2 = ImageOps.mirror(image.crop((x_range[0], 0, x_range[1], height)))
        vec = numpy.zeros(image.size[0]*image.size[1])
        vec[0:i2.size[0]*i2.size[1]] = i2.getdata()
        return vec

    def __symmetryc_digits_fix(self, image, ranges):
        """a little help for 0 an 8"""
        merged_ranges = []
        skip = False
        for i, range1 in enumerate(ranges):
            if skip:
                skip = False
                continue
            if i+1 < len(ranges):
                range2 = ranges[i+1]
                v1 = self.__first_half(image, range1)
                v2 = self.__second_half(image, range2)
                if numpy.linalg.norm(v1 - v2) < 2200:
                    merged_ranges.append((range1[0], range2[1]))
                    skip = True
                else:
                    merged_ranges.append(range1)
            else:
                merged_ranges.append(range1)
        return merged_ranges

    def __small_range_join(self, ranges):
        merged_ranges = []
        skip = False
        for i, range1 in enumerate(ranges):
            if skip:
                skip = False
                continue
            if i+1 < len(ranges):
                range2 = ranges[i+1]
                delta1 = abs(range1[1]-range1[0])
                delta2 = abs(range2[1]-range2[0])
                if delta1 < 18 and delta2 < 18:
                    merged_ranges.append((range1[0], range2[1]))
                    skip = True
                else:
                    merged_ranges.append(range1)
            else:
                merged_ranges.append(range1)
        return merged_ranges
        

    def __multiple_digits_fix(self, ranges):
        fixed = []
        for x_range in ranges:
            delta = abs(x_range[1]-x_range[0])
            # two digits
            if 53 < delta <= 90:
                fixed.append((x_range[0], x_range[0] + (delta/2)))
                fixed.append((x_range[0] + (delta/2), x_range[1]))
            # three digits
            elif 90 < delta <= 130:
                fixed.append((x_range[0], x_range[0]+(delta/3)))
                fixed.append((x_range[0] + (delta/3), x_range[0] + 2*(delta/3)))
                fixed.append((x_range[0] + 2*(delta/3), x_range[1]))
            # four digits
            elif delta > 130:
                fixed.append((x_range[0], x_range[0] + (delta/4)))
                fixed.append((x_range[0] + (delta/4), x_range[0] + 2*(delta/4)))
                fixed.append((x_range[0] + 2*(delta/4), x_range[0] + 3*(delta/4)))
                fixed.append((x_range[0] + 3*(delta/4), x_range[1]))
            else:
                fixed.append(x_range)
        return fixed

    def __add_margin(self, image, ranges):
        new_ranges = []
        for r in ranges:
            first = r[0]-3 if r[0]-3 >= 0 else 0
            last = r[1]+3 if r[1]+3 < image.size[0] else image.size[0]-1
            new_ranges.append((first, last))
        return new_ranges

    def __choose_ranges(self, image, ranges):
        ranges = self.__small_range_join(ranges)
        ranges = self.__symmetryc_digits_fix(image, ranges)
        ranges = self.__multiple_digits_fix(ranges)
        ranges = self.__add_margin(image, ranges)
        chosen = sorted(ranges, key=lambda x: abs(x[1]-x[0]), reverse=True)[:DigitSeparator.NUMBER_OF_DIGITS]
        chosen.sort()
        return chosen

    def __ranges(self, blocks):
        ranges = []
        state = DigitSeparator.EMPTY
        for i,value in enumerate(blocks):
            if value == DigitSeparator.FILLED and state == DigitSeparator.EMPTY:
                first_digit = i
                state = DigitSeparator.FILLED
            elif value == DigitSeparator.EMPTY and state == DigitSeparator.FILLED:
                ranges.append((first_digit, i))
                state = DigitSeparator.EMPTY
        return ranges

    def __create_image_from_range(self, num_range, image):
        height = image.size[1]
        return image.crop((num_range[0], 0, num_range[1], height))

    def get_digits(self):
        new_image = reduce_lines(reduce_noise(self.image))
        blocks = self.__image_into_blocks(new_image)
        digits = []
        ranges = self.__ranges(blocks)
        for digit_range in self.__choose_ranges(new_image, ranges):
            digits.append(Digit(self.__create_image_from_range(digit_range, new_image), digit_range))
        return digits
