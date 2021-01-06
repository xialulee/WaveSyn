(require [wavesynlib.languagecenter.hy.utils [super-init]])

(import tkinter)
(import [tkinter.ttk [Button]])
(import [typing [Any]])

(import [wavesynlib.languagecenter.datatypes [CommandObject]])



(defclass WSButton [Button]
    (defn --init-- [self &rest args &kwargs kwargs]
        (setv command-object (.pop kwargs "command_object" None))
        (super-init #* args #** kwargs)
        (when command-object    
            (assoc self "command_object" command-object)))
            
    
    (defn --setitem-- ^None [self ^str key ^Any value]
        (when (= key "command_object")
            (setv 
                command-object         value
                self.--command-object  command-object)
            
            (.add-observer command-object (fn [event]
                (when (= event.name "can_execute_changed")
                    (assoc self "state"
                        (if (.can-execute event.sender)
                            "normal"
                        #_else
                            "disabled") ) )))

            (.change-can-execute command-object)
            (assoc self "command" command-object)
            (return))
        (.--setitem-- (super) key value)) 
        
        
    (defn config [self &kwargs kwargs]
        (setv command-object (.pop kwargs "command_object" None))
        (when command-object
            (assoc self "command_object" command-object))
        (.config (super) #** kwargs)))



(defmain []
    (setv root (tkinter.Tk))
    (.pack (tkinter.Label root :text "You cannot quit until input something."))
    (setv entry-text (tkinter.StringVar ""))
    (.pack (setx entry (tkinter.Entry root :textvariable entry-text)))
    (setv command-object (CommandObject root.destroy (fn [] (!= (.get entry-text) ""))))
    (.trace entry-text "w" (fn [&rest args] (.change-can-execute command-object)))
    (.pack (setx button (WSButton root :text "Quit" :command-object command-object)))
    ;(.config button :command-object command-object)
    (.mainloop root))
