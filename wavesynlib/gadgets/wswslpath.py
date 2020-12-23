#!/usr/bin/python3

# Mainly used in command substitution.

import sys
import argparse
import pathlib
from functools import reduce
from operator import truediv
import platform



def _driver_convert(driver):
    name = driver[:driver.find(":")].lower()
    return pathlib.PurePosixPath(f"/mnt/{name}")




def _w2l(path):
    path = pathlib.PureWindowsPath(path)
    if path.is_absolute():
        parts = path.parts
        p0 = _driver_convert(parts[0])
        p1 = parts[1:]
    else:
        p0 = pathlib.Path(".").absolute()
        p1 = path.parts
        if platform.system() == "Windows":
            pa = p0.parts
            p0 = _driver_convert(pa[0])
            p1 = [*pa[1:], *p1]
    return str(reduce(truediv, [p0, *p1]))



def main(args):
    parser = argparse.ArgumentParser(
        description="Convert Windows path to wsl linux path.")
    parser.add_argument('path', metavar='path', type=str, help='The given path.')
    args = parser.parse_args(args)
    path = args.path
    path = pathlib.PureWindowsPath(path)
    try:
        print(_w2l(path))
    except TypeError:
        print("OS not supported.", file=sys.stderr)
        sys.exit(1)



if __name__ == "__main__":
    main(sys.argv[1:])
