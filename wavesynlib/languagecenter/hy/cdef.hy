(defmacro compound [typename name fields]
    `(defclass ~name [~typename]
        [-fields- 
	    ~(lfor i (range 0 (len fields) 2)
	        `(, 
		    ~(str (get fields (+ i 1)))
		    ~(get fields i)))]))



