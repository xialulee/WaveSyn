from __future__ import annotations

import json
import struct
import socket
from typing import Final

from .datatypes import DataHead, DataInfo
from .cryptutils import AESUtil



IV_LEN: Final = 16



def bind_port(sockobj, ip, port=None):
    if port:
        sockobj.bind((ip, port))
    else:
        port = 10000
        while True:
            try:
                sockobj.bind((ip, port))
            except socket.error:
                port += 1
                if port > 65535:
                    raise socket.error
            else:
                break
    return port



def recv_head(sockobj, password: int, aes_util: AESUtil):
    exit_flag = sockobj.recv(1)
    if exit_flag != b'\x00':
        # WaveSyn can abort a misson by sending a zero to itself.
        return True, None, 0
    head_len = struct.unpack("!I", sockobj.recv(4))[0]
    head_json = sockobj.recv(head_len).decode("utf-8")
    head_obj = DataHead(**json.loads(head_json))
    if head_obj.password != password:
        return True, None, 0

    # Receive the IV_LEN bytes of IV
    aes_util.iv = sockobj.recv(IV_LEN)
    # Receive the body of DataInfo
    encrypted_info = sockobj.recv(head_obj.info_len)
    # Decrypt using the received IV
    decrypted_info = aes_util.decrypt_text(encrypted_info)
    # Load bytes into DataInfo dataclass
    datainfo = DataInfo(**json.loads(decrypted_info))
    # (is_exit, datainfo, length of data)
    return False, datainfo, head_obj.data_len


def recv_text(sockobj, aes_util: AESUtil):
    iv, raw = recv_raw(sockobj)
    aes_util.iv = iv
    return aes_util.decrypt_text(raw)


def recv_raw(sockobj: socket.socket):
    iv = sockobj.recv(IV_LEN)

    data_list = []
    while True:
        data = sockobj.recv(8192)
        if not data:
            break
        data_list.append(data)

    return iv, b''.join(data_list)
