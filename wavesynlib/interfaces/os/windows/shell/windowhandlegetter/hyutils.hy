(require [hy.contrib.loop [loop]])
(require [wavesynlib.languagecenter.hy.cdef [→]])
(require [wavesynlib.languagecenter.hy.win32def [import-func]])

(import [ctypes [byref]])
(import [ctypes.wintypes [POINT]])



(import-func user32 
    GetCursorPos
    GetParent
    WindowFromPoint
    GetForegroundWindow)



(defn get-foreground [] (GetForegroundWindow) )


(defn get-toplevel [child]
    (loop [[c child]]
        (setv p (GetParent c) ) 
        (if-not p
            c
        #_else 
            (recur p) ) ) )


(defn get-hwnd-from-point [x y &optional [toplevel True]]
    (setv p (POINT :x x :y y) ) 
    (setv h (WindowFromPoint p) ) 
    (if toplevel
        (get-toplevel h) 
    #_else
        h) )


(defn get-hwnd-from-cursor-pos [&optional [toplevel True]]
    (setv cursor-pos (POINT)) 
    (GetCursorPos #→ cursor-pos) 
    (get-hwnd-from-point cursor-pos.x cursor-pos.y toplevel) )
