import numpy as np



def leak_func(N, index, int_indices):
    return (1 - np.exp(1j*2*np.pi*index)) / (1 - np.exp(1j/N*2*np.pi*(index - int_indices)))



class NUFFT:
    def __init__(self, N, indices, extent):
        self.__N = N
        self.__N_indices = N_indices = len(indices)
        self.__int_indices = np.empty(shape=(N, extent*2), dtype=int)
        self.__leak_lut = np.empty(shape=(N, extent*2))
        for i, index in enumerate(indices):
            int_index = int(index)
            int_indices = np.mod(np.arange(int_index-(extent-1), int_index+extent+1, dtype=int), N)
            self.__int_indices[i, :] = int_indices
            self.__leak_lut[i, :] = leak_func(N, index, int_indices)


    def spread(self, samples):
        result = np.zeros(shape=(self.__N), dtype=samples.dtype)
        for i in range(self.__N_indices):
            result[self.__int_indices[i]] += self.__leak_lut[i] * samples[i]
        return result


    def calc(self, samples):
        data = self.spread(samples)
        return np.fft.fft(data)


