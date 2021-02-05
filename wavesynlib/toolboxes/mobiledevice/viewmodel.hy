(import [tkinter [IntVar BooleanVar]])
(import [wavesynlib.languagecenter.datatypes [CommandObject]])
(import [wavesynlib.languagecenter.wavesynscript [code-printer]])



(defclass ViewModel []
    (defn --init-- [self window]
        (print window)
        (setv self.transfer-progress (IntVar) ) 
        (setv self.idle (BooleanVar) ) 
        (.set self.idle True)
                
        (setv self.read-clipb (CommandObject
            (fn []
                (with [(code-printer)]
                    (window.read-device-clipboard :on-finish None) ) ) ) )
        (.bind-tkvar self.read-clipb self.idle) 
        
        (setv self.write-clipb (CommandObject 
            (fn []
                (with [(code-printer)]
                    (window.write-device-clipboard) ) ) ) ) 
        (.bind-tkvar self.write-clipb self.idle) ) )