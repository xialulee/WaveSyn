(require [hy.extra.anaphoric [*]])

(import [xml.etree [ElementTree]])
(import html)
(import [itertools [chain]])

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

    (defn row-to-str [row tag-name]
        (tag tr (gfor item row 
            (tag (eval tag-name) [(escape item)]))))

    (setv first-row-tag (if have-head "th" "td"))

    (tag table (chain
        [(row-to-str (first iterable) first-row-tag)]
        (ap-map (row-to-str it "td") (rest iterable)))))

