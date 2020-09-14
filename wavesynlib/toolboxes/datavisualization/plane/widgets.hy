(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [tkinter [*]])
(import [tkinter.ttk [Button Combobox]])
(import [wavesynlib.widgets.tk.group [Group]])
(import [wavesynlib.widgets.tk.iconbutton [IconButton]])
(import [wavesynlib.widgets.tk.labeledentry [LabeledEntry]])
(import [wavesynlib.widgets.tk.labeledscale [LabeledScale]])

(import [wavesynlib.languagecenter.wavesynscript [Scripting]])



(widget Group load-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Load")
    (child Frame grid-frm [
        (pack :side LEFT :fill BOTH)
        (child IconButton loadvar-btn [
            (init 
                :text     "VAR"
                :compound LEFT
                :width    5) 
            (setattr :common-icon "python20x20.psd")
            (balloonmsg "Load a variable from console.")
            (grid :row 0 :column 0)])
        (child IconButton loadpkl-btn [
            (init
                :text     "PKL"
                :compound LEFT
                :width    5) 
            (setattr :common-icon "python20x20.psd")
            (balloonmsg "Load a pickle file.")
            (grid :row 1 :column 0)])
        (child IconButton runexpr-btn [
            (init
                :text     "EXP"
                :compound LEFT
                :width    5)
            (setattr :common-icon "python20x20.psd")
            (balloonmsg "Run a python expression.")
            (grid :row 2 :column 0) ])]) ])


(widget Frame common-prop-panel [
    (child IconButton color-btn [
        (init 
            :text     "color"
            :compound LEFT)
        (setattr :common-icon "color20x20.psd") 
        (balloonmsg "Choose color.")
        (pack :fill X) ])
    (child LabeledEntry marker-lent [
        (setattr :label-text "marker") ])
    (child LabeledScale alpha-scale [
        (init 
            :from- 0.0
            :to    1.0) 
        (setattr
            :value-formatter (fn [val] f"{(float val) :.2f}")
            :name            "alpha" 
            :scale-value     1.0)
        (pack :fill X) ]) ])


(widget Frame plot-prop-panel [
    (child LabeledEntry linestyle-lent [
        (setattr :label-text "linestyle") ])
    (child LabeledEntry linewidth-lent [
        (setattr 
            :label-text       "linewidth"
            :checker-function (. Scripting root-node gui value-checker check-nonnegative-float)) ])
    (child Button ok-btn [
        (init :text "OK") ]) ])


(widget Frame scatter-prop-panel [
    (child Button ok-btn [
        (init :text "OK") ]) ])


(widget Frame stem-prop-panel [
    (child Button ok-btn [
        (init :text "OK") ]) ])
