

(defmacro compound [type-name name fields]
    (setv class-fields [])
    (if (coll? type-name) (do 
        ; If not symbol, should be a collection.
        ; If type-name is a collection,
        ; the first item is a symbol represents the type (Structure/Union),
        ; the rest are property name property value pairs;
	; e.g. [Structure pack 32]
	(for [[prop-name prop-value] (-> type-name (rest) (partition))]
            (if (= prop-name "pack")
                (class-fields.extend ['-pack- prop-value])))
        (setv type-name (first type-name))))
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
; compound [Structure pack 32] Point [
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



(defmacro funcptr [type-name res-type name arg-types]
    (if (= res-type 'void)
        (setv res-type None))
    `(setv ~name 
        (~type-name ~res-type ~@arg-types)))

;;Example
; (import [ctypes [*]])
; 
; (funcptr CFUNCTYPE 
;     c_int CMPFUNC [(POINTER c_int) (POINTER c_int)])
;
; (qsort ia (len ia) (sizeof c_int) 
;     (CMPFUNC (fn [a b]
;         (print "hy_cmp_func" (first a) (first b))
;         0)))

