import re


def main(wavesyn, args):
    path = args[1]
    match = re.match(r"['\"]?([^'\"]*)['\"]?", path)
    path = match[1]
    wavesyn.interfaces.os.chdir(path)
