(require [wavesynlib.languagecenter.hy.tkdef [init-hywidget]])
(init-hywidget)

(import [tkinter [*]])
(import [tkinter.ttk [Button Progressbar]])
(import [pathlib [Path]])

(import [wavesynlib.widgets.tk.wsbutton [WSButton]])
(import [wavesynlib.widgets.tk.labeledentry [LabeledEntry]])
(import [wavesynlib.widgets.tk.scrolledlist [ScrolledList]])
(import [wavesynlib.widgets.tk.group [Group]])

(setv -res-dir (/ (. (Path --file--) parent) "resources"))



(widget Group clipb-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Clipboard")
    (child Frame clipb-grid-frm [
        (child WSButton read-clipb-btn [
            (grid :row 0 :column 0)
            (init 
                :image (/ -res-dir "readclipb.png")
                :command-object (bind "read_clipb"))
            (balloonmsg "Read the clipboard of an Android device.") ])
        (child WSButton write-clipb-btn [
            (grid :row 0 :column 1)
            (init 
                :image (/ -res-dir "writeclipb.png")
                :command-object (bind "write_clipb"))
            (balloonmsg "Write the clipboard of an Android device.") ])
        (child WSButton send-clipb-image-btn [
            (grid :row 0 :column 2)
            (init :image (/ -res-dir "sendclipbimage.png"))
            (balloonmsg "Send image in clipboard to the Android device.") ]) ]) ])


(widget Group storage-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Storage")
    (child Frame storage-grid-frm [
        (child WSButton get-image-btn [
            (grid :row 0 :column 0)
            (balloonmsg "Get gallery photos.")
            (init :image (/ -res-dir "getimage.png")) ])
        (child WSButton get-file-btn [
            (grid :row 0 :column 1)
            (balloonmsg "Get File")
            (init :image (/ -res-dir "getfile.png")) ])
        (child WSButton send-image-btn [
            (grid :row 1 :column 0)
            (balloonmsg "Send a picture to the device.")
            (init :image (/ -res-dir "sendclipbimage.png")) ])
        (child WSButton send-file-btn [
            (grid :row 1 :column 1)
            (balloonmsg "Send a file to the device.")
            (init :image (/ -res-dir "sendfile.png")) ])
        (child Progressbar transfer-progressbar [
            (grid :row 2 :columnspan 2)
            (balloonmsg "Data transfer progress")
            (init :length 60 :maximum 100 :variable (bind "transfer_progress")) ]) ]) ])


(widget Group sensors-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Sensors")
    (child Frame sensors-grid-frm [
        (child WSButton read-gps-btn [
            (balloonmsg "Read the AGPS sensor of the Android device.")
            (init 
                :text "Location" 
                :image (/ -res-dir "locationsensor.png")
                :compound LEFT) ]) ]) ])


(widget Group manage-grp [
    (pack :side LEFT :fill Y)
    (setattr :name "Manager")
    (child Frame manage-left-frm [
        (pack :side LEFT :fill Y)
        (child LabeledEntry qr-size-lent [
            (balloonmsg "Size (pixels) of the generated QR code.")
            (setattr 
                :label-text  "QR Size"
                :label-width 7
                :entry-width 4
                :entry-text  200) ])
        (child Button qr-size-ok-btn [
            (init :text "Ok") ])
        (child Button misson-abort-btn [
            (init :text "Abort") ]) ])
    (child Frame manage-right-frm [
        (pack :side LEFT :fill Y)
        (child ScrolledList ip-list [
            (pack :fill Y) ]) ]) ])
