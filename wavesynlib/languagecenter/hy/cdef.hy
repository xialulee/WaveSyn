;(defmacro compound [typename name fields]
;    `(defclass ~name [~typename]
;        [-fields- 
;	    ~(lfor i (range 0 (len fields) 2)
;	        `(, 
;		    ~(str (get fields (+ i 1)))
;		    ~(get fields i)))]))


(defmacro compound [typename name fields]
    (setv class-fields [])
    (if-not (symbol? typename) (do ;if not symbol, should be a list.
        (for [k (range 1 (len typename) 2)]
            (if (= (str (nth typename k)) "pack")
                (class-fields.extend ['-pack- (nth typename (inc k))])))
        (setv typename (first typename))))
    (setv field-list [])
    (setv anonymous-list [])
    (for [k (range 0 (len fields) 2)]
        (setv type-obj (nth fields k))
        (setv field-name (-> (nth fields (inc k)) (str) (mangle)))
        (setv field-width 0)
        (if-not (symbol? type-obj) (do
            ; if not symbol, should be a list or expression.
            (if (= (type type-obj) (type '())) ; a expression.
                (setv type-obj `(~@type-obj))
            (do ; else a list
                (if (= "anonymous" (str (first type-obj))) (do
                    (anonymous-list.append field-name)
                    (type-obj.pop 0)))
                (if (instance? int (last type-obj))
                    (setv field-width (last type-obj)))
                (setv type-obj (first type-obj))))))
            (setv field-desc [field-name type-obj])
        (if field-width (field-desc.append field-width))
        (field-list.append `(tuple ~field-desc)))
    (if anonymous-list 
        (class-fields.extend ['-anonymous- `(tuple ~anonymous-list)]))
    (class-fields.append '-fields-)
    (class-fields.append field-list)
    `(defclass ~name [~typename] ~class-fields))

;; Examples
;(import [ctypes [*]])
;
;; Basic Usage
;(compound Structure Point [
;    c_int x
;    c_int y])
;
;; Setting _pack_
;(compound [Structure pack 32] Point [
;    c_int x
;    c_int y])
;
;; Bit fields
;(compound Structure Int [
;    [c_int 16] first-16
;    [c_int 16] second-16])
;
;; Anonymous
;(compound Union -U [
;    (POINTER TYPEDESC) lptdesc
;    (POINTER ARRAYDESC) lpadesc
;    HREFTYPE hreftype])
;
;(compound Structure TYPEDESC [
;    [anonymous -U] u
;    VARTYPE vt])

