(import [xml.etree [ElementTree]])
(import html)
(import [html [parser]])



; See http://stackoverflow.com/a/9662410
(defn remove-tags [html-code]
    (as-> html-code it
        (ElementTree.fromstring it)
	(it.itertext)
	(str.join "" it)))


(defclass -TableTextExtractor [parser.HTMLParser]
    (defn --init-- [self tables]
        ((. (super) --init--))
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
              [(= tag "p") (do
                  (setv cell (. self --current-row [-1]))
		  (if cell 
                      (setv (. self --current-row [-1])
		            (+ cell "\n"))))]))
    
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
        (setv row-str (str.join " " (map 
            (comp
                (fn [item] (str.join "" [start-tag item stop-tag]))
                html.escape
                str) 
            row)))
        (str.join "" ["<tr> " row-str " </tr>"]))

    (setv rows [] tb iterable)

    (if have-head (do
        (setv row (first iterable))
	(rows.append (row-to-str row "<th>" "</th>"))
        (setv tb (rest iterable))))

    (rows.extend (map (fn [row] (row-to-str row "<td>" "</td>")) tb))
    (setv table-str (str.join "\n" rows))
    (str.join "\n" ["<table>" table-str "</table>"]))

