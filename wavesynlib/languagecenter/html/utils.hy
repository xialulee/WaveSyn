(require [hy.extra.anaphoric [*]])

(import [xml.etree [ElementTree]])
(import html)

(require [wavesynlib.languagecenter.hy.htmldef [traveller]])

; See http://stackoverflow.com/a/9662410
(defn remove-tags [html-code]
    (->> html-code
        (ElementTree.fromstring)
        (.itertext)
        (.join "")))



(traveller get-table-text [
    (shared tables        []
            current-table None
            current-row   None
            in-td-flag    False)
    
    (on-enter table 
        (setv current-table [])
        (tables.append current-table))
	
	(on-enter tr 
            (setv current-row [])
            (current-table.append current-row))
	    
            (on-enter td
                (setv in-td-flag True)
                (current-row.append ""))
             
                (on-enter p 
                    (ap-if (. current-row [-1])
                        (setv (. current-row [-1]) (+ it "\n"))))

                (on-data (if in-td-flag 
                    (+= (. current-row [-1]) data)))
            
            (on-leave td (setv in-td-flag False))
	    
    (on-finish tables)])



(defn iterable-to-table [iterable &optional have-head]
    (defn row-to-str [row start-tag stop-tag]
        (setv row-str (.join " " (map 
            (comp
                #%(.join "" [start-tag %1 stop-tag])
                html.escape
                str) 
            row)))
        (.join "" ["<tr> " row-str " </tr>"]))

    (setv rows [] 
          tb iterable)

    (if have-head (do
        (setv row (first iterable))
	(rows.append (row-to-str row "<th>" "</th>"))
        (setv tb (rest iterable))))

    (rows.extend (ap-map (row-to-str it "<td>" "</td>") tb))
    (setv table-str (.join "\n" rows))
    (.join "\n" ["<table>" table-str "</table>"]))

