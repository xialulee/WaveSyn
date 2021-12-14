(require [hy.contrib.loop [loop]])
(require [wavesynlib.languagecenter.hy.utils [super-init]])
(require [wavesynlib.languagecenter.wavesynscript.macros [
    init-wavesynscript-macros
    BindLazyNode]])
(init-wavesynscript-macros)

(import [time [sleep]])

(import [wavesynlib.languagecenter.wavesynscript [
    ModelNode WaveSynScriptAPI Scripting code-printer]])
(import [wavesynlib.interfaces.os.windows.inputsender [
    utils constants]])



(setv name-to-code {})
(for [k (range 1 25)]
    (assoc name-to-code 
        f"f{k}"
        (getattr constants f"VK_F{k}")))
(for [k (range 10)]
    (setv code (+ (ord "0") k))
    (assoc name-to-code
        (chr code)
        code))
(for [k "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    (setv code (ord k))
    (assoc name-to-code k code)
    (assoc name-to-code (.lower k) code))
(for [k ["ctrl" "control" "alt" "menu" "shift"]]
    (assoc name-to-code 
        k
        (getattr constants f"VK_{(.upper k)}" )))
(for [k ["lctrl" "lcontrol" "left ctrl" "left control"]]
    (assoc name-to-code k constants.VK_LCTRL))
(for [k ["rctrl" "rcontrol" "right ctrl" "right control"]]
    (assoc name-to-code k constants.VK_RCTRL))
(for [k ["lalt" "lmenu" "left alt" "left menu"]]
    (assoc name-to-code k constants.VK_LALT))
(for [k ["ralt" "rmenu" "right alt" "right menu"]]
    (assoc name-to-code k constants.VK_RALT))
(for [k ["left" "right" "up" "down"]]
    (assoc name-to-code k (getattr constants f"VK_{(.upper k)}")))



(defclass MouseSender [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs))
        
    #@(WaveSynScriptAPI
    (defn click-repeatedly [self times &optional absolute [dx 0] [dy 0] [delay 0] [interval 0]]
        "Left click several times.

times:       how many times to click.
absolute:    the given coordinate is absolute or not.
dx:          x-coordinate.
dy:          y-coordinate.
delay(s):    the click will wait (delay) seconds.
interval(s): the interval between clicks."
        (sleep delay) 
        (loop [[k times]]
            (if (zero? k)
                None
            #_else (do
                (utils.send-mouse-input dx dy "left" absolute)
                (sleep interval) 
                (recur (dec k) ) ) ) ) ) ) )



(defclass KeySender [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs))
        
    (defn send [self key &optional modifiers press release [interval 0]]
        (when (and (not press) (not release))
            (.send self key modifiers :press True)
            (when (pos? interval) 
                (sleep interval))
            (.send self key modifiers :release True)
            (return)) 
        
        (setv key (.lower key))
        (setv code (. name-to-code [key]))
        
        (if modifiers
            (setv mod-codes (lfor m modifiers (. name-to-code [m]))) 
        #_else
            (setv mod-codes [])) 
            
        (defn key-act []
            (utils.send-key-input code :press press :release release))
            
        (defn modifier-act []
            (for [modifier mod-codes]
                (utils.send-key-input modifier :press press :release release)))
                
        (if press (do
            (modifier-act)
            (key-act))
        #_else (do
            (key-act)
            (modifier-act))) ) )



(defclass -Condition [])



(defclass -DefaultCondition [-Condition])



(defclass -ExecPathCondition [-Condition]
    (defn --init-- [self exec-path]
        (setv self.--exec-path exec-path) ) 
        
    #@(property
    (defn exec-path [self]
        self.--exec-path) ) )



(defclass -Setting []
    (defn --init-- [self] ) )



(defclass -Profile []
    (defn --init-- [self condition]
        (setv 
            self.--condition condition
            self.--settings  []) ) 

    #@(property
    (defn condition [self]
        self.--condition) )
            
    (defn add-setting [self setting]
        (.append self.--settings setting) ) )



(defclass MacroManager [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (setv 
            self.--profiles {}
            self.--current-profile None
            self.--current-setting None) )

    (defn add-profile [self profile]
        (assoc self.--profiles profile.condition profile) ) 

    #@(property
    (defn -current-profile [self]
        (with [(code-printer :print- False)]
            (setv exec-path (
                .get-execpath-from-foreground 
                self.root-node.interfaces.os.windows.processes.utils)) )
        (setv condition (-ExecPathCondition exec-path)) 
        (.get self.--profiles None) ))

    #@(property
    (defn -current-setting [self]
        None))
        
    (defn set-trigger [self slot &optional hotkey] ) )



(defclass InputSenders [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs)
        (setv self.key-sender (KeySender) )
        (setv self.mouse-sender (MouseSender) )
        (BindLazyNode 
            self.macro-manager MacroManager)) ) 

