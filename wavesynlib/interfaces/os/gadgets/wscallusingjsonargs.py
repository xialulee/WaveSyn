import re
import sys
import json
import winreg
import subprocess

from numpy import byte

from wavesynlib.interfaces.os.gadgets.wswhich import which



def main(argv):
    s = argv[1]
    s = s.split()
    s = list(map(int, s))
    s = byte(s)
    s = b''.join(s)
    s = s.decode('utf-16')
    arg_list = json.loads(s)

    try:
        subprocess.call(arg_list)
    except FileNotFoundError:
        app = arg_list[0]
        # Only the name of the python script is given.
        app = which(app)[0]
        ext = app.suffix
        prog = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, ext)
        comkey = winreg.OpenKey(
                winreg.HKEY_CLASSES_ROOT, 
                rf'\{prog}\Shell\Open\Command')
        try:
            comstr = winreg.QueryValueEx(comkey, '')[0]
            items = re.findall(r'"[^"]+"|\S+', comstr)
        finally:
            winreg.CloseKey(comkey)
        new_list = [items[0].replace('"', '')]
        for item in items[1:]:
            item = item.replace('"', '')
            if item == '%1':
                new_list.append(str(app))
            elif item == '%*':
                new_list.extend(arg_list[1:])
            else:
                new_list.append(item)
        subprocess.call(new_list)



if __name__ == '__main__':
    main(sys.argv)

