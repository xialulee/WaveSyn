(require [hy.extra.anaphoric [*]])

(import [xml.etree [ElementTree]])
(import html)
(import [html [parser]])



; See http://stackoverflow.com/a/9662410
(defn remove-tags [html-code]
    (->> html-code
        (ElementTree.fromstring)
        (.itertext)
        (.join "")))


(defclass -TableTextExtractor [parser.HTMLParser]
    (defn --init-- [self tables]
        (.--init-- (super))
        (setv self.--tables tables)
        (setv self.--current-table None)
        (setv self.--current-row None)
        (setv self.--in-td-tag False))
	
    (defn handle-starttag [self tag attrs]
        (cond [(= tag "table") (do
                  (setv table [])
                  (setv self.--current-table table)
                  (self.--tables.append table))]
              [(= tag "tr") (do
                  (setv row [])
                  (self.--current-table.append row)
                  (setv self.--current-row row))]
              [(= tag "td") (do
                  (setv self.--in-td-tag True)
                  (self.--current-row.append ""))]
              [(= tag "p") (ap-if (. self --current-row [-1])
                      (setv (. self --current-row [-1]) 
                            (+ it "\n")))]))
    
    (defn handle-endtag [self tag]
        (if (= tag "td")
            (setv self.--in-td-tag False)))
	    
    (defn handle-data [self data]
        (if self.--in-td-tag
            (+= (. self --current-row [-1]) data))))



(defn get-table-text [html-code]
    (setv retval [])
    (setv extractor (-TableTextExtractor retval))
    (extractor.feed html-code)
    retval)



(defn iterable-to-table [iterable &optional have-head]
    (defn row-to-str [row start-tag stop-tag]
        (setv row-str (.join " " (map 
            (comp
                (fn [item] (.join "" [start-tag item stop-tag]))
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

