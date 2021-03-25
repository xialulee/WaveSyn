#!/usr/bin/python

# For termux usage:
# ln -s "this file" ~/bin/termux-file-editor

import sys
from PIL import Image
import pytesseract



def main(argv):
    path = argv[1]
    print(pytesseract.image_to_string(Image.open(path), lang="jpn"))



if __name__ == "__main__":
    try:
        main(sys.argv)
    except err:
        print(err)
    input()

