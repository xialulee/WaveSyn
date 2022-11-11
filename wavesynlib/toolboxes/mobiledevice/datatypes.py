
from dataclasses import dataclass



@dataclass
class Command:
    action: str = ""
    target: str = ""
    source: str = ""
    name:   str = ""
    
    
@dataclass
class DataHead:    
    password: int = 0
    info_len: int = 0
    data_len: int = 0


@dataclass
class DataInfo: 
    manufacturer: str = ""
    model:        str = ""
    filename:     str = ""


