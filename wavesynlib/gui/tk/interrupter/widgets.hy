(require [wavesynlib.languagecenter.hy.tkdef [widget]])

(import [tkinter [Frame Button]])
(import [tkinter.ttk [Label]])



(widget Frame main-panel [
    (child Label message-lbl [
        (init :text "If you start a time consuming loop in the wavesyn's console,
the GUI components will not response anymore.
If you want to abort this mission, you can click the button below.") ])
    (child Button abort-btn [
        (init 
            :text "Abort!"
            :bg   "red"
            :fg   "white") ])
    (child Label blank-lbl []) ])
