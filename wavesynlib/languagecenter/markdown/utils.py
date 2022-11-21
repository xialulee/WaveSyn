from __future__ import annotations

from typing import List


def table_to_code(table: List[List], head: List|None = None) -> str:
    if not head:
        head, table = table[0], table[1:]
        # table = table[1:]
    head_code = '|'.join(map(str, head))
    split_code = '|'.join(['---'] * len(head))
    rows = [head_code, split_code]
    rows.extend('|'.join(map(str, row)) for row in table)
    return '\n'.join(rows)
