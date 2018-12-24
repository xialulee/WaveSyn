(require [wavesynlib.languagecenter.hy.utils [call=]])

(import ctypes)
(import [ctypes [byref]])
(import [ctypes.wintypes [UINT MSG]])
(import [win32con [WM-HOTKEY PM-REMOVE]])
(setv -user32 ctypes.windll.user32)
(import [copy [deepcopy]])

(import [wavesynlib.languagecenter.wavesynscript [ModelNode]])

(setv -ID-UPPER-BOUND (inc 0xBFFF))



(defclass Modifiers [UINT]
    (setv -attr-names [
        [0 "alt"] [1 "ctrl"] [2 "shift"] [3 "win"] [14 "norepeat"]])
    (for [[idx name] -attr-names]
        (setv -temp (property (fn [self &optional [idx idx]] 
            (& self.value (<< 1 idx)))))
        (assoc (locals) name (.setter -temp (fn [self val &optional [idx idx]]
            (if val 
                (|= self.value (<< 1 idx))
                (&= self.value (~ (<< 1 idx)))))))))



(defn -modifier-name-convert [name]
    (setv name (.lower name))
    (cond 
    [(in name ["alt" "menu"]) "alt"]
    [(in name ["ctrl" "control"]) "ctrl"]
    [(= name "shift") "shift"]))



(defn -modifier-names-to-obj [modifiers]
    (setv modobj (Modifiers 0))
    (for [modifier modifiers]
        (setattr modobj (-modifier-name-convert modifier) 1))
    modobj)



(defclass GlobalHotkeyManager [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (.--init-- (super) #* args #** kwargs)
        (setv self.--hotkey-info {})
        (setv self.--repeater None))
        
    (defn --get-new-id [self]
        (for [i (range 1 -ID-UPPER-BOUND)]
            (when (not-in i self.--hotkey-info)
                (return i))))
                
    #@(property 
    (defn -repeater [self]
        (unless self.--repeater
            (setv self.--repeater 
                (.create_repeater_thread self.root-node.thread-manager (fn []
                    (setv msg (MSG))
                    (when (and 
                            (-user32.PeekMessageW (byref msg) -1 0 0 PM-REMOVE)
                            (= msg.message WM-HOTKEY))
                        (setv info (.get self.--hotkey-info msg.wParam (fn [] None)))
                        ((. info [-1]))))))
            (setv self.--repeater.daemon True)
            (.start self.--repeater))
        self.--repeater))
                            
    #@(property
    (defn hotkey-info [self]
        (deepcopy self.--hotkey-info)))
        
    (defn register [self modifiers vk func &optional [call-in-main-thread True]]
        (call= modifiers -modifier-names-to-obj)
        (if call-in-main-thread
            (defn f [] ((.main-thread-do self.root-node.thread-manager :block True) func))
            (setv f func))
        (setv id- (.--get-new-id self))
        (setv success (.do-once 
            self.-repeater
            (fn [] (-user32.RegisterHotKey None id- modifiers vk))))
        (when success
            (assoc self.--hotkey-info id- (, modifiers vk f)))
        success)
        
    (defn unregister [self &optional modifiers vk id-]
        (when modifiers
            (call= modifiers -modifier-names-to-obj))
        (unless id-
            (for [[key val] (.items self.--hotkey-info)]
                (when (and (= (first val) modifiers) (= (second val) vk))
                    (setv id- key)
                    (break))))
        (when id-
            (.do-once 
                self.-repeater 
                (fn []
                    (-user32.UnregisterHotKey None id-)))
            (del (get self.--hotkey-info id-))))
            
    (defn unregister-all [self]
        (for [id- (tuple (.keys self.--hotkey-info))]
            (.unregister self :id- id-))))

