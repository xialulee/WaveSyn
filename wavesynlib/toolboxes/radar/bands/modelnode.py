from wavesynlib.languagecenter.wavesynscript import ModelNode, WaveSynScriptAPI
from . import ieee_radar_bands



class BandInfo(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @WaveSynScriptAPI
    def get_ieee_radar_bands(self):
        return ieee_radar_bands
