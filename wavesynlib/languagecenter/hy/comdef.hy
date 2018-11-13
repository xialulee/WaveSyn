(defmacro interface [interfacesym bases guid methods]
    `(defclass ~interfacesym ~bases [
        -iid- ~guid
	-methods- ~(lfor methinfo methods `(~(first methinfo)
	    ~(second methinfo)
	    ~(str (get methinfo 2))
	    :argtypes
	    ~(get methinfo 3)))]))
