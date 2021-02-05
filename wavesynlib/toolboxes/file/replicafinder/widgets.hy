(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [tkinter [*]])
(import [tkinter.ttk [Label]])
(import [wavesynlib.widgets.tk.group [Group]])
(import [wavesynlib.widgets.tk.busylight [BusyLight]])
(import [wavesynlib.widgets.tk.wsbutton [WSButton]])

(import [PIL [ImageTk]])
(import [wavesynlib.languagecenter.hy.tools [get-hy-file-dir]])



(widget Group finder-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Finder")
    (child Frame grid-frm [
        (pack :side LEFT :fill BOTH)
        (child WSButton start-btn [
            (setattr :common-icon "run20x20.png")
            (grid :row 0 :column 0)])
        (child WSButton stop-btn [
            (setattr :common-icon "stop20x20.psd")
            (grid :row 0 :column 1)])])])



(widget Frame status-frm [
    (pack :fill X)
    (child BusyLight light-lbl [
        (pack :side RIGHT)])
    (child Label current-dir-lbl [
        (pack :side RIGHT)])])

