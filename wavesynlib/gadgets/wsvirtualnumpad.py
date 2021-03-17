import tkinter as tk
from tkinter import ttk



class HotKeyFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        entry_key = ttk.Entry(self)
        entry_key["width"] = 3
        entry_key.pack(side=tk.LEFT)

        self.__ctrl = tk.BooleanVar()
        self.__alt = tk.BooleanVar()
        self.__shift = tk.BooleanVar()
        
        check_ctrl = ttk.Checkbutton(self, text="Ctrl", variable=self.__ctrl)
        check_ctrl.pack(side=tk.LEFT)
        check_alt = ttk.Checkbutton(self, text="Alt", variable=self.__alt)
        check_alt.pack(side=tk.LEFT)
        check_shift = ttk.Checkbutton(self, text="Shift", variable=self.__shift)
        check_shift.pack(side=tk.LEFT)


    @property
    def ctrl(self):
        return self.__ctrl.get()

    @property
    def alt(self):
        return self.__alt.get()


    @property
    def shift(self):
        return self.shift.get()
    



class KeyMapLabel(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["borderwidth"] = 2
        self["relief"] = tk.GROOVE
        label_width = 1
        self.__label_old = tk.Label(self)
        self.__label_old["fg"] = "red"
        self.__label_old["width"] = label_width
        self.__label_old["font"] = ("Arial", 60)
        self.__label_old.pack(side=tk.LEFT)
        self.__label_new = tk.Label(self)
        self.__label_new["fg"] = "forestgreen"
        self.__label_new["width"] = label_width
        self.__label_new.pack(side=tk.LEFT, anchor=tk.SE)


    def show_key_map(self, old, new):
        self.__label_old["text"] = old
        self.__label_new["text"] = new



class NumpadFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        old = [["7", "8", "9"], ["U", "I", "O"], ["J", "K", "L"], ["M", ",", "."]]
        new = [["7", "8", "9"], ["4", "5", "6"], ["1", "2", "3"], ["0", ",", "."]]

        for r in range(4):
            for c in range(3):
                label = KeyMapLabel(self)
                label.show_key_map(old=old[r][c], new=new[r][c])
                label.grid(row=r, column=c)



if __name__ == "__main__":
    root = tk.Tk()
    tk.Label(root, text="Numlock Hotkey:").pack(anchor=tk.W)
    htk = HotKeyFrame(root)
    htk.pack(anchor=tk.W)
    frm = NumpadFrame(root)
    frm.pack()
    root.mainloop()
