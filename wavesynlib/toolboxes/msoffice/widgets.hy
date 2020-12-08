(require [wavesynlib.languagecenter.hy.tkdef [widget]])
(import [tkinter [*]])
(import [tkinter.ttk [
    Button]])
(import [wavesynlib.widgets.tk.group [Group]])



(widget Group connect-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Connect")
    (child Button get-active-btn [
        (init :text "Get Active")])
    (child Button create-btn [
        (init :text "Create")])])



(widget Group window-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Window")
    (child Button foreground-btn [
        (init :text "Foreround")])
    (child Button copypath-btn [
        (init :text "Copy Path")])])



(widget Group utils-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Utils")])

