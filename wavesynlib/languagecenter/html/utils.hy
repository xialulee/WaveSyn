(require [hy.extra.anaphoric [*]])

(import [xml.etree [ElementTree]])
(import html)

(require [wavesynlib.languagecenter.hy.htmldef [traveller]])
(require [wavesynlib.languagecenter.hy.xmldef [tag]])

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
    (defn escape [item]
        (-> item (str) (html.escape)))

    (tag table (gfor [idx row] (enumerate iterable)
        (tag tr (gfor item row
            (if (and have-head (not idx))
                (tag th [(escape item)])
            ;else
                (tag td [(escape item)])))))))

