(import [datetime [timedelta]])



(defclass WeekNumberTool []
    (defn --init-- [self date weeknum]
        (-= weeknum 1)
	(setv self.--first-monday
	    (- date 
	       (timedelta :weeks weeknum
                          :days (date.weekday)))))
		
    (defn get-date [self weeknum weekday]
        (-= weeknum 1)
        (+ self.first-monday
	   (timedelta :weeks weeknum
                      :days weekday)))

    (defn get-weeknum [self date]
        (setv delta (-> date
	    (- self.first-monday)
	    (. days)
	    (// 7)))
	(inc delta))

    #@(property
    (defn first-monday [self]
        (. self --first-monday))))

