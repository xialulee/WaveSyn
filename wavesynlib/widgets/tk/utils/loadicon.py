from toolz import first, last
from PIL import ImageTk
from wavesynlib.fileutils.photoshop.psd import get_pil_image


def load_icon(path, common=False):
    if common:
        from wavesynlib.languagecenter.wavesynscript import Scripting
        path = Scripting.root_node.get_gui_image_path(path)
    if last(path.split('.')) == 'psd':
        with open(path, 'rb') as psd_file:
            pil_image = first(get_pil_image(psd_file))
            result = ImageTk.PhotoImage(image=pil_image)
    else:
        result = ImageTk.PhotoImage(file=path)
    return result
