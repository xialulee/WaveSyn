import quantities as pq



class Constants:
    
    @property
    def c(self):
        return 299792458 * pq.meter/pq.second



constants = Constants()
