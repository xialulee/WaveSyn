import os

from quantities import second
from .dirindicator import DirIndicator
from wavesynlib.interfaces.timer.tk import TkTimer


class CWDIndicator(DirIndicator):
    def __init__(self, *args, **kwargs):
        self.__chdir_func = kwargs.pop('chdir_func', None)
        super().__init__(*args, **kwargs)
        self.__timer = TkTimer(self, interval = 0.5 * second)

        @self.__timer.add_observer
        def on_timer(event):
            cwd = os.getcwd()
            if not isinstance(cwd, str):
                cwd = cwd.decode(self._coding, 'ignore')
            if os.path.altsep is not None:
                # Windows OS
                cwd = cwd.replace(os.path.altsep, os.path.sep)
            if self._directory != cwd:
                self.change_dir(cwd, passive=True) 
        self.__timer.active = True


    def change_dir(self, dirname, passive=False):
        if self.__chdir_func:
            self.__chdir_func(dirname, passive)
        else:
            os.chdir(dirname)
        super().change_dir(dirname)
