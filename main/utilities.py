""" Misc Useful Utilities """

class prev_next:
    """ Make a series of prev, next links.  I'd be a nice guy if I
    took the time to add 'first' and 'last' links, plus links to each
    subset of pages."""
    def __init__(self, start=None, per_page=None):

        if not per_page: self.per_page=25
        else: self.per_page = int(per_page)

        if not start: self.start=0
        else: self.start = int(start)

        self.next = self.start + self.per_page
        self.prev = self.start - self.per_page
        if self.prev < 0: self.prev = 0

        self.first = True
        if start: self.first = False

        if self.per_page == 25: self.toggle = 100
        else: self.toggle = 25

    
    
    
        

    





    
