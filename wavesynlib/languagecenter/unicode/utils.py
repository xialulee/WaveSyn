from typing import Final

from toolz import interleave



__DECO: Final = {
    'strikethrough': "\u0335", 
    'overline':      "\u0305",
    'underline':     "\u0332",
    'hat':           "\u0302"
}


def decorate_text(text: str, arg: str) -> str:
    return ''.join(interleave((text, __DECO[arg] * len(text))))
