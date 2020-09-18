(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [tkinter [Frame]])
(import [tkinter.ttk [Button Combobox Radiobutton]])

(import [wavesynlib.widgets.tk.group [Group]])
(import [wavesynlib.widgets.tk.iconbutton [IconButton]])
(import [wavesynlib.widgets.tk.labeledentry [LabeledEntry]])

(import [wavesynlib.languagecenter.wavesynscript [Scripting]])


(widget Frame to-dvplane-frm [
    (pack :fill "both")
    (child Button new-btn [
        (init :text "New")
        (pack :fill "x") ])
    (child Frame exist-frm [
        (pack :fill "x")
        (child Combobox id-cmb [ 
            (pack :side "left" :fill "x") ])
        (child Button ok-btn [
            (init :text "Ok") ]) ]) ])


(widget Frame ask-export-to-console-frm [
    (pack :fill "both")
    (child Radiobutton rad-btn [
        (init :text "rad")
        (pack :anchor "nw") ])
    (child Radiobutton deg-btn [
        (init :text "deg")
        (pack :anchor "nw") ])
    (child LabeledEntry varname-lent [
        (setattr :label-text "var name:" )
        (pack :anchor "nw")
        (balloonmsg "Input variable name here. ") ]) 
    (child Button ok-btn [
        (init :text "Ok") ]) ])


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
            :label-width       3
            :entry-width       6
            :entry-text        0.5
            :checker-function (. Scripting root-node gui value-checker check-positive-float))
        (balloonmsg "The space between elements (with respect to wavelength).") ])
    (child IconButton run-btn [
        (init
            :compound "left")
        (setattr
            :common-icon "run20x20.png") ]) ])


(widget Group export-data-grp [
    (pack :side "left" :fill "y")
    (setattr :name "Data")
    (child Frame export-button-frame [
        (child IconButton export-to-console-btn [
            (setattr :common-icon "console20x20.psd")
            (grid :row 0 :column 0) 
            (balloonmsg "Export data to the console.") ]) 
        (child IconButton export-to-dvplane-btn [
            (setattr :common-icon "figurewindow20x20.psd")
            (grid :row 0 :column 1)
            (balloonmsg "Export data to a data visualization plane window.") ]) ]) ])
