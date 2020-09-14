(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [tkinter [*]])
(import [tkinter.ttk [
    Button Label]])
(import [wavesynlib.widgets.tk.group [Group]])

(import [PIL [ImageTk]])
(import [wavesynlib.languagecenter.hy.tools [get-hy-file-dir]])

(setv -file-dir (get-hy-file-dir --file--))
(setv -start-icon (ImageTk.PhotoImage 
    :file (/ -file-dir "images" "start_button.png")))
(setv -stop-icon (ImageTk.PhotoImage 
    :file (/ -file-dir "images" "stop_button.png")))
(setv -green-light-icon (ImageTk.PhotoImage
    :file (/ -file-dir "images" "green_light.png")))
(setv -red-light-icon (ImageTk.PhotoImage
    :file (/ -file-dir "images" "red_light.png")))



(widget Group finder-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Finder")
    (child Frame grid-frm [
        (pack :side LEFT :fill BOTH)
        (child Button start-btn [
            (init :image -start-icon)
            (grid :row 0 :column 0)])
        (child Button stop-btn [
            (init :image -stop-icon)
            (grid :row 0 :column 1)])])])



(widget Frame status-frm [
    (pack :fill X)
    (child Label light-lbl [
        (pack :side RIGHT)])
    (child Label current-dir-lbl [
        (pack :side RIGHT)])])

