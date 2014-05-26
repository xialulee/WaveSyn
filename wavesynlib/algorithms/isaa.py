from numpy import *
from mathtools import Operator, Algorithm

@Operator
def Proj_M1(s): # This function is corresponding to eq.22.
    return exp(1j * angle(s)) # see eq.22


class CProj_A_DIAC(Operator):
    def __init__(self, Qr=None):
        self.Qr   = Qr
        def func(s):
            N   = len(s)
            a   = fft.ifftshift(convolve(s, conj(s[::-1])))
            a[self.__Qr]  = 0; a[-self.__Qr] = 0 # see eq.33
            Fa     = fft.fft(a)
            Fa.imag  = 0
            s   = fft.ifft(sqrt(Fa) * \
                    exp(1j * angle(fft.fft(s, 2*N-1))))[:N] # see eq.23
            return s
        Operator.__init__(self, func)

    @property
    def Qr(self):
        return self.__Qr

    @Qr.setter
    def Qr(self, value):
        if isinstance(value, ndarray):
            self.__Qr   = value
        else:
            self.__Qr   = array(value)


class DIAC(Algorithm):
    __algorithmName__    = 'ISAA-DIAC'
    def __init__(self):
        self.exitcond   = {}
        Algorithm.__init__(self)

    def initpoint(self, N):
        return exp(1j * 2 * pi * random.rand(N))
        
    __parameters__  = (
        ['N', 'int', 'Sequence Length.'],
        ['Qr', 'expression', 'The interval in which correlation sidelobes are suppressed.'],
        ['K', 'int', 'Maximum iteration number.']
    )
    def __call__(self, N, Qr, K):
        s_init  = self.initpoint(N)
        if not isinstance(Qr, ndarray):
            Qr      = array(Qr)        
        Proj_A_DIAC = CProj_A_DIAC(Qr)
        Tisaa   = (Proj_M1*Proj_A_DIAC) # see eq.26
        Tisaa.exitcond  = self.exitcond
        return (Tisaa**K)(s_init)

diac    = DIAC()



def plot_acdb(fig, s, *args, **kwargs):
    if not isinstance(s, ndarray):
        s   = array(s)
    N       = len(s)
    ac      = convolve(s, conj(s[::-1]))
    acdb    = 20*log10(abs(ac))
    acdb    = acdb - max(acdb)
    fig.plot(r_[(-N+1):N], acdb, *args, **kwargs)


'''
function wf = isaa(init, Qr)
N = numel(init);
wf = init;
for k = 1 : 1e4
    acwf = ifftshift(conv(wf, conj(wf(end:-1:1))));
    acwf(Qr+1) = 0;
    acwf(end-Qr+1) = 0;
    Pwf = real(fft(acwf));
    new_wf = ifft(sqrt(Pwf) .* exp(1j * angle(fft(wf, 2*N-1))));
    old_wf = wf;
    wf = exp(1j * angle(new_wf(1:N)));
    if norm(old_wf - wf) < 1e-14, k, break; end
end
end
'''
