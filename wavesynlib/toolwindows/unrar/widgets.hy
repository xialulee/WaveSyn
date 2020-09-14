(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [tkinter [*]])
(import [tkinter.ttk [Button]])
(import [wavesynlib.widgets.tk.group [Group]])



(widget Group load-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Load")
    (child Button load-btn [
        (init :text "Load")])])



(widget Group unpack-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Unpack")
    (child Button unpack-btn [
        (init :text "Unpack")])])

