import sys
from pathlib import Path

from wavesynlib.gadgets.wswhich import which
from wavesynlib.interfaces.os.windows.wsl import winpath_to_wslpath



python_path  = winpath_to_wslpath(Path(which("python")[0]))
gadgets_path = Path(__file__).parent



def make_wsl_alias(gadget_name):
    if gadget_name == "wsguicd":
        gadget_name = "wspathselector.py"
        command = " ".join([
            r'cd \"\$(',
            f"'{python_path.as_posix()}'",
            f"'{(gadgets_path/gadget_name).as_posix()}'",
            "--dir",
            "--wsl",
            r"| sed 's/\r//g'",
            r')\"' ])
        command = f'alias wsguicd="{command}"'
        return command



def main(argv):
    print(make_wsl_alias(argv[1]))



if __name__ == "__main__":
    main(sys.argv)
