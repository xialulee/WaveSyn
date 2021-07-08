import numpy as np
import quantities as pq

import re
from pathlib import Path
import json
from dataclasses import dataclass, field

from wavesynlib.languagecenter.cutils import ctype_build, StructReader
from wavesynlib.languagecenter.nputils import NamedAxesArray
from wavesynlib.languagecenter.datatypes.physicalquantities.functions import expj2π
from wavesynlib.toolwindows.imagedisplay.ppi import Canvas, app

from ctypes import c_uint32, c_uint64

@ctype_build("struct")
class Info:
    tag:          c_uint32
    version:      c_uint32
    flags:        c_uint32
    numIdx:       c_uint32
    dataFileSize: c_uint64



def read_adc_data(directory, frame_index, index=0):
    paths = get_paths(directory)
    config = read_mmwave_json(paths["mmwave.json"])
    chirp_per_loop = config.num_loops
    num_loops = config.angles_to_steer.size
    device_names = ("master", "slave1", "slave2", "slave3")
    data_list = []
    for device_name in device_names:
        data_list.append(
            read_bin_file(
                paths["data"][index][device_name], 
                frame_index, config.sample_per_chirp, chirp_per_loop, num_loops, 4))
    data_cube = NamedAxesArray.concat(*data_list, axis="rx_elements")
    data_cube = data_cube.indexing(
        fast_time   = np.s_[:],
        slow_time   = np.s_[:],
        tx_steering = np.s_[:],
        rx_elements = config.cascade_rx_id)
    return data_cube



def signal_processing(data_cube, config):
    assert(isinstance(data_cube, NamedAxesArray))
    # Range processing
    #   Windowing along fast_time sampling
    window = hann(data_cube.shape["fast_time"])
    cube_r = data_cube.mul1d(window, axis="fast_time")
    #   FFT along fast_time sampling
    cube_r = cube_r.fft(axis="fast_time")
    cube_r.rename_axes(fast_time="range")
    # Doppler processing
    #   Windowing along slow_time sampling
    window = hann(data_cube.shape["slow_time"])
    cube_rd = cube_r.mul1d(window, axis="slow_time")
    #   FFT along slow_time sampling
    cube_rd = cube_rd.fft(axis="slow_time")
    cube_rd.rename_axes(slow_time="Doppler")
    # Rx calibration
    rx_mismatch = config.rx_mismatch[config.cascade_rx_id]
    rx_mismatch = NamedAxesArray(rx_mismatch, axis_names=("rx_elements",))
    rx_mismatch = rx_mismatch.expj().conj()
    cube_rd *= rx_mismatch
    # RX Beamforming
    for angle_index, angle in enumerate(config.angles_to_steer):
        steering = rx_steering_vector(angle, config)
        cube_angle = cube_rd.indexing(
            tx_steering = angle_index,
            rx_elements = np.s_[:],
            Doppler     = np.s_[:],
            range       = np.s_[:])
        cube_angle.imul1d(steering, axis="rx_elements")
    cube_rda = cube_rd.sum(axis="rx_elements")
    cube_rda *= cube_rda.conj()
    return cube_rda



def show_ppi(cube, config):
    ca = cube.array
    ca /= ca.max()
    delta_angle = 2 * pq.deg
    buf_width  = int((360*pq.deg / delta_angle).rescale(pq.dimensionless).magnitude)
    buf_height = config.sample_per_chirp
    buf = np.zeros((buf_height, buf_width, 3), dtype=np.uint8)
    #buf[:, :16, 1] = cube.indexing(
        #tx_steering = np.s_[15:],
        #Doppler = 0, 
        #range = np.s_[:]).array.real.T * 4096
    #buf[:, -15:, 1] = cube.indexing(
        #tx_steering = np.s_[:15],
        #Doppler = 0,
        #range = np.s_[:]).array.real.T * 4096
    buf[:, :31, 1] = cube.indexing(
        tx_steering = np.s_[:],
        Doppler = 0, 
        range = np.s_[:]).array.real.T * 4096
    canvas = Canvas(image=buf)
    app.run()



def rx_steering_vector(angle, config):
    if isinstance(angle, pq.Quantity):
        angle = angle.rescale(pq.rad).magnitude
    wx = np.sin(angle)
    d = config.cascade_rx_id
    D = config.cascade_rx_D
    a = expj2π(-wx*d*D)
    return a



def get_paths(directory):
    directory = Path(directory)
    result = {}
    result["mmwave.json"] = next(directory.glob("*.mmwave.json"))

    def get_dev_file_paths(file_type):
        regex = re.compile(rf"([^_]+)_(\d+)_{file_type}.bin")
        result[file_type] = result_file_type = {}
        for p in directory.glob(f"*_*_{file_type}.bin"):
            match = regex.match(p.name)
            device, index = match[1], match[2]
            index = int(index)
            if index not in result_file_type:
                result_file_type[index] = {}
            result_file_type[index][device] = p

    get_dev_file_paths("data")
    get_dev_file_paths("idx")

    return result



def hann(M):
    return np.hanning(M+2)[1:-1]



