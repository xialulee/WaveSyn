(setv ctypes-name (HySymbol "CTYPES-CE006C7F-2A67-437D-9444-6F2E6D645AA3") )

(defmacro init-cdef []
    `(import [ctypes :as ~ctypes-name]) )



(import [funcparserlib.parser [maybe many]])
(import [hy.model-patterns [
    whole sym brackets pexpr dolike FORM SYM]])



(setv -compound-parser (whole [
    (maybe (brackets (many (+ SYM FORM)))) 
    SYM
    (brackets (many (+ FORM FORM) ) )]) )



(defn -make-compound [type- &rest definition]
    (setv type- 
        (get 
            {"struct" 'Structure 
             "union"  'Union} type-) )
    (setv arg-list       []
          field-list     []
          anonymous-list [])
    (setv [type-args type-name [fields]] 
        (.parse -compound-parser definition) ) 
    (if type-args
        (setv type-args (first type-args) )
    #_else
        (setv type-args []) )
    (for [[name val] type-args]
        (when (= name "endian") 
            (setv type- (HySymbol f"{(.capitalize val)}Endian{type-}") ) )
        (when (= name "pack") 
            (.extend arg-list ['-pack- val]) ) ) 
    (for [[field-type field-name] fields]
        (if (coll? field-type) (do
            (setv [t0 t1] field-type)
            (cond 
            [(= t0 "anonymous")
                (.append anonymous-list (str field-name))
                (setv field-type [t1])]
            [(instance? int t1)
                (setv field-type [t0 t1])]) ) 
        #_else
            (setv field-type [field-type]) )
        (.append field-list `(, ~(str field-name) ~@field-type)))
    (when anonymous-list
        (.extend arg-list ['-anonymous- `(, ~@anonymous-list)]) )
    (.extend arg-list ['-fields- field-list])
    `(defclass ~type-name [(. ~ctypes-name ~type-)]
        (setv ~@arg-list) ) )



;Usage:
;(struct optional:[pack a-integer endian big/little] NAME [
    ;ctypes.c_int x
    ;ctypes.c_int y
    ;; bit field
    ;[ctypes.c_int 16] b
    ;; anonymous
    ;[anonymous -U] a])


(defmacro struct [&rest definition]
    (-make-compound 'struct #* definition) )

(defmacro union [&rest definition]
    (-make-compound 'union #* definition) )



(defmacro/g! make-ptr-type [&rest types]
    `(do
        (setv ~g!POINTER (. ~ctypes-name POINTER) )
        ~@(gfor tp types
            `(setv ~(HySymbol (+ (str tp) "*")) (~g!POINTER ~tp) ) ) ) )

;;Example
; (import [ctypes [*]])
; 
; (make-ptr-type c_int c_float)
; Then you can use c_int* and c_float* as pointer types of 
; c_int and c_float. 



(defmacro funcptrtype [type-name res-type name arg-types]
    (if (= res-type 'void)
        (setv res-type None))
    `(setv ~name 
        (~type-name ~res-type ~@arg-types)))

;;Example
; (import [ctypes [*]])
; (make-ptr-type c_int)
; 
; (funcptrtype CFUNCTYPE 
;     c_int CMPFUNC [c_int* c_int*])
;
; (qsort ia (len ia) (sizeof c_int) 
;     (CMPFUNC (fn [a b]
;         (print "hy_cmp_func" (first a) (first b))
;         0)))



; An alias of ctypes.byref
; Should run "from ctypes import byref"
; before using it. 
(deftag → [expr] `((. ~ctypes-name byref) ~(first expr)))
