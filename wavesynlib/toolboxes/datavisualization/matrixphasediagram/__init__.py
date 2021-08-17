from itertools import product
from pathlib import Path

import numpy as np
from numpy import pi as π
from PIL import Image
import quantities as pq



def _get_path():
    return Path(__file__).parent



class MatrixPhaseDiagram:
    def __init__(self, matrix, delta_x, delta_y, elem_size, ppi=None):
        self.__A = matrix
        self.__Δx = delta_x
        self.__Δy = delta_y
        self.__d = elem_size
        self.__ppi = ppi

        def to_px(value):
            if not isinstance(value, pq.Quantity):
                return value
            else:
                if not ppi:
                    raise ValueError("PPI information missing.")
                return int((value * ppi).rescale(pq.dimensionless).magnitude)
        
        self.__Δx_px = to_px(delta_x)
        self.__Δy_px = to_px(delta_y)
        self.__d_px = to_px(elem_size)

        self.__face = Image.open(_get_path()/"face.png")
        self.__hand = Image.open(_get_path()/"hand.png")


    def get_canvas_size(self, unit=None):
        if not self.__ppi and unit:
            raise ValueError("PPI information missing.")
        Ny, Nx = self.__A.shape
        width = int(self.__d_px + (Nx - 1)*self.__Δx_px)
        height = int(self.__d_px + (Ny - 1)*self.__Δy_px)

        if unit:
            width = (width / self.__ppi).rescale(unit)
            height = (height / self.__ppi).rescale(unit)

        return width, height


    def draw(self):
        target = Image.new(mode="RGBA", size=self.get_canvas_size(), color=255)
        face = self.__face.resize(size=(self.__d_px,)*2)
        hand = self.__hand.resize(size=(self.__d_px,)*2)
        P = np.angle(self.__A) / π * 180
        Ny, Nx = self.__A.shape

        for r, c in product(range(Ny), range(Nx)):
            pos = (c*self.__Δx_px, r*self.__Δy_px)
            target.paste(face, pos)
            rothand = hand.rotate(P[r, c])
            # See https://stackoverflow.com/a/9459208
            target.paste(rothand, pos, mask=rothand.split()[3])
        
        return target



if __name__ == "__main__":
    import scipy.linalg 
    A = scipy.linalg.dft(8)
    mpd = MatrixPhaseDiagram(A, 2*pq.cm, 2*pq.cm, 2*pq.cm, 1200*pq.inch**-1)
    im = mpd.draw()
    im.save('test.png')