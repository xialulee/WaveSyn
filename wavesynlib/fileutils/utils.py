from __future__ import annotations

from io import IOBase

import hashlib


def calc_hash(
        fileobj: IOBase, 
        algorithm: str
    ) -> str:
    algo = getattr(hashlib, algorithm.lower())()

    while True:
        data = fileobj.read(1048576)
        if data:
            algo.update(data)
        else:
            return algo.hexdigest()
