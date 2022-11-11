import json
import struct
import socket

from .datatypes import DataHead, DataInfo



class Communicator:
    def __init__(self, socket_object: socket.socket):
        self.__sockobj = socket_object
        self.__ip = None
        self.__port = None
        

    @property
    def socket_object(self):
        return self.__sockobj

    @property
    def ip(self):
        return self.__ip
    
    @property
    def port(self):
        return self.__port


    def bind_port(self, ip, port=None):
        if port:
            self.__sockobj.bind((ip, port))
        else:
            port = 10000
            while True:
                try:
                    self.__sockobj.bind((ip, port))
                except socket.error:
                    port += 1
                    if port > 65535:
                        raise socket.error
                else:
                    break
        self.__ip   = ip
        self.__port = port


    def recv_head(self, password: int, aes_util):
        sockobj = self.__sockobj
        exit_flag = sockobj.recv(1)
        if exit_flag != b'\x00':
            # WaveSyn can abort a misson by sending a zero to itself.
            return True, None, 0
        head_len = struct.unpack("!I", sockobj.recv(4))[0]
        head_json = sockobj.recv(head_len).decode("utf-8")
        head_obj = DataHead(**json.loads(head_json))
        if head_obj.password != password:
            return True, None, 0
        info_len = head_obj.info_len
        encrypted_info = sockobj.recv(info_len)
        decrypted_info = aes_util.decrypt_text(encrypted_info)
        datainfo = DataInfo(**json.loads(decrypted_info))
        return False, datainfo, head_obj.data_len



    def recv_raw(self) -> bytes:
        sockobj = self.__sockobj
        data_list = []
        while True:
            data = sockobj.recv(8192)
            if not data:
                break
            data_list.append(data)
        return b''.join(data_list)
