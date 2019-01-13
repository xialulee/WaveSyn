(defmacro/g! query [path &optional name]
    (unless name
        (setv name "") )
    (setv path (str path) )
    (setv idx (.index path "\\") )
    (setv 
        key    (cut path 0 idx) 
        subkey (cut path (inc idx) None) )
    `(do
        (setv ~g!mod (--import-- "winreg") ) 
        (with [
            ~g!key 
            ((getattr ~g!mod "OpenKey") 
                (getattr ~g!mod ~key)
                ~subkey)] 
            ((getattr ~g!mod "QueryValueEx") ~g!key ~name) ) ) )


; Example
; (query HKEY_CLASSES_ROOT\Python.File\Shell\Open\Command)

