#!/usr/bin/env python

import os
import sys
import win32clipboard
import getopt
import re
import msvcrt
from ctypes import sizeof
from io import BytesIO
from PIL import Image, ImageGrab

from wavesynlib.interfaces.os.windows.win32def import BITMAPFILEHEADER



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
# --2015.03.12 PM 08:55 Modified by xialulee--
#   add new function image2clipb
# --2015.03.13 PM 04:05 Modified by xialulee--
#   add --html option. Now support writing HTML string to clipboard.
# --2015.09.18 PM 02:28 Modified by xialulee--
#   add new function clipboard_to_image_file which can read image in clipboard and write it into a file. 
#   imageFileToClip now support photoshop .PSD file. 
# 
# --xialulee--

ERROR_NOERROR, ERROR_PARAM, ERROR_CLIPB, ERROR_IMAGE = range(4)
NEWLINE = re.compile(r'(?<!\r)\n')
CF_HTML = win32clipboard.RegisterClipboardFormat('HTML Format')

def clipboard_to_stream(stream, mode, code, null, html=False):
    if not code:
        code = '@' # Automatic mode.
    exitcode = ERROR_NOERROR
    win32clipboard.OpenClipboard(0)
    try:
        clipboard_format = CF_HTML if html else win32clipboard.CF_UNICODETEXT
        format_name = 'HTML' if html else 'TEXT'
        s = win32clipboard.GetClipboardData(clipboard_format)
    except TypeError:
        sys.stderr.write(f'Clipb-Error: Data in clipboard is not {format_name} FORMAT!\n')
        exitcode = ERROR_CLIPB
    else:
        if code:
            if code == '@': # Automatical encoding.
                if html: # Since most html sources are UTF-8 coded.
                    code = 'utf-8'
                else: # using sys.getfilesystemencoding().
                    code = sys.getfilesystemencoding()            

            if not isinstance(s, str):
                s = s.decode(code, 'ignore')
        if null:
            s = s[:s.index('\x00')]
        if mode == 't':
            s = s.replace('\r\n', '\n')
        stream.write(s)
    win32clipboard.CloseClipboard()
    return exitcode

def stream_to_clipboard(stream, mode, code, tee, null, html=False):
    exitcode = ERROR_NOERROR
    #s = sys.stdin.read()
    s = stream.read()
    if null:
        s = s[:s.index('\x00')]
    if mode == 't':
        s = NEWLINE.sub('\r\n', s)      
    if tee:
        #sys.stdout.write(s)
        tee.write(s)
    if code:
        if code == '@': #Automatical decoding using sys.getfilesystemencoding().
            code = sys.getfilesystemencoding()
        s = s.decode(code, 'ignore')
    
    win32clipboard.OpenClipboard(0)
    win32clipboard.EmptyClipboard()        
    if html:
        template_head    = '''Version:0.9
StartHTML:{0: 13d}
EndHTML:{1: 13d}
StartFragment:{2: 13d}
EndFragment:{3: 13d}
<HTML>
<BODY>'''
        template_tail = b'</BODY></HTML>'
        template_length = 125
        s = s.encode('utf-8')
        if len(s) >  9999999999860:
            raise Exception('content too long.')
        template_head = template_head.format(
                template_length-13,
                template_length+len(s)+14,
                template_length,
                template_length+len(s)
        )

        # On Python 3, bytes object does not have format method.
        # Hence, template_head is str type.
        # Here we have to convert it to bytes object.
        template_head = template_head.encode('utf-8')
        html_string = b''.join((template_head, s, template_tail))
        win32clipboard.SetClipboardData(CF_HTML, html_string)
    else: # not html
        if code:
            win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, s)
        else:
            win32clipboard.SetClipboardText(s)        
    win32clipboard.CloseClipboard()
    return exitcode


def image_to_clipboard(image):
    bio = BytesIO()
    image.convert('RGB').save(bio, 'BMP')
    data = bio.getvalue()[sizeof(BITMAPFILEHEADER):]
    bio.close()
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    finally:
        win32clipboard.CloseClipboard()


