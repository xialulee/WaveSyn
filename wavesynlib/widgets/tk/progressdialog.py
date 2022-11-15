from tkinter import Frame, Toplevel, IntVar
from tkinter.ttk import Label, Progressbar
import _thread

from toolz import second
from quantities import second

from wavesynlib.interfaces.timer.tk import TkTimer


class LabeledProgress(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        (label := Label(self)).pack(expand="yes", fill="x")
        self.__label = label
        Progressbar(self, 
            orient="horizontal", 
            variable=(progress := IntVar()), 
            maximum=100, 
            length=400).pack(expand="yes", fill="x")
        self.__progress = progress
    
    @property
    def progress(self):
        return self.__progress.get()
    
    @progress.setter
    def progress(self, value):
        self.__progress.set(value)

    @property
    def label_text(self):
        return self.__label["text"]
    
    @label_text.setter
    def label_text(self, value):
        self.__label["text"] = value



class ProgressDialog:
    def __init__(self, text_list, title=""):
        self.__win = win = Toplevel()
        win.protocol("WM_DELETE_WINDOW", self._on_close)
        win.title(title)
        self.__lock = _thread.allocate_lock()
        number = len(text_list)
        self.__progressbars = []
        progressbars = self.__progressbars
        self.__text_list = text_list
        self.__text_changed = False
        self.__progress_list = [0] * number
        progress_list = self.__progress_list
        for n in range(number):
            (progressbar := LabeledProgress(self.__win)).pack(expand="yes", fill="x")
            progressbar.label_text = text_list[n]
            progressbars.append(progressbar)
        self.__timer = TkTimer(widget=self.__win, interval=0.05 * second)

        def on_timer(event=None):
            with self.__lock:
                for n in range(number):
                    progressbars[n].progress = progress_list[n]
                    if self.__text_changed:
                        self.__text_changed = False
                        for n in range(number):
                            progressbars[n].label_text = text_list[n]
        self.__timer.add_observer(on_timer)
        self.__timer.active = True

    def close(self):
        return self._on_close()

    def set_progress(self, index, progress):
        with self.__lock:
            self.__progress_list[index] = progress

    def set_text(self, index, text):
        with self.__lock:
            self.__text_list[index] = text
            self.__text_changed = True

    def _on_close(self):
        self.__timer.active = False
        return self.__win.destroy()


if __name__ == "__main__":
    from tkinter import Tk
    root = Tk()
    dialog = ProgressDialog([
        "ProgressDialog Tester", 
        "Test ProgressDialog"])
    dialog.set_progress(index=0, progress=50)
    dialog.set_progress(index=1, progress=80)
    root.mainloop()
