import colorsys



class WaveSynColor:
    def __init__(self, rgb=None, yiq=None, hls=None, hsv=None):
        if rgb:
            self.__rgb = rgb
            return
        if yiq:
            self.__rgb = colorsys.yiq_to_rgb(*yiq)
            return
        if hls:
            self.__rgb = colorsys.hls_to_rgb(*hls)
            return
        if hsv:
            self.__rgb = colorsys.hsv_to_rgb(*hsv)
            return

    def to_hexstr(self):
        return '#{:02x}{:02x}{:02x}'.format(
            *(int(x * 255) for x in self.__rgb)
        )

    def to_tk(self):
        return self.to_hexstr()

    def to_matplotlib(self):
        return self.__rgb

    def from_photoshop_hsv(self, hsv):
        H = hsv[0] / 360
        S = hsv[1] / 100
        V = hsv[2] / 100
        self.__rgb = colorsys.hsv_to_rgb(H, S, V)
        return self

    def to_photoshop_hsv(self):
        hsv = colorsys.rgb_to_hsv(self.__rgb)
        H = int(hsv[0] * 360)
        S = int(hsv[1] * 100)
        V = int(hsv[2] * 100)
        return H, S, V