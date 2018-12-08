(defn table-to-code [table &optional head]
    (if-not head (do
        (setv head (first table))
	(setv table (rest table))))
    (setv head-code (->> head
        (map str)
	(str.join "|")))
    (setv split-code (->> (len head)
        (* ["---"])
	(str.join "|")))
    (setv rows [head-code split-code])
    (rows.extend 
        (gfor row table (->> row 
	    (map str) 
	    (str.join "|"))))
    (str.join "\n" rows))
