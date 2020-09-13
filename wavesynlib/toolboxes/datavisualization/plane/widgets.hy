(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [tkinter [*]])
(import [tkinter.ttk [Button Combobox]])
(import [wavesynlib.widgets.tk.group [Group]])
(import [wavesynlib.widgets.tk.iconbutton [IconButton]])
(import [wavesynlib.widgets.tk.labeledentry [LabeledEntry]])



(widget Group load-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Load")
    (child Frame grid-frm [
        (pack :side LEFT :fill BOTH)
        (child IconButton loadvar-btn [
            (setattr :common-icon "python20x20.psd")
            (balloonmsg "Load variable.")
            (config 
                :text     "VAR"
                :compound LEFT
                :width    5) 
            (grid :row 0 :column 0)])
        (child IconButton loadpkl-btn [
            (setattr :common-icon "python20x20.psd")
            (balloonmsg "Load a pickle file.")
            (config
                :text     "PKL"
                :compound LEFT
                :width    5) 
            (grid :row 1 :column 0)])
        (child IconButton runexpr-btn [
            (setattr :common-icon "python20x20.psd")
            (balloonmsg "Run a python expression.")
            (config
                :text     "EXP"
                :compound LEFT
                :width    5)
            (grid :row 2 :column 0) ])]) ])


(widget Frame drawmode-panel [
    (child Label prompt [
        (config :text "Select draw mode:") ])
    (child Combobox drawmode-comb [
        (config
            :value      ["plot" "stem" "scatter"]
            :takefocus  1
            :stat       "readonly") ])
    (child Button ok-btn [
        (config :text "OK") ]) ])


(widget Frame scatter-panel [
    (child IconButton color-btn [
        (setattr :common-icon "color20x20.psd")
        (balloonmsg "Choose marker color.")
        (config
            :text     "color"
            :compound LEFT) ])
    (child LabeledEntry marker-lent [
        (setattr :label-text "marker") ])

    (child Button ok-btn [
        (config :text "OK") ]) ])
