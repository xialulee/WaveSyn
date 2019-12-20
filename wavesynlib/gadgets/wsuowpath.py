#!/usr/bin/python3

# Mainly used in command substitution.

import sys
import argparse
import pathlib
from functools import reduce
from operator import truediv



def _driver_convert(driver):
    name = driver[:driver.find(":")]
    return pathlib.PurePosixPath(f"/mnt/{name}")



def _w2u(path):
    path = pathlib.PureWindowsPath(path)
    if path.is_absolute():
        parts = path.parts
        p0 = _driver_convert(parts[0])
        p1 = parts[1:]
    else:
        # To-Do: This code only supports running on Linux.
        # Please add Windows support.
        p0 = pathlib.Path(".").absolute()
        p1 = path.parts
    return str(reduce(truediv, [p0, *p1]))



def main(args):
    parser = argparse.ArgumentParser(
        description="Convert Windows path to UoW path.")
    parser.add_argument('path', metavar='path', type=str, help='The given path.')
    args = parser.parse_args(args)
    path = args.path
    path = pathlib.PureWindowsPath(path)
    print(_w2u(path))



if __name__ == "__main__":
    main(sys.argv[1:])
