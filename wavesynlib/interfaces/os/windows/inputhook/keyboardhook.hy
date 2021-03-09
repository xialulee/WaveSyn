(require [wavesynlib.languagecenter.hy.win32def [import-func]])
(require [wavesynlib.languagecenter.hy.utils [super-init]])

(import-func user32
    SetWindowsHookExA
    UnhookWindowsHookEx
    CallNextHookEx)

(import [win32con [WM-KEYDOWN WM-KEYUP WH-KEYBOARD-LL]])
(import atexit)

(import [wavesynlib.languagecenter.wavesynscript [ModelNode]])
(import [wavesynlib.languagecenter.datatypes.wintypes.hook [KHOOKPROC]])
(import [wavesynlib.interfaces.os.windows.inputsender.utils [send-mouse-input]])



(defclass -KeyToMouse [] 
    (defn --init-- ^None [self ^str mouse-btn]
        (setv 
            self.--previous  None
            self.--mouse-btn mouse-btn))
            
    (defn --callback ^bool [self ^str key-stat]
        (if (= self.--previous key-stat)
            (return True)
        #_else (do
            (setv self.--previous key-stat)
            (send-mouse-input #** {
                "dx"      0
                "dy"      0
                "button"  self.--mouse-btn
                #** (cond
                    [(= key-stat "keydown") {"press"   True}]
                    [(= key-stat "keyup")   {"release" True}]
                    [True (raise (ValueError "key_stat not supported."))])})
            (return True))))
            
    (defn on-keydown ^bool [self] 
        (return (.--callback self "keydown")))
        
    (defn on-keyup ^bool [self]
        (return (.--callback self "keyup"))))


(defclass KeyboardHook [ModelNode]
    (defn --init-- ^None [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs)
        (setv 
            self.--remap    {}
            self.--hkhook   None
            self.--c-khook  (KHOOKPROC self.--khookproc)))
            
    (defn add-key-to-mouse [self ^int key ^str mouse-btn]
        (setv mapobj (-KeyToMouse :mouse-btn mouse-btn))
        (assoc self.--remap key mapobj))
        
    (defn --khookproc [self nCode wParam lParam]
        (setv 
            vk-code lParam.contents.vkCode
            mapobj  (.get self.--remap vk-code None))
        (when mapobj 
            (setv eat 
                ((.get {
                        WM-KEYDOWN mapobj.on-keydown
                        WM-KEYUP   mapobj.on-keyup}
                    wParam (fn [] False))) )
            (when eat (return -1)))
        (return (CallNextHookEx self.--hkhook nCode wParam lParam)))
        
    (defn hook [self]
        (setv self.--hkhook (SetWindowsHookExA WH-KEYBOARD-LL self.--c-khook None 0))
        (unless self.--hkhook
            (raise (OSError "Failed to setup global keyboard hook."))))
            
    (defn unhook [self]
        (UnhookWindowsHookEx self.--hkhook))
        
    (defn unhook-at-exit [self]
        (atexit.register self.unhook)))