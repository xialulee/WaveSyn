from math import pi
import numpy as np
import vispy.scene
from vispy.scene import visuals



def make_grid(view, x_span, x_major_tick, y_span, y_major_tick):
    x_count = int(np.ceil(x_span/x_major_tick))
    y_count = int(np.ceil(y_span/y_major_tick))
    x_range = x_count*x_major_tick
    y_range = y_count*y_major_tick

    for k in range(y_count+1):
        y = k*y_major_tick
        line = visuals.Line(
            pos=np.array([[-x_range, y], [x_range, y]]),
            color=(0.0, 1.0, 1.0, 1.0))
        view.add(line)

    for k in range(-x_count, x_count+1):
        x = k*x_major_tick
        line = visuals.Line(
            pos=np.array([[x, 0], [x, y_range]]),
            color=(0.0, 1.0, 1.0, 1.0))
        view.add(line)






if __name__ == "__main__":
    import sys

    canvas = vispy.scene.SceneCanvas(keys="interactive", show=True)
    view = canvas.central_widget.add_view()

    make_grid(view, x_span=50, x_major_tick=10, y_span=100, y_major_tick=10)

    view.camera = "turntable"

    visuals.XYZAxis(parent=view.scene)

    if sys.flags.interactive != 1:
        vispy.app.run()
