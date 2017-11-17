# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 23:29:03 2017

@author: Feng-cong Li
"""
import socket



class AbortException(Exception):
    pass



class InterruptHandler:
    def __init__(self, sockobj, check_interval, check_func):
        self.__sockobj = sockobj
        self.__interval = check_interval
        self.__check_func = check_func
        sockobj.settimeout(check_interval)
        
        
    def __check(self, func, *args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except socket.timeout:
                if self.__check_func(self):
                    break
        raise AbortException
        
        
    def recv(self, datalen):            
        return self.__check(self.__sockobj.recv, datalen)
            
            
    def send(self, data):                
        return self.__check(self.__sockobj.send, data)
