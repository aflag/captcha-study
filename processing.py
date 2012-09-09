import Image
from vector import EasyVector

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
    new_img = image.copy()
    width, height = new_img.size
    MARGIN = 1
    for x in range(width):
        for y in range(height):
            x_gradient = _get(image, (x-MARGIN, y)) - _get(image, (x+MARGIN, y))
            y_gradient = _get(image, (x, y-MARGIN)) - _get(image, (x, y+MARGIN))
            new_img.putpixel((x,y), max(x_gradient, y_gradient))
    return new_img

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

class Digit(object):
    def __init__(self, image, range):
        self.image = image
        self.range = range

class DigitSeparator(object):
    EMPTY = False
    NUMBER = True
    BLACK_THRESHOLD = 0.85
    NUMBER_OF_NUMBERS = 4
    
    def __init__(self, image):
        self.image = image

    def __num_of_blacks(self, lines):
        count = 0
        for color in lines:
            if color < 160:
                count += 1
        return count

    def __image_into_blocks(self, image):
        img_range = ImageRange(*image.getbbox())
        blocks = {}
        for x in range(img_range.x_min, img_range.x_max):
            lines = []
            for y in range(img_range.y_min, img_range.y_max):
                lines.append(_get(image, (x,y)))
                lines.append(_get(image, (x-1,y)))
                lines.append(_get(image, (x+1,y)))
            if self.__num_of_blacks(lines)/float(len(lines)) > DigitSeparator.BLACK_THRESHOLD:
                blocks[x] = DigitSeparator.EMPTY
            else:
                blocks[x] = DigitSeparator.NUMBER
        return blocks

    def __y_histogram(self, image, x_range):
        histogram = EasyVector()
        for y in range(image.size[1]):
            for x in range(x_range[0], x_range[1]):
                histogram[y] += _get(image, (x,y))
        return histogram

    def __simetric_digits_fix(self, image, ranges):
        merged_ranges = []
        # A little help for 0 an 8
        for i, range1 in enumerate(ranges):
            for range2 in ranges[i+1:i+2]:
                v1 = self.__y_histogram(image, range1)
                v2 = self.__y_histogram(image, range2)
                if v1.euclidean_distance(v2) < 4000:
                    merged_ranges.append((range1[0], range2[1]))
        for main_range in ranges:
            if not any(map(lambda r: r[0] <= main_range[0] <= r[1] or r[0] <= main_range[1] <= r[1], merged_ranges)):
                merged_ranges.append(main_range)
        return merged_ranges

    def __multiple_digits_fix(self, image, ranges):
        fixed = []
        for x_range in ranges:
            delta = abs(x_range[1]-x_range[0])
            if delta > 50:
                fixed.append((x_range[0], x_range[0]+(delta/2)))
                fixed.append((x_range[0]+(delta/2)+1, x_range[1]))
            else:
                fixed.append(x_range)
        return fixed

    def __choose_ranges(self, image, ranges):
        ranges = self.__simetric_digits_fix(image, ranges)
        ranges = self.__multiple_digits_fix(image, ranges)
        return sorted(ranges, key=lambda x: abs(x[1]-x[0]), reverse=True)[:DigitSeparator.NUMBER_OF_NUMBERS]

    def __ranges(self, blocks):
        ranges = []
        state = DigitSeparator.EMPTY
        for x,value in sorted(blocks.items()):
            if value == DigitSeparator.NUMBER and state == DigitSeparator.EMPTY:
                first_digit = x
                state = DigitSeparator.NUMBER
            elif value == DigitSeparator.EMPTY and state == DigitSeparator.NUMBER:
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
        new_image = remove_noise_block(self.image)
        blocks = self.__image_into_blocks(new_image)
        digits = []
        ranges = self.__ranges(blocks)
        for digit_range in self.__choose_ranges(new_image, ranges):
            digits.append(Digit(self.__create_image_from_range(digit_range, new_image), digit_range))
        return digits
