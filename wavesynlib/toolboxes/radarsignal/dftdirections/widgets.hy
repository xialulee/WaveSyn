(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [wavesynlib.widgets.tk.group [Group]])
(import [wavesynlib.widgets.tk.iconbutton [IconButton]])
(import [wavesynlib.widgets.tk.labeledentry [LabeledEntry]])

(import [wavesynlib.languagecenter.wavesynscript [Scripting]])


(widget Group parameter-grp [
    (pack :side "left" :fill "y")
    (setattr :name "Parameters")
    (child LabeledEntry num-elem-lent [
        (setattr
            :label-compound    "left"
            :label-common-icon "Pattern_M_Label.png"
            :label-text        "M"
            :label-width       3
            :entry-width       6
            :entry-text        16
            :checker-function  (. Scripting root-node gui value-checker check-int))
        (balloonmsg "The number of the array elements.") ])
    (child LabeledEntry dist-elem-lent [
        (setattr
            :label-compound    "left"
            :label-common-icon "Pattern_d_Label.png"
            :label-text        "d"
            :label-width      3
            :entry-width       6
            :entry-text        0.5
            :checker-function (. Scripting root-node gui value-checker check-positive-float))
        (balloonmsg "The space between elements (with respect to wavelength).") ])
    (child IconButton run-btn [
        (init
            :compound "left")
        (setattr
            :common-icon "run20x20.png") ]) ])
