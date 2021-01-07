(import [tkinter [Tk]])
(import [queue [Empty]])
(import [quantities [second]])

(import [wavesynlib.interfaces.timer.tk [TkTimer]])
(import [wavesynlib.widgets.tk.desctotk [hywidgets-to-tk]])

(import [.widgets [main-panel]])



(defn main [messages-from-interrupter messages-to-interrupter]
    (setv root (Tk))
    (doto root
        (.title         "WaveSyn-Interrupter")
        (.protocol      "WM_DELETE_WINDOW" (fn [] None))
        (.wm-attributes "-topmost" True) )
    (setv widgets-desc [main-panel])
    (setv widgets (hywidgets-to-tk root widgets-desc))
    (setv (. widgets ["abort_btn"] ["command"]) (fn []
        (setv command {
            "type"     "command"
            "command"  "interrupt_main_thread"
            "args"     ""})
        (.put messages-from-interrupter command)))
    (setv queue-monitor (TkTimer root :interval (* 0.25 second)))
    (.add-observer queue-monitor (fn [event]
        (try
            (setv message (.get-nowait messages-to-interrupter))
        (except [Empty]
            (return)))
        (when (and 
                (= (get message "type")    "command")
                (= (get message "command") "exit"))
            (doto root
                (.deiconify)
                (.destroy)) )))
    (setv queue-monitor.active True)
    (doto root
        (.iconify)
        (.mainloop)) )



;import hy

;import tkinter as tk
;from tkinter import ttk
;import queue

;from wavesynlib.interfaces.timer.tk import TkTimer
;from wavesynlib.widgets.tk.desctotk import hywidgets_to_tk

;from .widgets import main_panel



;def main(messages_from_interrupter, messages_to_interrupter):
    ;root = tk.Tk()
    ;root.title('WaveSyn-Interrupter')
    ;root.protocol('WM_DELETE_WINDOW', lambda:None)
    ;root.wm_attributes('-topmost', True)
    ;widgets_desc = [main_panel]
    ;widgets = hywidgets_to_tk(root, widgets_desc)
    ;def on_abort():
        ;command = {'type':'command', 'command':'interrupt_main_thread', 'args':''}
        ;messages_from_interrupter.put(command)
    ;widgets["abort_btn"]["command"] = on_abort

    ;queue_monitor = TkTimer(root, interval=250) 
    
    ;@queue_monitor.add_observer
    ;def queue_observer(*args, **kwargs):
        ;try:
            ;message = messages_to_interrupter.get_nowait()
        ;except queue.Empty:
            ;return
         
        ;if message['type']=='command' and message['command']=='exit':
            ;root.deiconify()
            ;root.destroy()
            
    ;queue_monitor.active = True
        
    ;root.iconify()
    ;root.mainloop()
