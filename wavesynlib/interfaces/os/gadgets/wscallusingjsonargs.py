import sys
import json
import subprocess
from numpy import byte



def main(argv):
    s = argv[1]
    s = s.split()
    s = list(map(int, s))
    s = byte(s)
    s = b''.join(s)
    s = s.decode('utf-16')
    arg_list = json.loads(s)
    subprocess.call(arg_list)



if __name__ == '__main__':
    main(sys.argv)

