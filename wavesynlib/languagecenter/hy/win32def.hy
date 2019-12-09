(require [wavesynlib.languagecenter.hy.cdef [init-cdef struct]])
(init-cdef)
(import [ctypes.wintypes [WORD DWORD]])



(defmacro/g! import-func [dll-name &rest func-names]
    `(do
        (import [ctypes [windll :as ~g!windll]]) 
        ~@(lfor func-name func-names
            `(setv ~func-name (. ~g!windll ~dll-name ~func-name) ) ) ) )



(struct BITMAPFILEHEADER [pack 1] [
    WORD  bfType
    DWORD bfSize
    WORD  bfReserved1
    WORD  bfReserved2
    DWORD bfOffBits])