@dataclass
class Config:
    start_freq:         pq.Quantity = None
    chirp_slope:        pq.Quantity = None
    idle_time:          pq.Quantity = None
    adc_start_time:     pq.Quantity = None
    ramp_end_time:      pq.Quantity = None
    sampling_rate:      pq.Quantity = None
    sample_per_chirp:   int = None
    chirp_per_loop:     int = None
    num_loops:          int = None
    num_frames:         int = None
    angles_to_steer:    pq.Quantity = None
    dutycycle:          float = 0.5
    chirp_duration:     pq.Quantity = field(init=False)
    sample_per_channel: int = field(init=False)
    center_freq:        pq.Quantity = field(init=False)
    design_freq:        pq.Quantity = 76.8 * pq.GHz
    angle_per_sweep:    int = field(init=False)
    range_resolution:   pq.Quantity = field(init=False)
    cascade_rx_id:      np.ndarray = np.array([12, 13, 14 ,15 ,0 ,1 ,2 ,3 ,8 ,9 ,10 ,11 ,4 ,5 ,6 ,7])
    cascade_rx_D:       np.array = np.array([0, 1, 2, 3, 11, 12, 13, 14, 46, 47, 48, 49, 50, 51, 52, 53])
    cascade_rx_d:       float = field(init=False)
    rx_mismatch:        pq.Quantity = field(init=False)


    def __post_init__(self):
        self.chirp_duration     = self.ramp_end_time + self.idle_time
        self.angle_per_sweep    = self.angles_to_steer.size
        # !
        self.sample_per_channel = self.sample_per_chirp * self.num_loops * self.angle_per_sweep * self.num_frames
        self.center_freq        = (self.start_freq + self.sample_per_chirp/self.sampling_rate*self.chirp_slope/2).rescale(pq.GHz)
        self.range_resolution   = (3e8*pq.m/pq.s / 2 / (self.sample_per_chirp / self.sampling_rate * self.chirp_slope)).rescale(pq.m)
        self.cascade_rx_d       = (0.5*self.center_freq/self.design_freq).rescale(pq.dimensionless).magnitude
        
        with open(Path(__file__).parent/"calibration"/"rxmismatch.npy", "rb") as rxmismatch_file:
            self.rx_mismatch = np.load(rxmismatch_file) * pq.deg



def read_mmwave_json(path):
    with open(path) as f:
        jsonobj = json.loads(f.read())
    dev_id = 0
    rl_profiles = jsonobj['mmWaveDevices'][0]['rfConfig']['rlProfiles'][0]['rlProfileCfg_t']
    frame_seq   = jsonobj["mmWaveDevices"][dev_id]["rfConfig"]["rlAdvFrameCfg_t"]["frameSeq"]
    # Get properties:
    kwargs = {}
    kwargs["start_freq"]       = rl_profiles["startFreqConst_GHz"] * pq.GHz
    kwargs["chirp_slope"]      = rl_profiles["freqSlopeConst_MHz_usec"] * pq.MHz / pq.us
    kwargs["idle_time"]        = rl_profiles["idleTimeConst_usec"] * pq.us
    kwargs["adc_start_time"]   = rl_profiles["adcStartTimeConst_usec"] * pq.us
    kwargs["ramp_end_time"]    = rl_profiles["rampEndTime_usec"] * pq.us
    kwargs["sampling_rate"]    = rl_profiles["digOutSampleRate"] * pq.kHz # Unit of sampling rate in json is ksps
    kwargs["sample_per_chirp"] = rl_profiles["numAdcSamples"]
    kwargs["num_loops"]        = frame_seq['subFrameCfg'][0]['rlSubFrameCfg_t']['numLoops']
    kwargs["num_frames"]       = frame_seq["numFrames"]
    kwargs["angles_to_steer"]  = np.arange(-30, 31, 2) * pq.deg
    return Config(**kwargs)



def read_bin_file(path, frame_index, sample_per_chirp, chirp_per_loop, loop_per_frame, rx_per_device, **kwargs):
    sample_per_frame = sample_per_chirp * chirp_per_loop * loop_per_frame * rx_per_device * 2 # 2 means real & imag.
    sample_type          = np.int16
    byte_per_sample      = sample_type().nbytes 
    with open(path, "rb") as f:
        f.seek((frame_index-1) * sample_per_frame * byte_per_sample)
        raw_data = f.read(sample_per_frame * byte_per_sample)
    adc_int     = np.frombuffer(raw_data, dtype=sample_type)
    adc_double  = np.double(adc_int)
    adc_complex = adc_double[::2] + 1j*adc_double[1::2]
    adc_cube = adc_complex.reshape((loop_per_frame, chirp_per_loop, sample_per_chirp, rx_per_device))
    adc_cube = NamedAxesArray(adc_cube, axis_names=("tx_steering", "slow_time", "fast_time", "rx_elements"))
    adc_cube = adc_cube.permute("tx_steering", "rx_elements", "slow_time", "fast_time")
    return adc_cube



def get_valid_num_frames(paths, index=0):
    master_idx = paths["idx"][index]["master"]
    with open(master_idx, "rb") as f:
        info = StructReader(Info).read(f)
    return info.numIdx, info.dataFileSize



if __name__ == '__main__':
    # Test
    path = r"C:\LocalWork\Cascade\20210626\20_29_53_06_26_21\20_29_53_06_26_21.mmwave.json"
    config = read_mmwave_json(path)
    print(config)

    path = r"C:\LocalWork\Cascade\20210626\20_29_53_06_26_21\slave1_0000_data.bin"
    cube = read_bin_file(path, 2, 256, 64, 31, 4)

    paths = get_paths(r"C:\LocalWork\Cascade\20210626\20_29_53_06_26_21")
    print(paths)
    num_idx, data_file_size = get_valid_num_frames(paths)
    print(num_idx, data_file_size)
    data_cube = read_adc_data(r"C:\LocalWork\Cascade\20210626\20_29_53_06_26_21", frame_index=2)
    print(data_cube)
    cube_rda = signal_processing(data_cube, config)
    print(cube_rda)

    show_ppi(cube_rda, config)