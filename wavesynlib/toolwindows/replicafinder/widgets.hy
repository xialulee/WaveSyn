(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [tkinter [*]])
(import [tkinter.ttk [
    Button]])
(import [wavesynlib.widgets.tk [Group]])

(import [PIL [ImageTk]])
(import [wavesynlib.languagecenter.hy.tools [get-hy-file-dir]])

(setv -file-dir (get-hy-file-dir --file--))
(setv -start-icon (ImageTk.PhotoImage 
    :file (/ -file-dir "images" "start_button.png")))
(setv -stop-icon (ImageTk.PhotoImage 
    :file (/ -file-dir "images" "stop_button.png")))



(widget Group finder-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Finder")
    (child Frame grid-frm [
        (pack :side LEFT :fill BOTH)
        (child Button start-btn [
            (config :image -start-icon)
            (grid :row 0 :column 0)])
        (child Button stop-btn [
            (config :image -stop-icon)
            (grid :row 0 :column 1)])])])

