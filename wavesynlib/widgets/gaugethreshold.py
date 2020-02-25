from tkinter import Frame, Label
from tkinter.ttk import Scale



class GaugeThreshold(Frame):
    def __init__(self, *args, **kwargs):
        default_range = kwargs.pop("default_range", (60, 90))
        
        super().__init__(*args, **kwargs)

        color_list = ["green", "yellow"]
        label_list = []
        scale_list = []

        range_list = [*default_range]

        def on_scale0(value):
            value = int(float(value))
            if value > range_list[1]:
                scale_list[1].set(value)
                label_list[1]["text"] = f"{value: 3d}%"
            range_list[0] = value
            label_list[0]["text"] = f"{value: 3d}%"

        def on_scale1(value):
            value = int(float(value))
            if value < range_list[0]:
                scale_list[0].set(value)
                label_list[0]["text"] = f"{value: 3d}%"
            range_list[1] = value
            label_list[1]["text"] = f"{value: 3d}%"

        callback_list = [on_scale0, on_scale1]

        for index in range(2):
            frame = Frame(self)
            frame.pack(expand="yes", fill="x")
            label = Label(frame, 
                bg=color_list[index], 
                text=f"{default_range[index]: 3d}%",
                width=5)
            label.pack(side="left")
            label_list.append(label)
            scale = Scale(frame,
                from_=0, to=100, value=default_range[index],
                orient="horizontal", 
                command=callback_list[index])
            scale.pack(side="left", fill="x", expand="yes")
            scale_list.append(scale)

        self.__scale_list = scale_list


    @property
    def threshold_list(self):
        return [int(float(scale.get())) for scale in self.__scale_list]



if __name__ == "__main__":
    range_scale = GaugeThreshold()
    range_scale.pack(expand="yes", fill="x")
    range_scale.mainloop()
