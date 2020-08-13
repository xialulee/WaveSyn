from pathlib import Path
from io import IOBase
import numpy as np
from numba import jit



def read_frame_timestamps(idx_file):
    def _read(f):
        data = np.fromfile(f, dtype=np.uint64)
        return data[7::6]
    if isinstance(idx_file, (Path, str)):
        with open(idx_file, "rb") as f:
            timestamps = _read(f)
    elif isinstance(idx_file, IOBase):
        idx_file.seek(0)
        timestamps = _read(idx_file)
    else:
        raise TypeError("Type of idx_file not supported.")
    return timestamps






def create_data_cube(adcdata_prop):
    # tx, rx, doppler, range
    nr, nd, ntx, nrx, ndev = \
        adcdata_prop.num_sample_per_chirp, \
        adcdata_prop.num_loops, \
        adcdata_prop.num_chirp_per_loop, \
        adcdata_prop.num_rx_per_device, \
        adcdata_prop.num_devices
    return np.empty([ntx, nrx*ndev, nd, nr], dtype=np.complex64)



@jit(nopython=True)
def _buf_to_cube(buf, cube, nr, nd, ntx, nrx, ndev, dev_id):
    # doppler, tx, range,   rx =>
    # tx,      rx, doppler, range
    data_length = buf.shape[0]
    page_length = nr * nd
    total_nrx   = nrx * ndev    
    book_length = page_length * total_nrx

    for i in range(data_length):
        i_range   = i % nr
        i_doppler = i // nr % nd
        i_trx     = i // page_length % total_nrx
        i_dev     = i_trx // nrx
        i_rx      = i_trx % nrx
        i_tx      = i // book_length
        cube[i] = buf[i_dev, i_doppler, i_tx, i_range, i_rx]


        
def read_frame_data(data_files, data_cube, frame_index, adcdata_prop):
    nr, nd, ntx, nrx, ndev = \
        adcdata_prop.num_sample_per_chirp, \
        adcdata_prop.num_loops, \
        adcdata_prop.num_chirp_per_loop, \
        adcdata_prop.num_rx_per_device, \
        adcdata_prop.num_devices
    frame_size = nr * nd * ntx * nrx * 4 # IQ, int16
    
    def _read(f):
        f.seek(frame_index * frame_size)
        buf = f.read(frame_size)
        arr = np.frombuffer(buf, dtype=np.int16)
        arr = np.float32(arr)
        arr = arr.view(dtype=np.complex64)
        return arr
        
    buf_list = []
        
    for dev_id, data_file in enumerate(data_files):
        if isinstance(data_file, IOBase):
            buf_list.append(_read(data_file))
        elif isinstance(data_file, (Path, str)):
            with open(data_file, "rb") as f:
               buf_list.append(_read(f))
        else:
            raise TypeError("Type of data_file not supported.")
            
    buf = np.concatenate(buf_list)

    cube = data_cube
    cube_shape = cube.shape
    cube.shape = [buf.shape[0]]
    buf.shape = [ndev, nd, ntx, nr, nrx]    
    _buf_to_cube(buf, cube, nr, nd, ntx, nrx, ndev, dev_id)
    cube.shape = cube_shape
        
        
