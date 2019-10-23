

(defmacro compound [type-name name &rest args]
    (setv class-fields [])

    (if-not (symbol? name)
        (raise (TypeError "Name of a struct should be a symbol.")))
    
    (setv len-args (len args))
    (cond ; Do not have struct properties such as pack.
          ; The first item of args is fields.
          [(= len-args 1) (setv props [] 
                                fields (first args))]
	  ; len args == 2 means
	  ; the first item is struct property
	  ; and the second one is the fields.
          [(= len-args 2) (setv props (first args) 
                                fields (second args))])

    (for [[prop-name prop-value] (partition props)]
        (if (= prop-name "pack")
            (class-fields.extend ['-pack- prop-value])))

    (setv field-list [])
    (setv anonymous-list [])

    ; Analyzing fields
    (for [[type-obj field-name] (partition fields)]
        (setv field-name (-> field-name (str) (mangle)))
        (setv field-width 0)
        (if (coll? type-obj) (do
            ; If not symbol, should be a collection or an expression.
	    ; If type-obj is a collection, it includes field type
	    ; and extra information;
	    ; e.g. [anonymous -U] represents the field is type -U
	    ; and this field is an anonymous field, and
	    ; [c_int 16]
            (if (= (type type-obj) (type '())) 
	        ; An expression.
                (setv type-obj `(~@type-obj))
            (do ; else a list
                (if (= "anonymous" (str (first type-obj))) (do
                    (anonymous-list.append field-name)
                    (type-obj.pop 0)))
                (if (instance? int (last type-obj))
		    ; Bit field. 
                    (setv field-width (last type-obj)))
                (setv type-obj (first type-obj))))))
            (setv field-desc [field-name type-obj])
        (if field-width (field-desc.append field-width))
	; ctypes.Structure/Union only supports field descriptions
	; in tuple type. 
        (field-list.append `(tuple ~field-desc)))
    (if anonymous-list 
        (class-fields.extend ['-anonymous- `(tuple ~anonymous-list)]))
    (class-fields.extend ['-fields- field-list])
    `(defclass ~name [~type-name] ~class-fields))

;; Examples
; import [ctypes [*]])
;
;; Basic Usage
; compound Structure Point [
;    c_int x
;    c_int y])
;
;; Setting _pack_
; compound Structure [pack 32] Point [
;    c_int x
;    c_int y])
;
;; Bit fields
; compound Structure Int [
;    [c_int 16] first-16
;    [c_int 16] second-16])
;
;; Anonymous
; compound Union -U [
;    (POINTER TYPEDESC) lptdesc
;    (POINTER ARRAYDESC) lpadesc
;    HREFTYPE hreftype])
;
; compound Structure TYPEDESC [
;    [anonymous -U] u
;    VARTYPE vt])



; The following macros provide more convenient way
; for defining structs and unions.

(defmacro/g! -aux-compound [type-name name &rest args]
    (setv len-args (len args))

    (cond [(= len-args 1) (setv props [] 
                                fields (first args))]
          [(= len-args 2) (setv props (first args) 
                                fields (second args))])

    (setv type-name (str type-name))

    (for [[prop-name prop-value] (partition props)]
        (if (= prop-name 'endian) 
            (setv type-name (.join "" 
                [(-> prop-value 
                    (str) 
                    (str.capitalize)) 
                "Endian" 
                type-name]))))
    `(setv ~name ((fn []
        (import ctypes)
        (setv type- (getattr ctypes ~type-name))
        (require wavesynlib.languagecenter.hy.cdef)
        (wavesynlib.languagecenter.hy.cdef.compound type- ~g!TheStruct ~#*args)
        ~g!TheStruct))))



(defmacro struct [name &rest args]
    `(do
        (require wavesynlib.languagecenter.hy.cdef)
        (wavesynlib.languagecenter.hy.cdef.-aux-compound "Structure" ~name ~#*args)))



(defmacro union [name &rest args]
    `(do
        (require wavesynlib.languagecenter.hy.cdef)
        (wavesynlib.languagecenter.hy.cdef.-aux-compound "Union" ~name ~#*args)))



(defmacro/g! make-ptr-type [&rest types]
    `(do
        (import [ctypes [POINTER :as ~g!POINTER]])
        ~@(gfor tp types
            `(setv ~(HySymbol (+ (str tp) "*")) (~g!POINTER ~tp) ) ) ) )

;;Example
; (import [ctypes [*]])
; 
; (make-ptr-type c_int c_float)
; Then you can use c_int* and c_float* as pointer types of 
; c_int and c_float. 



(defmacro funcptr [type-name res-type name arg-types]
    (if (= res-type 'void)
        (setv res-type None))
    `(setv ~name 
        (~type-name ~res-type ~@arg-types)))

;;Example
; (import [ctypes [*]])
; (make-ptr-type c_int)
; 
; (funcptr CFUNCTYPE 
;     c_int CMPFUNC [c_int* c_int*])
;
; (qsort ia (len ia) (sizeof c_int) 
;     (CMPFUNC (fn [a b]
;         (print "hy_cmp_func" (first a) (first b))
;         0)))



; An alias of ctypes.byref
; Should run "from ctypes import byref"
; before using it. 
(deftag → [expr] `(byref ~expr))
