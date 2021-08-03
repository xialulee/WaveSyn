from wavesynlib.languagecenter.datatypes.physicalquantities.containers import QuantityFrame, Query
from wavesynlib.toolboxes.emwave.algorithms import λfT_eq

from pathlib import Path
import quantities as pq
import numpy as np



def _read_csv():
    csv_path = Path(__file__).parent / "radarfrequencybands.csv"
    frm = QuantityFrame.read_csv(csv_path)
    min_freq = frm.qcol("min_freq")
    max_freq = frm.qcol("max_freq")
    
    result = λfT_eq(f=min_freq)
    max_λ = result.qcol("λ").rescale(pq.m)
    max_T = result.qcol("T").rescale(pq.ns)
    
    result = λfT_eq(f=max_freq)
    min_λ = result.qcol("λ").rescale(pq.m)
    min_T = result.qcol("T").rescale(pq.ns)

    frm["min_λ/m"] = min_λ.magnitude
    frm["max_λ/m"] = max_λ.magnitude
    frm["min_T/ns"] = min_T
    frm["max_T/ns"] = max_T

    return frm



ieee_radar_bands = _read_csv()



def freq_to_name(f):
    if not isinstance(f, pq.Quantity):
        f = f*pq.Hz
    result = Query()\
        .SELECT("band_name")\
        .FROM(ieee_radar_bands)\
        .WHERE(lambda r: r.qelem("min_freq") <= f < r.qelem("max_freq"))\
        .FIRST()
    return result[1]["band_name"]