def image_file_to_clipboard(fileObj, is_psd=False):
    '''Read an image file and write the image data into clipboard.
See http://stackoverflow.com/questions/7050448/write-image-to-windows-clipboard-in-python-with-pil-and-win32clipboard
'''
    from psd_tools  import PSDImage

    if is_psd:
        psd = PSDImage.from_stream(fileObj)
        image = psd.as_PIL()
    elif isinstance(fileObj, Image.Image):
        image = fileObj
    else:
        image = Image.open(fileObj)
    image_to_clipboard(image)
        
        
def clipboard_to_image_file(file_path):
    image = ImageGrab.grabclipboard()
    if image:
        image.save(file_path)
        return True
    else:
        return False
        
        
def get_clipboard_file_list():
    file_list = None
    win32clipboard.OpenClipboard()
    try:
        file_list = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
    finally:
        win32clipboard.CloseClipboard()
    return file_list
        
        
def get_clipboard_format():
    win32clipboard.OpenClipboard()
    format_code = win32clipboard.EnumClipboardFormats(0)
    win32clipboard.CloseClipboard()
    return format_code
    


def usage():
    perr    = sys.stderr.write
    perr('Usage: {0} [options]\n'.format(os.path.split(sys.argv[0])[-1]))
    perr('Copy clipboard to stdout or copy stdin to cliboard\n')
    perr('\n')
    perr(' -r, --read\t\tcopy clipboard to stdout\n')
    perr(' -w, --write\t\tcopy stdin to clipboard\n')
    perr(
''' -i,
 --imagefile=FILENAME\tread an image file specified by FILENAME
\t\t\tand put it into clipboard if "-w" is specified.\n'''
)
    perr(
''' -t, --text\t\ttranslate \\r\\n into \\n when copy clipboard to stdout
\t\t\tand \\n to \\r\\n when copy stdin to clipboard\n'''
)
    perr(''' --html\t\t\tput string to clipboard in HTML format \n\t\t\tif -w is specified
\t\t\tcopy string from clipboard to stdout in HTML format 
\t\t\tif -r is specified\n''')
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
            'htrwTNd:e:i:', \
            ['help', 'text', 'read', 'write', 'tee', 'null', 'decode=', 'encode=', 'imagefile=', 'html'] \
        )
    except getopt.GetoptError as err:
        sys.stderr.write(str(err)+'\n')
        usage()
        sys.exit(ERROR_PARAM)

    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        
    rw      = ''
    im      = False
    mode    = None
    html    = False
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
        if o in ('--html'):
            html    = 'html'
        if o in ('-d', '--decode'):
            code    = a
        if o in ('-e', '--encode'):
            code    = a
        if o in ('-r', '--read'):
            rw      = 'r'
        if o in ('-w', '--write'):
            rw      = 'w'
        if o in ('-T', '--tee'):
            tee     = sys.stdout
        if o in ('-N', '--null'):
            null    = True
        if o in ('-i', '--imagefile'):
            im          = True
            filename    = a

    if rw == 'r':
        if im:
            if clipboard_to_image_file(filename) is False:
                exitcode = ERROR_IMAGE
            else:
                exitcode = ERROR_NOERROR
        else:
            exitcode    = clipboard_to_stream(sys.stdout, mode, code, null, html)
        sys.exit(exitcode)
    elif rw == 'w':
        if im:
            is_psd = True if os.path.splitext(filename)[-1].lower() == '.psd' else False
            with open(filename, 'rb') as f:
                image_file_to_clipboard(f, is_psd)
            exitcode    = ERROR_NOERROR
        else:
            exitcode    = stream_to_clipboard(sys.stdin, mode, code, tee, null, html)
        sys.exit(exitcode)
    else:
        sys.stderr.write('Clipb-Error: Error parameter\n')
        sys.stderr.write('Please specify -r or -w\n\n')
        usage()
        sys.exit(ERROR_PARAM)


if __name__ == '__main__':
    main()
