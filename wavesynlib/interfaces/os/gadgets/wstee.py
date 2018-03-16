# --2009.12.25 PM 09:32 Created--
# --ActivePython 2.6.4.8--
# --Author: Feng-cong Li--
# --tee.py--

from __future__ import print_function
import sys

ERROR_NOERROR, ERROR_PARAM, ERROR_FILE = range(3)

def print_usage(file = sys.stdout):
    helpstr = r'''
COMMAND | python wstee.py [OPTION]... [FILE]...

Copies standard input to each FILE, and also to standard output

Valid Options are:
-a Append output to files.
-? Print this help string and exit.

    '''
    print(helpstr, file=file)
    

if __name__ == '__main__':
    file_mode = 'w'
    file_list = []
    for arg in sys.argv[1:]:
        arg = arg.lower()
        if arg == '-a':
            file_mode = 'a'
        elif arg == '-?' or arg == '--help':
            print_usage()
            sys.exit(ERROR_NOERROR)
        elif arg[0] == '-':
            print('Incorrect Usage:', file = sys.stderr)
            print_usage(sys.stderr)
            sys.exit(ERROR_PARAM)
        else:
            try:
                file_list.append(open(arg, file_mode))
            except:
                print('Error Opening', arg, file = sys.stderr)
                sys.exit(ERROR_FILE)
    line = sys.stdin.readline()
    while line:
        for file in file_list:
            file.write(line)
        print(line, end='')
        line = sys.stdin.readline()
    sys.exit(ERROR_NOERROR)
