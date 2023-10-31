from itertools import product
from pathlib import Path
from typing import Tuple, Union, Optional, Self

import numpy as np
from numpy import pi as π
from PIL import Image
import quantities as pq



def _get_path():
    return Path(__file__).parent



class MatrixPhaseDiagram:
    def __init__(
            self, 
            matrix: np.ndarray, 
            delta_x: Union[float, pq.Quantity], 
            delta_y: Union[float, pq.Quantity], 
            elem_size: Union[float, pq.Quantity], 
            ppi: Optional[Union[float, pq.Quantity]] = None):
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


    def draw(self: Self) -> Image.Image:
        # Create a new image with an RGBA color mode
        canvas: Image.Image = Image.new(mode="RGBA", size=self.get_canvas_size(), color=255)
        # Resize the clock face image to the specified dimensions
        resized_face: Image.Image = self.__face.resize(size=(self.__d_px,)*2)
        # Resize the clock hand image to the specified dimensions
        resized_hand: Image.Image = self.__hand.resize(size=(self.__d_px,)*2)
        # Calculate the hand angle in degrees from the complex amplitude
        hand_angle_deg: np.ndarray = np.angle(self.__A) / π * 180
        # Get the dimensions of the amplitude matrix
        num_rows: int
        num_cols: int
        num_rows, num_cols = self.__A.shape

        # Iterate through each cell in the amplitude matrix
        for row, col in product(range(num_rows), range(num_cols)):
            # Calculate the position to place the clock face and hand
            position: Tuple[int, int] = (col * self.__Δx_px, row * self.__Δy_px)
            # Paste the clock face onto the canvas
            canvas.paste(resized_face, position)
            # Rotate the hand image based on the angle at the current cell
            rotated_hand: Image.Image = resized_hand.rotate(hand_angle_deg[row, col])
            # Paste the rotated hand onto the canvas with a mask to maintain transparency
            # Reference: https://stackoverflow.com/a/9459208
            canvas.paste(rotated_hand, position, mask=rotated_hand.split()[3])
        
        # Return the final canvas image
        return canvas



if __name__ == "__main__":
    import scipy.linalg 
    A = scipy.linalg.dft(8)
    mpd = MatrixPhaseDiagram(A, 2*pq.cm, 2*pq.cm, 2*pq.cm, 1200*pq.inch**-1)
    im = mpd.draw()
    im.save('test.png')