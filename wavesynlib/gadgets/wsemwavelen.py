import sys
import tkinter as tk

from wavesynlib.toolboxes.emwave.wavelengthpanel import WavelengthPanel



def main(argv):
    root = tk.Tk()
    root.title("λ")
    panel = WavelengthPanel(root)
    panel.pack(fill=tk.X, expand=tk.YES)
    root.mainloop()



if __name__ == "__main__":
    main(sys.argv)
