# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 19:34:50 2016

@author: Feng-cong Li

Originally posted on http://blog.sina.com.cn/s/blog_4513dde60100metg.html.
2010.10.18.
"""
from __future__ import division

import zlib
import struct
from six import StringIO
from copy import deepcopy
import math
import numpy as np

import numba


class Decoder:
    def __init__(self, filename=None):
        self.__pixel_width = {
            0: 1, # Each pixel is a grayscale sample.
            2: 3, # Each pixel is an R, G, B triple.
            3: 1, # Each pixel is a palette index.
            4: 2, # Each pixel is a grayscale sample, followed by an alpha.
            6: 4  # Each pixel is RGB plus alpha.
        }
        if not filename:
            return
        self.open(filename)
       
    def open(self, filename):
        pixel_width = self.__pixel_width  
        
        def read(f, N):
            bytes = f.read(N)
            if bytes == '':
                raise EOFError
            return bytes
        
        def get_ihdr_info(data):
            '''get information of png file which is contained in the IHDR chunk
                data:   IHDR chunk Chunk Data
                return value:   information'''
            result = struct.unpack('!iiBBBBB', data)
            # struct{
            #   int32 width;
            #   int32 height;
            #   uint8 bit_depth;
            #   uint8 color_type;
            #   uint8 compression_method;
            #   uint8 filter_method;
            #   uint8 interlace_method;
            # }
            info = {}
            prop = ['width', 'height', 'bit depth', \
                    'color type', 'compression method', \
                    'filter method', 'interlace method']
            for idx, item in enumerate(prop):
                info[item] = result[idx]
            return info
        
        def calcbpp(ihdr_info):          
            return int(ihdr_info['bit depth']/8.0*
                       pixel_width[ihdr_info['color type']] + 0.5)
        
        self.__filename = filename
        self.__chunks   = []
        with open(filename, 'rb') as f:
            pngsig = read(f, 8)
            if pngsig != '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
                return None
            ihdr_len    = struct.unpack('!I', read(f, 4))[0]
            chunk_type  = read(f, 4)
            if chunk_type != 'IHDR':
                return None
            chunk_data = read(f, ihdr_len)
            self.__ihdr_info = get_ihdr_info(chunk_data)
            self.__bpp = calcbpp(self.ihdr_info)
            ihdr_crc = read(f, 4)
            while True:
                try:
                    chunk       = {}
                    chunk_len   = read(f, 4)
                    try:
                        chunk_len   = struct.unpack('!I', chunk_len)[0]
                    except TypeError:
                        break
                    chunk['len']       = chunk_len
                    chunk['type']      = read(f, 4)
                    chunk['data pos']  = f.tell()
                    f.seek(chunk_len, 1)
                    chunk['crc']       = read(f, 4)
                    self.__chunks.append(chunk)
                except EOFError:
                    break

    def decode(self):
        width = self.ihdr_info['width']
        height = self.ihdr_info['height']
        bit_depth = self.ihdr_info['bit depth']    
        color_type = self.ihdr_info['color type']
        pixel_width = self.__pixel_width
        
        def ifilter0(m, N, buf, bpp):
            '''Type 0: No filter'''
            return 

        @numba.jit
        def ifilter1(m, N, buf, bpp):
            '''Type 1: Inverse Sub filter'''
            for k in range(bpp, N):
                buf[m, k] += buf[m, k-bpp]
                buf[m, k] &= 0xff

        @numba.jit
        def ifilter2(m, N, buf, bpp):
            '''Type 2: Inverse Up filter'''
            buf[m, :] += buf[(m-1), :]
            buf[m, :] &= 0xff

        @numba.jit
        def ifilter3(m, N, buf, bpp):
            '''Type 3: Inverse Average filter'''
            for k in range(bpp):
                buf[m, k] += buf[(m-1), k] // 2
                buf[m, k] &= 0xff
            for k in range(bpp, N):
                buf[m, k] += (buf[m, (k-bpp)] + buf[(m-1), k]) // 2
                buf[m, k] &= 0xff
        
        @numba.jit
        def predictor(a, b, c):
            '''Helper function for ifilter4.
a = left, b = above, c = upper left.'''
            p = a + b -c
            pa = abs(p - a)
            pb = abs(p - b)
            pc = abs(p - c)
            if pa <= pb and pa <= pc:
                return a
            elif pb <= pc:
                return b
            else:
                return c    

        @numba.jit
        def ifilter4(m, N, buf, bpp):
            '''Type 4: Inverse Paeth filter'''
            for k in range(bpp):
                buf[m, k] += buf[(m-1), k]
                buf[m, k] &= 0xff
            for k in range(bpp, N):
                buf[m, k] += predictor(buf[m, (k-bpp)], buf[(m-1), k], buf[(m-1), (k-bpp)])
                buf[m, k] &= 0xff

        def ifilter(byte_stream):
            '''inverse filter
                before: decompressed data stream
                width:  width of the image
                height: height of the image
                return value: data stream which has been inverse filtered'''

            bwidth = int(math.ceil(width * bit_depth * pixel_width[color_type] / 8.0))
            bpp = self.__bpp
            filter_list = [ifilter0, ifilter1, ifilter2, ifilter3, ifilter4]
            buf = np.empty((height+1, bwidth+1), dtype=np.int)
            buf[0, :] = 0
            buf[1:, :] = np.reshape(np.fromstring(byte_stream, dtype=np.ubyte), (height, bwidth+1))
            for m in range(1, height+1):
                filter_type = buf[m, 0]
                if filter_type == 0: continue
                filter_list[filter_type](m, bwidth, buf[:, 1:], bpp)
            byte_mtx = np.empty((height, bwidth), dtype=np.ubyte)
            byte_mtx[:, :] = buf[1:, 1:]
            return byte_mtx

        def split_byte(b, width):
            mask = 2**width - 1
            li = []
            for k in range(8//width):
                li.append(b & mask)
                b >>= width
            li.reverse()
            return li

        def bytes_to_pixels(mtx, bit_depth, img_width):
#            if bit_depth < 8:
#                for idx, line in enumerate(mtx):
#                    pixels = []
#                    for B in line:
#                        pixels.extend(split_byte(B, bit_depth))
#                    pixels = pixels[:img_width]
#                    mtx[idx] = pixels
#            if bit_depth == 16:
#                for idx, line in enumerate(mtx):
#                    pixels = []
#                    for k in range(img_width):
#                        pixels.append(line[2*k]*2**8 + line[2*k+1])
#                    mtx[idx] = pixels
            if bit_depth == 8:
                return mtx
            if bit_depth == 16:
                return mtx.view(np.ushort) # reinterpret_cast 
            else:
                raise NotImplementedError

        com_stream = StringIO()
        with open(self.__filename, 'rb') as f:
            for chunk in self.__chunks:
                if chunk['type'] == 'IDAT':
                    f.seek(chunk['data pos'])
                    com_stream.write(f.read(chunk['len']))
        byte_stream = zlib.decompress(com_stream.getvalue())
        pix_mtx = ifilter(byte_stream)
        pix_mtx = bytes_to_pixels(pix_mtx, bit_depth, width)
        

        
        pixel_type = np.ubyte if bit_depth <=8 else np.ushort
        
        pix_mtx = np.array(pix_mtx, dtype=pixel_type)
        pix_mtx.shape = (height, width, pixel_width[color_type])
        return pix_mtx

    @property
    def filename(self):
        return self.__filename
        
    @property
    def ihdr_info(self):
        return deepcopy(self.__ihdr_info)

    @property
    def chunks(self):
        return deepcopy(self.__chunks)