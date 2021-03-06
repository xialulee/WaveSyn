(require [hy.extra.anaphoric [*]])
(import [hy.contrib.walk [postwalk]])

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



(traveller TableExtractor 
    (shared 
        tables        []
        current-table None
        current-row   None) 
    (match table
        (enter 
            (setv current-table []) 
            (.append tables current-table) ) 
        (match tr
            (enter 
                (setv current-row []) 
                (.append current-table current-row) ) 
            (match td 
                (enter 
                    (.append current-row "") ) 
                (match p
                    (enter (+= (. current-row [-1]) "\n") ) ) 
                (data (+= (. current-row [-1] ) data) ) ) ) ) 
    (finish tables) ) 



(defn get-table-text [html-code &optional strip]
    (setv strip-func (if strip str.strip identity))
    (defn walking [item]
        (if (instance? str item)
            (strip-func item)
        #_else
            item) ) 
    (setv tables (TableExtractor html-code))
    (postwalk walking tables) )



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

