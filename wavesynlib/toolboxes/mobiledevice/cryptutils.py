from __future__ import annotations

from dataclasses import dataclass
from base64 import b64encode, b64decode
from typing import Final

try:
    from Crypto.Cipher import AES
    from Crypto.Util import Padding
    from Crypto.Random import get_random_bytes
except ModuleNotFoundError:
    raise ModuleNotFoundError("Please install pycryptodome to use this toolbox.")


IV_LEN: Final = 16


@dataclass
class AESInfoB64: 
    iv:  str = ""
    key: str = ""
    
    def to_bytes(self) -> AESInfoBytes:
        return AESInfoBytes(
            iv  = b64decode(self.iv),
            key = b64decode(self.key))
    

@dataclass
class AESInfoBytes:
    iv:  bytes = b""
    key: bytes = b""

    def to_b64(self) -> AESInfoB64:
        return AESInfoB64(
            iv  = b64encode(self.iv).decode(),
            key = b64encode(self.key).decode())
        


class AESUtil: 
    def __init__(self, *args, **kwargs):
        if "key" not in kwargs:
            key = get_random_bytes(32)
            kwargs["key"] = key
#        if "IV" not in kwargs:
#            iv = get_random_bytes(16)
#            kwargs["IV"] = iv
        # self.__aes = AES.new(*args, **kwargs)
        self.__aes_info = AESInfoBytes(key=key)
        

    @property
    def aes_info(self):
        return self.__aes_info


    @property
    def key(self) -> bytes:
        return self.__aes_info.key

    @key.setter
    def key(self, val: bytes):
        self.__aes_info.key = val

    @property
    def iv(self) -> bytes:
        return self.__aes_info.iv

    @iv.setter
    def iv(self, val: bytes):
        self.__aes_info.iv = val
    
    
#    def decrypt(self, *args, **kwargs):
#        return self.__aes.decrypt(*args, **kwargs)
#    
#
#    def encrypt(self, *args, **kwargs):
#        return self.__aes.encrypt(*args, **kwargs)


    def decrypt_text(self, encrypted: bytes) -> str:
        aes = AES.new(
            self.__aes_info.key, 
            AES.MODE_CBC, 
            IV=self.__aes_info.iv)
        decrypted = aes.decrypt(encrypted)
        decrypted = Padding.unpad(decrypted, block_size=16)
        text = decrypted.decode("utf-8")
        return text
    

    def encrypt_text(self, text: bytes) -> bytes:
        aes = AES.new(
            self.__aes_info.key, 
            AES.MODE_CBC, 
            IV=self.__aes_info.iv)
        text = Padding.pad(text, block_size=16)
        encrypted = aes.encrypt(text)
        return encrypted


    def decrypt_stream(self, output_stream, input_stream): 
        aes = AES.new(
            self.__aes_info.key, 
            AES.MODE_CBC, 
            IV=self.__aes_info.iv)
        buflen = 65536
        last_buf = b""
        while True:
            buf = input_stream.read(buflen)
            # recvcnt += buflen
            decrypted_buf = aes.decrypt(last_buf)
            if not buf:
                decrypted_buf = Padding.unpad(decrypted_buf, block_size=16)
            output_stream.write(decrypted_buf)
            if not buf:
                break
            last_buf = buf
