import re
from wavesynlib.languagecenter.python.pattern import string as string_pattern



word_pattern = r"(?P<WORD>[^\s'\"]+)"
item_pattern = f"{string_pattern}|{word_pattern}"
item_prog = re.compile(item_pattern, re.S)
