(require [wavesynlib.languagecenter.hy.tkdef [widget]])
(import [tkinter [*]])
(import [tkinter.ttk [
    Button]])
(import [wavesynlib.widgets.tk [Group]])



(widget Group connect-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Connect")
    (child Button get-active-btn [
        (config :text "Get Active")])
    (child Button create-btn [
        (config :text "Create")])])



(widget Group window-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Window")
    (child Button foreground-btn [
        (config :text "Foreround")])
    (child Button copypath-btn [
        (config :text "Copy Path")])])



(widget Group utils-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Utils")])

