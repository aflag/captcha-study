import sys
import Image
import os
import uuid

from processing import DigitSeparator

def main():
    image = Image.open(sys.argv[1]).convert("L")
    num_separator = DigitSeparator(image)
    for i,image in enumerate(num_separator.get_digits()):
        img_name = '%s-%d.jpg' % (os.path.basename(sys.argv[1]), i)
        with open(os.path.join(sys.argv[2],img_name), 'w') as f:
            image.save(f, 'JPEG')

if __name__ == '__main__':
    main()
