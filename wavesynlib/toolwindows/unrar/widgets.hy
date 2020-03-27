(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [tkinter [*]])
(import [tkinter.ttk [Button]])
(import [wavesynlib.widgets.group [Group]])



(widget Group load-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Load")
    (child Button load-btn [
        (config :text "Load")])])



(widget Group unpack-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Unpack")
    (child Button unpack-btn [
        (config :text "Unpack")])])

