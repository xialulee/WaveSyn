(defn -split-key [path]
    (if (in "\\" path) 
        (setv 
            idx    (.index path "\\")
            key    (cut path 0 idx)
            subkey (cut path (inc idx) None) ) 
    #_else
        (setv 
            key    path
            subkey "") ) 
    (return (, key subkey) ) )



(defmacro/g! query [path &optional name]
    (unless name
        (setv name "") )
    (setv path (str path) )
    (setv [key subkey] (-split-key path))
    `((fn [] 
        (setv ~g!mod (--import-- "winreg") ) 
        (with [
            ~g!key 
            ((getattr ~g!mod "OpenKey") 
                (getattr ~g!mod ~key)
                ~subkey)] 
            ((getattr ~g!mod "QueryValueEx") ~g!key ~name) ) )) )


; Example
; (query HKEY_CLASSES_ROOT\Python.File\Shell\Open\Command)



(defmacro/g! enum-key [path]
    (setv path (str path)) 
    (setv [key subkey] (-split-key path))
    `((fn []
        (setv ~g!mod (--import-- "winreg"))
        (setv ~g!OpenKey (getattr ~g!mod "OpenKey"))
        (setv ~g!EnumKey (getattr ~g!mod "EnumKey"))
        (with [
            ~g!key
            (~g!OpenKey
                (getattr ~g!mod ~key)
                ~subkey)]
            (for [i (count)]
                (try
                    (yield (~g!EnumKey ~g!key i))
                (except [OSError]
                    (break) ) ) ) ) )) )

