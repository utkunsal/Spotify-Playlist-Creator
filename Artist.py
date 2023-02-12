class Artist:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def __str__(self):
        return self.name

    def __eq__(self, other): 
        # when comparing with an object of another class, returns false
        if not isinstance(other, Artist): return False
        # when comparing with an object of the same class, compares by their ids
        return self.id == other.id
