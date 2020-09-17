(require [wavesynlib.languagecenter.hy.utils [super-init defprop]])

(import [tkinter [Frame Toplevel IntVar]])
(import [tkinter.ttk [Label Progressbar]])

(import -thread)

(import [wavesynlib.interfaces.timer.tk [TkTimer]])



(defclass LabeledProgress [Frame]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs)
        (.pack
            (setx self.--label (Label self)) 
            :expand "yes" :fill "y")
        (.pack 
            (Progressbar self 
                :orient   "horizontal"
                :variable (setx self.--progress (IntVar)) 
                :maximum  100
                :length   400)
            :expand "yes"
            :fill   "x") ) 
            
    (defprop progress
        #_getter
        (fn [self]
            (.get self.--progress) ) 
        #_setter
        (fn [self value]
            (.set self.--progress value)))
            
    (defprop label-text 
        #_getter
        (fn [self]
            (. self --label ["text"]))
        #_setter
        (fn [self value]
            (setv (. self --label ["text"]) value))))


(defclass ProgressDialog []
    (defn --init-- [self text-list &optional [title ""]]
        (setv self.--win (Toplevel))
        (doto self.--win
            (.protocol "WM_DELETE_WINDOW" self.-on-close)
            (.title    title))
        (setv self.--lock (-thread.allocate-lock))
        (setv number (len text-list))
        (setv 
            self.--progressbars  []
            progressbars         self.--progressbars
            self.--text-list     text-list
            self.--text-changed  False
            self.--progress-list (* [0] number)
            progress-list        self.--progress-list)
        (for [n (range number)]
            (.pack 
                (setx progressbar (LabeledProgress self.--win))
                :expand "yes"
                :fill   "x")
            (setv progressbar.label-text (get text-list n)) 
            (.append progressbars progressbar))
        (setv self.--timer (TkTimer 
            :widget   self.--win 
            :interval 50))
        (.add-observer self.--timer (fn []
            (with [self.--lock]
                (for [n (range number)]
                    (setv 
                        (. progressbars [n] progress) 
                        (get progress-list n))
                    (when self.--text-changed
                        (setv self.--text-changed False)
                        (for [n (range number)]
                            (setv 
                                (. progressbars [n] label-text)
                                (get text-list n))))))))
        (setv self.--timer.active True))
        
    (defn close [self]
        (.-on-close self))
        
    (defn set-progress [self index progress]
        (with [self.--lock]
            (setv 
                (. self --progress-list [index]) 
                progress)))
                
    (defn set-text [self index text]
        (with [self.--lock]
            (setv 
                (. self --text-list [index]) text
                (. self --text-changed)      True)))
                
    (defn -on-close [self]
        (setv self.--timer.active False)
        (.destroy self.--win)) )


(defmain [&rest args]
    (import [tkinter [Tk]])
    (setv root (Tk))
    (setv dialog (ProgressDialog 
        ["ProgressDialog Tester"
         "Test ProgressDialog"]))
    (doto dialog
        (.set-progress :index 0 :progress 50)
        (.set-progress :index 1 :progress 80))
    (.mainloop root))




;# -*- coding: utf-8 -*-
;"""
;Created on Wed Jan 27 16:47:12 2016

;@author: Feng-cong Li
;"""

;from tkinter import Frame, Toplevel, IntVar
;from tkinter.ttk import Label, Progressbar

;import six.moves._thread as thread

;from wavesynlib.interfaces.timer.tk import TkTimer


;class LabeledProgress(Frame):
    ;def __init__(self, *args, **kwargs):
        ;super().__init__(*args, **kwargs)
        ;self.__label = label = Label(self)
        ;label.pack(expand='yes', fill='x')
        ;self.__progress = progress = IntVar()
        ;Progressbar(self, orient='horizontal', 
                          ;variable=progress, maximum=100,
                          ;length=400).pack(expand='yes', fill='x')
        
    ;@property
    ;def progress(self):
        ;return self.__progress.get()
        
    ;@progress.setter
    ;def progress(self, value):
        ;self.__progress.set(value)
        
    ;@property
    ;def label_text(self):
        ;return self.__label['text']
        
    ;@label_text.setter
    ;def label_text(self, value):
        ;self.__label['text'] = value


;class ProgressDialog:
    ;def __init__(self, text_list, title=''):
        ;self.__win = win = Toplevel()
        ;win.protocol("WM_DELETE_WINDOW", self._on_close)
        ;win.title(title)
        ;self.__lock = thread.allocate_lock() 
                
        ;number = len(text_list)        
        ;self.__progressbars = progressbars = []
        ;self.__text_list = text_list
        ;self.__text_changed = False
        ;self.__progress_list = progress_list = [0]*number                
        ;for n in range(number):
            ;progressbar = LabeledProgress(win)
            ;progressbar.pack(expand='yes', fill='x')
            ;progressbar.label_text = text_list[n]
            ;progressbars.append(progressbar)
        
        ;self.__timer = timer = TkTimer(widget=win, interval=50)
        
        ;@timer.add_observer
        ;def on_timer():
            ;with self.__lock:
                ;for n in range(number):
                    ;progressbars[n].progress = progress_list[n]
                ;if self.__text_changed:
                    ;self.__text_changed = False
                    ;for n in range(number):
                        ;progressbars[n].label_text = self.__text_list[n]
            
        ;timer.active = True        
        
    ;def close(self):
        ;self._on_close()
        
    ;def set_progress(self, index, progress):
        ;with self.__lock:
            ;self.__progress_list[index] = progress
            
    ;def set_text(self, index, text):
        ;with self.__lock:
            ;self.__text_list[index] = text
            ;self.__text_changed = True
            
    ;def _on_close(self):
        ;self.__timer.active = False
        ;self.__win.destroy()
            
            
;def main(argv):
    ;from tkinter import Tk
    ;root = Tk()
    ;dialog = ProgressDialog(['abcd', 'efgh'])
    ;dialog.set_progress(index=0, progress=50)
    ;dialog.set_progress(index=1, progress=80)
    ;root.mainloop()
    

;if __name__ == '__main__':
    ;main(None)
            
