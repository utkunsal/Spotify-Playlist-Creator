class Track:
    def __init__(self, name, id, popularity, artist):
        self.name = name
        self.id = id
        self.popularity = popularity
        self.artist = artist

    def __str__(self):
        return self.name + " by " + self.artist
