from collections import namedtuple



ADCDataProperty = namedtuple(
    "ADCDataProperty",
    [
        "sample_size",
        "num_sample_per_chirp",
        "num_chirp_per_loop",
        "num_loops",
        "num_rx_per_device",
        "num_devices"])

