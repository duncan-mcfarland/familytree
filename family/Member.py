class Member(object):

    def __init__(self, name, born, died, places):
        self.name = name
        self.born = born
        self.died = died
        self.places = places

    def __str__(self):
        return self.name + " Born: " + self.born + " Died: " + self.died

    def printPlace(self):
        if len(self.places) > 0:
            for place in self.places.values():
                print(place)

    def getName(self):
        return self.name

    def getPlaces(self):
        return self.places

    def getAlive(self, year):
        """This method returns an array that includes the dates this person was alive. Consider re-doing this,
        as the lists must be very long..."""
        if year == "":
            return False

        if self.born == "00000000" and self.died != "00000000":  # Only death date, assume died @ 20
            diedInt = int(self.died[:4])
            aliveYears = range(diedInt-20, diedInt+1)
        elif self.born != "00000000" and self.died == "00000000":  # Only born date, assume died in infancy
            bornInt = int(self.born[:4])
            aliveYears = range(bornInt, bornInt+1)
        elif self.born != "00000000" and self.died != "00000000":  # Have both dates
            diedInt = int(self.died[:4])
            bornInt = int(self.born[:4])
            aliveYears = range(bornInt, diedInt+1)
        else:
            aliveYears = []

        for yearAlive in aliveYears:
            if int(year) == int(yearAlive):
                return True
        return False

    def getBorn(self):
        return self.born

    def getDied(self):
        return self.died

