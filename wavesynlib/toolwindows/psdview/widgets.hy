(require [wavesynlib.languagecenter.hy.tkdef [widget]])



(import [tkinter [*]])
(import [tkinter.ttk [
    Label Scale Entry Button 
    Scrollbar Treeview Combobox]])
(import [wavesynlib.widgets.tk.group [Group]])



(widget Group load-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Load")
    (child Button load-btn [
        (init :text "Load")])])



(widget Group export-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Resize")
    (child Button export-all-btn [
        (init :text "All Layers")
        (pack :fill X)])
    (child Button export-selected-btn [
        (init :text "Selected Layer/Group")])])



(widget Group resize-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Resize")
    (child Scale image-scale [
        (init :from- 5 
                :to 100 
                :orient HORIZONTAL
                :value 100)])
    (child Label scale-label [
        (init :text "100%")])])



(widget Group external-viewer-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Viewer")
    (child Button launch-viewer-btn [
        (init :text "Launch")])])



(widget Group wallpaper-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Wallpaper")
    (child Button set-wallpaper-btn [
        (init :text "Set")])
    (child Combobox wallpaper-position-combo [
        (init :stat "readonly"
                :values ["Center" "Tile"
                         "Stretch" "Fit"
                         "Fill" "Span"])])])

