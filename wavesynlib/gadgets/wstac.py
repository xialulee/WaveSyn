import sys
from argparse import ArgumentParser



def reverse(fileobj, separator='\n'):
    data = fileobj.read()
    datalist = data.split(separator)
    for idx in range(len(datalist))[::-1]:
        yield datalist[idx]



def main():
    parser = ArgumentParser(description='''\
Write each FILE to standard output, last line first
''')
    parser.add_argument(
        'files', 
        metavar='FILE', 
        type=str, 
        nargs='*',
        help='Write each FILE to standard output, last line first')
    parser.add_argument(
        '-s', '--separator',
        type=str,
        help='use SEPARATOR as the separator instead of newline')
    parser.add_argument(
        '-b', '--before',
        action='store_true',
        help='attach the separator before instead of after')

    args = parser.parse_args()
    
    if args.separator:
        end = args.separator.encode().decode('unicode_escape')
    else:
        end = '\n'

    files = list(args.files)
    if not files:
        files.append('-')

    for filepath in files:
        if filepath == '-':
            fileobj = sys.stdin
        else:
            fileobj = open(filepath, 'r')

        try:
            for line in reverse(fileobj, separator=end):
                if args.before:
                    print(end, line, sep='', end='')
                else:
                    print(line, end=end) 
        finally:
            if fileobj != sys.stdin:
                fileobj.close()


if __name__ == '__main__':
    sys.exit(main())
    
