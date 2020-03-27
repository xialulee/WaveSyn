(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [tkinter [*]])
(import [tkinter.ttk [Button]])
(import [wavesynlib.widgets.tk.group [Group]])



(widget Group source-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Source")
    (child Button parse-btn [
        (config :text "Parse")])])

