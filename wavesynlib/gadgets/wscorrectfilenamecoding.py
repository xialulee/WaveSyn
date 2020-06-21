import sys
import argparse
from locale import getpreferredencoding
from tkinter.filedialog import askopenfilenames
from tkinter import Tk
from pathlib import Path



def main():
    parser = argparse.ArgumentParser('''\
Correct filename encoding.
For example, If you zipped a folder on Windows with shift-jis,
and upzipped this zip file on Windows with cp936, you'll see scrambled
filename. You can correct the filename coding by specifying
the original encoding of the filename.
''')
    parser.add_argument(
        "files",
        metavar="FILES",
        type=str,
        nargs="*",
        help="File names need to be corrected.")
    parser.add_argument(
        "-d", "--decode",
        type=str,
        help="Original code name.")

    args = parser.parse_args()

    if not args.files:
        root = Tk()
        root.withdraw()
        files = askopenfilenames()
        root.quit()
    else:
        files = args.files

    syscoding = getpreferredencoding()

    for filepath in files:
        filepath = Path(filepath)
        new_name = filepath.name.encode(
            syscoding).decode(args.decode)
        filepath.rename(filepath.parent / new_name)



if __name__ == "__main__":
    main()