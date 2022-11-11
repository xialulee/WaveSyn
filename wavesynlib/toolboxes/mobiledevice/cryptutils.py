from __future__ import annotations

from dataclasses import dataclass
from base64 import b64encode, b64decode

try:
    from Crypto.Cipher import AES
    from Crypto.Util import Padding
    from Crypto.Random import get_random_bytes
except ModuleNotFoundError:
    raise ModuleNotFoundError("Please install pycryptodome to use this toolbox.")


@dataclass(frozen=True)
class AESInfoB64: 
    iv:  str = ""
    key: str = ""
    
    def to_bytes(self) -> AESInfoBytes:
        return AESInfoBytes(
            iv  = b64decode(self.iv),
            key = b64decode(self.key))
    

@dataclass(frozen=True)
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
        if "IV" not in kwargs:
            iv = get_random_bytes(16)
            kwargs["IV"] = iv
        self.__aes = AES.new(*args, **kwargs)
        self.__aes_info = AESInfoBytes(iv=iv, key=key)
        

    @property
    def aes_info(self):
        return self.__aes_info
    
    
    def decrypt(self, *args, **kwargs):
        return self.__aes.decrypt(*args, **kwargs)
    

    def encrypt(self, *args, **kwargs):
        return self.__aes.encrypt(*args, **kwargs)


    def decrypt_text(self, encrypted: bytes) -> str:
        #aes = AES.new(key, AES.MODE_CBC, IV=iv)
        barr = self.__aes.decrypt(encrypted)
        barr = Padding.unpad(barr, block_size=16)
        text = barr.decode("utf-8")
        return text
    

    def encrypt_text(self, text: bytes) -> bytes:
        #aes = AES.new(key, AES.MODE_CBC, IV=iv)
        text = Padding.pad(text, block_size=16)
        barr = self.__aes.encrypt(text)
        return barr


    def decrypt_stream(self, output_stream, input_stream): 
        buflen = 65536
        last_buf = b""
        while True:
            buf = input_stream.read(buflen)
            # recvcnt += buflen
            decrypted_buf = self.__aes.decrypt(last_buf)
            if not buf:
                decrypted_buf = Padding.unpad(decrypted_buf, block_size=16)
            output_stream.write(decrypted_buf)
            if not buf:
                break
            last_buf = buf
