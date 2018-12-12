(defn table-to-code [table &optional head]
    (if-not head 
        (setv head (first table) 
              table (rest table)))
    (setv head-code (->> head
        (map str)
	(.join "|")))
    (setv split-code (->> (len head)
        (* ["---"])
	(.join "|")))
    (setv rows [head-code split-code])
    (rows.extend 
        (gfor row table (->> row 
	    (map str) 
	    (.join "|"))))
    (.join "\n" rows))
