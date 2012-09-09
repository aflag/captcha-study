import sys
import Image
import os
import uuid

from processing import DigitSeparator

def main():
    image = Image.open(sys.argv[1]).convert("L")
    num_separator = DigitSeparator()
    num_separator.process(image)

    for image in num_separator.get_digit_images(image):
        with open(os.path.join(sys.argv[2],uuid.uuid4().hex + '.jpg'), 'w') as f:
            image.save(f, 'JPEG')

if __name__ == '__main__':
    main()
