(require [hy.extra.anaphoric [*]])
(require [wavesynlib.languagecenter.hy.utils [call= dyn-defprop defprop freeze super-init]])
(require [wavesynlib.languagecenter.hy.cdef [init-cdef →]])
(init-cdef)

(import ctypes)
(import [ctypes [byref]])
(import [ctypes.wintypes [UINT MSG]])
(import [win32con [WM-HOTKEY PM-REMOVE]])
(setv -user32 ctypes.windll.user32)
(import [copy [deepcopy]])
(import [queue [Queue Empty]])

(import [wavesynlib.languagecenter.wavesynscript [ModelNode]])
(import [wavesynlib.languagecenter.designpatterns [Observable]])

(setv -ID-UPPER-BOUND (inc 0xBFFF))



(defclass Modifiers [UINT]
    (setv -attr-names [
        [0 "alt"] [1 "ctrl"] [2 "shift"] [3 "win"] [14 "norepeat"]])
    (for [[bitpos name] -attr-names] 
        (dyn-defprop name 
            #_getter
            (freeze [bitpos]
            (fn [self]
                (& self.value (<< 1 bitpos))))
            #_setter
            (freeze [bitpos]
            (fn [self val]
                (if val
                    (|= self.value (<< 1 bitpos))
                    (&= self.value (~ (<< 1 bitpos)))))))))



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



(defclass GlobalHotkeyManager [ModelNode Observable]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs)
        (setv self.--hotkey-info {})
        (setv self.--repeater None) 
        (setv self.--queue (Queue))
        (.add-observer self (fn [id- info]
            (ap-if (. info [2]) (it) ) ) ) )

    (defn on-connect [self]
        (setv self.--timer (.create-timer self.root-node :interval 50) ) 
        (.add-observer self.--timer (fn []
            (try
                (while True
                    (setv id- (.get-nowait self.--queue) )
                    (.notify-observers self 
                        id- 
                        (get self.--hotkey-info id-) ) #_while)
            (except [Empty]) ) ) ) )

    (defn set-timer-interval [self interval]
        (setv self.--timer.interval interval) )

    (defn start-timer [self]
        (setv self.--timer.active True) )

    (defn stop-timer [self]
        (setv self.--timer.active False) )
        
    (defn --get-new-id [self]
        (for [i (range 1 -ID-UPPER-BOUND)]
            (when (not-in i self.--hotkey-info)
                (return i) #_when) #_for) )
                
    (defprop -repeater
        #_getter
        (fn [self]
            (unless self.--repeater
                (setv self.--repeater 
                    (.create_repeater_thread self.root-node.thread-manager (fn []
                        (setv msg (MSG))
                        (when (and 
                                (-user32.PeekMessageW #→[msg] -1 0 0 PM-REMOVE)
                                (= msg.message WM-HOTKEY))
                            (setv id- msg.wParam)
                            (.put self.--queue id-) ) ) ) )
                (setv self.--repeater.daemon True)
                (.start self.--repeater) 
                (.start-timer self) )
            self.--repeater))
                            
    (defprop hotkey-info
        #_getter
        (fn [self]
            (deepcopy self.--hotkey-info)))
        
    (defn register [self modifiers vk &optional func]
        (call= modifiers -modifier-names-to-obj)
        (setv id- (.--get-new-id self))
        (setv success (.do-once 
            self.-repeater
            (fn [] (-user32.RegisterHotKey None id- modifiers vk))))
        (when success
            (assoc self.--hotkey-info id- (, modifiers vk func)) )
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
                (del (get self.--hotkey-info id-)) #_when) )
            
    (defn unregister-all [self]
        (for [id- (tuple (.keys self.--hotkey-info))]
            (.unregister self :id- id-))))

