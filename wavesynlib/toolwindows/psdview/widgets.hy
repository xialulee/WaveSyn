(require [wavesynlib.languagecenter.hy.tkdef [widget]])



(import [tkinter [*]])
(import [tkinter.ttk [
    Label Scale Entry Button 
    Scrollbar Treeview Combobox]])
(import [wavesynlib.widgets.group [Group]])



(widget Group load-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Load")
    (child Button load-btn [
        (config :text "Load")])])



(widget Group export-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Resize")
    (child Button export-all-btn [
        (config :text "All Layers")
        (pack :fill X)])
    (child Button export-selected-btn [
        (config :text "Selected Layer/Group")])])



(widget Group resize-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Resize")
    (child Scale image-scale [
        (config :from- 5 
                :to 100 
                :orient HORIZONTAL
                :value 100)])
    (child Label scale-label [
        (config :text "100%")])])



(widget Group external-viewer-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Viewer")
    (child Button launch-viewer-btn [
        (config :text "Launch")])])



(widget Group wallpaper-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Wallpaper")
    (child Button set-wallpaper-btn [
        (config :text "Set")])
    (child Combobox wallpaper-position-combo [
        (config :stat "readonly"
                :values ["Center" "Tile"
                         "Stretch" "Fit"
                         "Fill" "Span"])])])

