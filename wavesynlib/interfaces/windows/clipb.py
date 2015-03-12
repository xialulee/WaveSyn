#!/usr/bin/env python

import os
import sys
import win32clipboard
import getopt
import re
import msvcrt

# --2009.10.16 PM 04:00 Created by xialulee--
#   accept /r and /w for copy clipboard to stdout and copy stdin to clipboard respectively
# --2009.11.09 PM 09:00 Modified by xialulee--
#   add /t for translating \r\n and \n
# --2009.11.15 PM 01:25 Modified by xialulee--
#   add /u for unicode format
# --2009.12.08 PM 12:26 Modified by xialulee--
#   output error message to stderr
# --2011.01.11 PM 04:30 Modified by xialulee--
#   rewrite
#   use getopt to parse parameters
#   modify parameters styles (/r -> -r for example, from Windows style to Linux style)
#   add "#!/usr/bin/env python" for msys
# --2011.01.19 AM 00:08 Modified by xialulee--
#   set stdout and stdin as binary mode using msvcrt.setmode,
#     otherwise the \n will always translate into \r\n
# --2011.01.19 AM 09:49 Modified by xialulee--
#   add -N, --null option, indicate to discard the bytes behind the null character
# --2011.01.19 AM 10:47 Modified by xialulee--
#   add -e, --encode option, indicate to encode the unicode string comes from clipboard
#
# --ActivePython2.6.6.15--
# --xialulee--

ERROR_NOERROR, ERROR_PARAM, ERROR_CLIPB = range(3)
NEWLINE = re.compile(r'(?<!\r)\n')

def clipb2stdout(mode, code, null):
    exitcode = ERROR_NOERROR
    win32clipboard.OpenClipboard(0)
    try:
        s = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except TypeError:
        sys.stderr.write('Clipb-Error: Data in clipboard is not TEXT FORMAT!\n')
        exitcode = ERROR_CLIPB
    else:
        if code:
            s = s.encode(code, 'ignore')
        if null:
            s = s[:s.index('\x00')]
        if mode == 't':
            s = s.replace('\r\n', '\n')
        sys.stdout.write(s)
    win32clipboard.CloseClipboard()
    return exitcode

def stdin2clipb(mode, code, tee, null):
    exitcode = ERROR_NOERROR
    s = sys.stdin.read()
    if null:
        s = s[:s.index('\x00')]
    if mode == 't':
        s = NEWLINE.sub('\r\n', s)        
    if tee:
        sys.stdout.write(s)
    if code:
        s = s.decode(code, 'ignore')
    win32clipboard.OpenClipboard(0)
    win32clipboard.EmptyClipboard()
    if code:
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, s)
    else:
        win32clipboard.SetClipboardText(s)        
    win32clipboard.CloseClipboard()
    return exitcode


def usage():
    perr    = sys.stderr.write
    perr('Usage: {0} [options]\n'.format(os.path.split(sys.argv[0])[-1]))
    perr('Copy clipboard to stdout or copy stdin to cliboard\n')
    perr('\n')
    perr(' -r, --read\t\tcopy clipboard to stdout\n')
    perr(' -w, --write\t\tcopy stdin to clipboard\n')
    perr(
''' -t, --text\t\ttranslate \\r\\n into \\n when copy clipboard to stdout
\t\t\tand \\n to \\r\\n when copy stdin to clipboard\n'''
)
    perr(' -T, --tee\t\twhen -w is specifed, copy stdin to clipboard and stdout\n')
    perr(' -N, --null\t\tdiscard the bytes behind the null character\n')
    perr(
''' -d, --decode=CODE\tusing the CODE to decode text from stdin and copy it to
\t\t\tclipboard using CF_UNICODETEXT format
\t\t\tfor example, use -dgbk or --decode=gbk to handle
\t\t\tChinese simplified characters
''')
    perr(
''' -e, --encode=CODE\tusing the code to encode the unicode string from
\t\t\tclipboard and copy it to stdout
\t\t\tfor example, use -egbk or --encode=gbk to handle
\t\t\tChinese simplified characters
''')
    perr(' -h, --help\t\tdisplay this help and exit\n')

def main():
    try:
        opts, args  = getopt.getopt(sys.argv[1:], \
            'htrwTNd:e:', \
            ['help', 'text', 'read', 'write', 'tee', 'null', 'decode=', 'encode='] \
        )
    except getopt.GetoptError, err:
        sys.stderr.write(str(err)+'\n')
        usage()
        sys.exit(ERROR_PARAM)

    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        
    rw      = ''
    mode    = None
    code    = ''
    tee     = None
    null    = False
    # parse options
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            exit(ERROR_NOERROR)
        if o in ('-t', '--text'):
            mode    = 't'
        if o in ('-d', '--decode'):
            code    = a
        if o in ('-e', '--encode'):
            code    = a
        if o in ('-r', '--read'):
            rw      = 'r'
        if o in ('-w', '--write'):
            rw      = 'w'
        if o in ('-T', '--tee'):
            tee     = True
        if o in ('-N', '--null'):
            null    = True

    if rw == 'r':
        exitcode    = clipb2stdout(mode, code, null)
    elif rw == 'w':
        exitcode    = stdin2clipb(mode, code, tee, null)
    else:
        sys.stderr.write('Clipb-Error: Error parameter\n')
        sys.stderr.write('Please specify -r or -w\n\n')
        usage()
        sys.exit(ERROR_PARAM)


if __name__ == '__main__':
    main()