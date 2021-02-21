
class Bank(object):
    def __init__(self):
        self._money = 100000
 
    @property
    def money(self):
        """Get the money available."""
        return self._money