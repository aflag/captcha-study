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

class DigitSeparator(object):
    EMPTY = False
    NUMBER = True
    RELEVANT_LINE_THRESHOLD = 55
    NUMBER_OF_NUMBERS = 4
    
    def __init__(self, *args, **kwargs):
        super(DigitSeparator, self).__init__(*args, **kwargs)
        self.lines = {}

    def step(self, line, current_x):
        if float(sum(line))/len(line) < DigitSeparator.RELEVANT_LINE_THRESHOLD:
            self.lines[current_x] = DigitSeparator.EMPTY
        else:
            self.lines[current_x] = DigitSeparator.NUMBER

    def process(self, image):
        img_range = ImageRange(*image.getbbox())
        for x in range(img_range.x_min, img_range.x_max):
            line = []
            for y in range(img_range.y_min, img_range.y_max):
                line.append(image.getpixel((x,y)))
            self.step(line, x)

    def ranges_of_digits(self):
        ranges = []
        state = DigitSeparator.EMPTY
        for x,value in sorted(self.lines.items()):
            if value == DigitSeparator.NUMBER and state == DigitSeparator.EMPTY:
                first_digit = x
                state = DigitSeparator.NUMBER
            elif value == DigitSeparator.EMPTY and state == DigitSeparator.NUMBER:
                ranges.append((first_digit, x))
                state = DigitSeparator.EMPTY
        return sorted(ranges, key=lambda x: abs(x[1]-x[0]), reverse=True)[:DigitSeparator.NUMBER_OF_NUMBERS]

    def create_digit_image(self, num_range, image):
        width = abs(num_range[1] - num_range[0])
        height = image.size[1]
        digit_img = Image.new('L', (width,height))
        for x in range(num_range[0], num_range[1]):
            for y in range(height):
                value = image.getpixel((x,y))
                digit_img.putpixel((x-num_range[0],y), value)
        return digit_img

    def get_digit_images(self, image):
        self.process(image)
        digits = []
        for num_range in self.ranges_of_digits():
            digits.append(self.create_digit_image(num_range, image))
        return digits
