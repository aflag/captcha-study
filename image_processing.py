import Image
import ImageFilter
import ImageDraw
import ImageOps
from vector import EasyVector, img2vec

class ImageRange(object):
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def contains(self, x, y):
        return x < self.x_max and x >= self.x_min and y < self.y_max \
                and y >= self.y_min

def _get(image, coord, default=0):
    x, y = coord
    width, height = image.size
    if (x>=width) or (x<0) or (y>=height) or (y<0):
        return default
    else:
        return image.getpixel(coord)

def border_detection(image):
    return image.filter(ImageFilter.FIND_EDGES)

def remove_noise_block(image):
    new_img = image.copy()
    width, height = image.size
    for x in range(width):
        for y in range(height):
            squares = []
            squares.append(_get(image, (x,y)))
            squares.append(_get(image, (x,y+1)))
            squares.append(_get(image, (x+1,y)))
            squares.append(_get(image, (x+1,y+1)))
            if all(map(lambda x: x < 120, squares)):
                new_img.putpixel((x,y), 0)
            elif all(map(lambda x: x > 150, squares)):
                new_img.putpixel((x,y), 255)
    return new_img

def reduce_noise(image):
    new_img = image.copy()
    width, height = image.size
    for x in range(width):
        for y in range(height):
            color = image.getpixel((x,y))
            if color < 127:
                new_img.putpixel((x,y), 0)
            else:
                new_img.putpixel((x,y), 255)
    return new_img

def reduce_lines(image):
    new_img = image.copy()
    width, height = image.size
    for x in range(width):
        for y in range(height):
            colors = []
            colors.append(_get(image, (x+1,y)))
            colors.append(_get(image, (x-1,y)))
            colors.append(_get(image, (x,y+1)))
            colors.append(_get(image, (x,y-1)))
            if any(map(lambda color: color == 0, colors)):
                new_img.putpixel((x,y), 0)
    return new_img

def smooth(image):
    return image.filter(ImageFilter.SMOOTH)

def thicken_lines(image):
    new_img = image.copy()
    width, height = image.size
    for x in range(width):
        for y in range(height):
            colors = []
            colors.append(_get(image, (x+1,y)))
            colors.append(_get(image, (x-1,y)))
            colors.append(_get(image, (x,y+1)))
            colors.append(_get(image, (x,y-1)))
            colors.append(_get(image, (x+1,y+1)))
            colors.append(_get(image, (x-1,y+1)))
            colors.append(_get(image, (x+1,y-1)))
            colors.append(_get(image, (x-1,y-1)))
            if any(map(lambda color: color > 20, colors)):
                new_img.putpixel((x,y), 255)
    return new_img


class Digit(object):
    def __init__(self, image, range):
        self.image = image
        self.range = range

class DigitSeparator(object):
    EMPTY = False
    FILLED = True
    BLACK_THRESHOLD = 0.92
    NUMBER_OF_NUMBERS = 4
    
    def __init__(self, image):
        self.image = image

    def __num_of_blacks(self, lines):
        count = 0
        for color in lines:
            if color < 127:
                count += 1
        return count

    def __image_into_blocks(self, image):
        width, height = image.size
        blocks = {}
        for x in range(width):
            column = []
            for y in range(height):
                column.append(_get(image, (x,y)))
            if self.__num_of_blacks(column)/float(len(column)) > DigitSeparator.BLACK_THRESHOLD:
                blocks[x] = DigitSeparator.EMPTY
            else:
                blocks[x] = DigitSeparator.FILLED
        return blocks

    def __first_half(self, image, x_range):
        height = image.size[1]
        width = abs(x_range[1] - x_range[0])
        i1 = image.crop((x_range[0], 0, x_range[1], height))
        return img2vec(i1)

    def __second_half(self, image, x_range):
        height = image.size[1]
        width = abs(x_range[1] - x_range[0])
        i2 = ImageOps.mirror(image.crop((x_range[0], 0, x_range[1], height)))
        return img2vec(i2)

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
                if v1.euclidean_distance(v2) < 2200:
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
        chosen = sorted(ranges, key=lambda x: abs(x[1]-x[0]), reverse=True)[:DigitSeparator.NUMBER_OF_NUMBERS]
        chosen.sort()
        return chosen

    def __ranges(self, blocks):
        ranges = []
        state = DigitSeparator.EMPTY
        for x,value in sorted(blocks.items()):
            if value == DigitSeparator.FILLED and state == DigitSeparator.EMPTY:
                first_digit = x
                state = DigitSeparator.FILLED
            elif value == DigitSeparator.EMPTY and state == DigitSeparator.FILLED:
                ranges.append((first_digit, x))
                state = DigitSeparator.EMPTY
        return ranges

    def __create_image_from_range(self, num_range, image):
        width = abs(num_range[1] - num_range[0])
        height = image.size[1]
        digit_img = Image.new('L', (width,height))
        for x in range(num_range[0], num_range[1]):
            for y in range(height):
                value = image.getpixel((x,y))
                digit_img.putpixel((x-num_range[0],y), value)
        return digit_img

    def get_digits(self):
        new_image = reduce_lines(reduce_noise(self.image))
        blocks = self.__image_into_blocks(new_image)
        digits = []
        ranges = self.__ranges(blocks)
        for digit_range in self.__choose_ranges(new_image, ranges):
            digits.append(Digit(self.__create_image_from_range(digit_range, new_image), digit_range))
        return digits
