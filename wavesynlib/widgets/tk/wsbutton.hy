(require [wavesynlib.languagecenter.hy.utils [super-init defprop]])

(import [pathlib [Path]])
(import tkinter)
(import [tkinter.ttk [Button]])
(import [PIL [ImageTk]])
(import [typing [Any]])

(import [wavesynlib.languagecenter.datatypes [CommandObject]])
(import [.utils.loadicon [load-icon]])



(defclass WSButton [Button]
    (defn --init-- [self &rest args &kwargs kwargs]
        (setv icon (.pop kwargs "image" None))
        (when icon
            (when (instance? (, Path str) icon)
                (setv icon (load-icon icon :common True)))
            (assoc kwargs "image" icon))
        (setv self.--icon icon)

        (setv command-object (.pop kwargs "command_object" None))

        (super-init #* args #** kwargs)
        
        (when command-object    
            (assoc self "command_object" command-object)))


    (defprop common-icon
        #_getter
        (fn [self]
            self.--icon)
        #_setter
        (fn [self icon]
            (assoc self "image"
                (setx self.--icon (load-icon icon :common True)))) ) 
            
    
    (defn --setitem-- ^None [self ^str key ^Any value]
        (when (= key "command_object")
            (setv 
                command-object         value
                self.--command-object  command-object)
            
            (.add-observer command-object (fn [event]
                (when (= event.name "can_execute_changed")
                    (try
                        (assoc self "state"
                            (if (.can-execute event.sender)
                                "normal"
                            #_else
                                "disabled") ) 
                    (except [tkinter.TclError]
                        #_pass) ) ) ) )

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
