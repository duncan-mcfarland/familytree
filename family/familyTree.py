from gmplot import gmplot
from Member import Member
from geopy import Nominatim

def grabDate(dateString):
    """This function takes in a string in most typical formats and returns an eight digit normalized date code
    in the format of "YYYYMMDD" (string). Currently accepted formats are: YYYY, YYYY-MM-DD, YYYY-YYYY, MM/DD/YYYY,
    Mon YYYY, Mon DD YYYY, and DD Mon YYYY where 'Mon' is the written month, in three-letter or full word form."""

    # Associate written months to numbers for processing
    monthList = {"jan":'01', "feb":'02', "mar":'03', "apr":'04', "may":'05', "jun":'06' , "jul":'07', "aug":'08',
                 "sep":'09', "sept":"09", "oct":'10', "nov":'11', "dec":'12', "january":'01', "february":'02', "march":'03',
                 "april":'04', "june":'06', "july":'07', "august":'08', "september":'09', "october":'10',
                 "november":'11', "december":'12'}

    # For our purposes, knowing 'about' doesn't do us much good. Strip away extra words.
    testList = ["bef", "abt", "est", "aft", "ca", "pre", "before"]

    # For easier processing, split our string into an array
    dateArray = dateString.split(" ")

    # Check to see if the current element is on our list of words, and if it is, strip it out.
    for elem in dateArray:
        if elem in testList:
            dateString = dateString.replace(elem, "")

    # Get rid of trailing spaces and newlines just in case, and as a final layer of cleaning.
    dateString = dateString.strip()

    # Begin checking for different date formats. There are a lot, so if I missed any, the final 'return' statement
    # is to return 8 0's. We'll have to accept some loss here.
    if len(dateString) == 10 and dateString[4] == '-': # FORMAT YYYY-MM-DD
        return dateString[:4] + dateString[5:7] + dateString[8:]

    if len(dateString) == 4: # FORMAT YYYY
        return dateString + "00" + "00"

    if dateString[4] == '-': # FORMAT YYYY-YYYY
        return dateString[:4] + "00" + "00"

    if dateString[-5] == '/':  # FORMAT MM/DD/YYYY
        dateArray = dateString.split("/")

        # Add heading 0's if date only had one digit.
        for x in range(2):
            if len(dateArray[x]) == 1:
                dateArray[x] = "0" + dateArray[x]

        return dateArray[2] + dateArray[0] + dateArray[1]

    # Found I was having a problem missing some extra words, this cleaned those up.
    test = [ele for ele in testList if(ele in dateString.lower())]
    if test:
        return dateString[-4:] + "0000"

    # The rest of the date format included month words, so I split them up here to process them a little easier.
    stripDate = dateString.replace(".", "")
    stripDate = stripDate.replace(",", "")
    dateArray = stripDate.split(" ")

    if dateArray[0].lower() in monthList and len(dateArray) == 2:  # FORMAT Mon YYYY
        return dateString[-4:] + monthList[dateArray[0].lower()] + "00"

    elif len(dateArray) == 3:
        if dateArray[0].lower() in monthList:  # FORMAT Mon DD YYYY
            day = dateArray[1]
            if len(day) == 1:
                day = "0" + dateArray[1]
            return dateArray[2] + monthList[dateArray[0].lower()] + day

        if dateArray[1].lower() in monthList:  # FORMAT DD Mon YYYY
            if ' ' in dateString[:2]:
                day = "0" + dateString[0]
            else:
                day = dateString[:2]

            key = dateArray[1].lower()
            key = key[:3]
            return dateString[-4:] + monthList[key] + day

    return "00000000"  # Unrecognized date format

def grabName(nameString):

    nameArray = nameString.split()

    firstName = nameArray[0]
    lastName = nameArray[-1]

    lastName = lastName.replace("/", "")

    return firstName + " " + lastName

def populateMembers():
    """This takes nothing as input, but requires the GEDCOM file's location to be hard-coded here at the beginning.
    It reads through the GEDCOM file, identifying, normalizing, and storing relevant data about family members. It then
    returns an array of the members found."""

    ged = open("mcfarland_tree.ged", "r", encoding="utf-8")  # Open the GEDCOM File, specify encoding

    curLine = ged.readline()  # Initialize my line


    # Initialize my variables
    birthDate = "00000000"
    deathDate = "00000000"
    name = "JOHN DOE"
    memberArray = []
    placeDict = {}
    placeCounter = 0
    resiDate = "00000000"
    left = False
    dateLine = " "

    # While we have stuff left to read...
    while curLine != '':
        # If we haven't hit a new individual yet...
        while curLine[0] != "0":
            # Grab data from inside individual section
            if curLine[:6] == "1 BIRT":
                dateLine = ged.readline()
                while dateLine[0] != "1":
                    if dateLine[:6] == "2 DATE":
                        birthDate = grabDate(dateLine[7:-1])  # Grab birthday, store date code
                    elif dateLine[:6] == "2 PLAC":
                        placeStr = dateLine[7:]
                        placeStr = placeStr.strip("\n")
                        place = {birthDate: placeStr}
                        placeDict[placeCounter] = place
                        placeCounter += 1
                    dateLine = ged.readline()
                    left = True
            if curLine[:6] == "1 DEAT":
                dateLine = ged.readline()
                while dateLine[0] != "1":
                    if dateLine[:6] == "2 DATE":
                        deathDate = grabDate(dateLine[7:-1])  # Grab death day, store date code
                    elif dateLine[:6] == "2 PLAC":
                        dPlaceStr = dateLine[7:]
                        dPlaceStr = dPlaceStr.strip("\n")
                        dPlace = {deathDate: dPlaceStr}
                        placeDict[placeCounter] = dPlace
                        placeCounter += 1
                    dateLine = ged.readline()
                    left = True

            if curLine[:6] == "1 NAME":
                name = grabName(curLine[7:-1])  # Grab and store name

            if curLine[:6] == "1 RESI":
                dateLine = ged.readline()
                while dateLine[0] != "1":
                    if dateLine[:6] == "2 DATE":
                        resiDate = grabDate(dateLine[7:-1])  # Grab birthday, store date code
                    elif dateLine[:6] == "2 PLAC":
                        placeStr = dateLine[7:]
                        placeStr = placeStr.strip("\n")
                        place = {resiDate: placeStr}
                        placeDict[placeCounter] = place
                        placeCounter += 1
                    dateLine = ged.readline()
                    left = True

            if left:
                curLine = dateLine
                left = False
            else:
                curLine = ged.readline()

        # curLine must be '0', create member given variable data from above. Start by cleaning up the current
        # line to read easier.
        curLine.strip()
        individualArray = curLine.split(" ")


        if len(individualArray) > 2:
            if individualArray[2] == "INDI":  # If we're talking individuals, not anything else
                newMember = Member(name, birthDate, deathDate, placeDict)  # Create this member given above info.
                memberArray.append(newMember)  # Add this member to the array.

        # reset member data to avoid carryover
        birthDate = "00000000"
        deathDate = "00000000"
        name = "JOHN DOE"
        placeCounter = 0
        placeDict = {}
        resiDate = "00000000"

        # Increment curLine to next individual
        curLine = ged.readline()

    ged.close()

    return memberArray

def createHTML(memberArray):
    #testPlace = memberArray[1].getPlaces()

    print("Creating your HTML heat map, please be patient...")

    lats = []
    longs = []

    gmap = gmplot.GoogleMapPlotter(37.616063, -76.238841, 5)  # Center the Map on Northeast
    gmap.apikey = "API-KEY-GOES-HERE"  # Hard-code my Google API code for this program

    for member in memberArray:  # Iterate through the members passed
        testPlace = member.getPlaces()

        for placeDict in testPlace.values():  # First layer of dict is key: index | value: date/place Dict
            for date, place in placeDict.items():  # Second layer is key: date | value: location string
                if place is not None:
                    geolocator = Nominatim(user_agent="familyTree")  # Initialize geolocator
                    location = geolocator.geocode(place, timeout=1000)  # Specify timeout to avoid excessive failure
                    if location is not None:
                        print("Grabbing ", location, end=" ")  # Let user know something is happening
                        lat, long = location.latitude, location.longitude  # Take lats and longs
                        print(lat, long)
                        lats.append(lat)
                        longs.append(long)
                    markerStr = str(member) + " Date at this location: " + str(date) + " " + place

                    # Comment this out if you don't want markers
                    #gmap.marker(lat, long, 'cornflowerblue', title=markerStr)

    gmap.heatmap(lats, longs)  # Create heatmap

    gmap.draw("my_map.html")  # Write HTML to file

    print("HTML document completed!")


def chooseMembers(memberArray):

    choice = "s"

    while choice.lower() == "s":

        chosenMems = []  # Initialize

        print("Please fill out the variable prompts. If you don't wish to search for a certain")
        print("criteria, simply leave it blank. You must fill out at least one variable.")

        searchStr = input("First, last, or full name: ")
        searchStr += "|"
        searchStr += input("Four-digit year alive: ")

        name, alive = searchStr.split("|")
        name = name.lower()

        print("Finding members, please be patient...")

        for member in memberArray:  # Iterate through entire member array
            if member.getAlive(alive) and name in member.getName().lower() and name != "":  # Both options given, false all other times
                chosenMems.append(member)
            elif alive == "" and name != "":  # Got just the name
                if name in member.getName().lower():
                    chosenMems.append(member)
            elif alive != "" and name == "":  # Got just the alive year
                if member.getAlive(alive):
                    chosenMems.append(member)

        print("Members selected: ")

        ctr = 1
        for member in chosenMems:
            print(ctr, end=" ")
            print(member)
            ctr += 1

        choice = input("[A]ccept, or [s]earch again? ")

    return chosenMems

def main():

    # Load the GEDCOM file, display successful loading and populating.
    print("Loading GEDCOM file...")
    memberArray = populateMembers()
    print("Loaded", len(memberArray), "members into the family tree.\n")

    # Initialize sentinel variable.
    choice = ""

    #for member in memberArray:
        #print(member)

    # Main program loop
    while choice.lower() != "exit":

        # Gather user input
        print("Type 'Exit' at anytime to exit.")
        choice = input("Would you like to [s]elect members, or the [e]ntire tree? ")

        # Choose to select members or select a full family
        if choice.lower() == 's':
            chosenMems = chooseMembers(memberArray)
            createHTML(chosenMems)
        elif choice.lower() == 'e':
            chosenMems = memberArray
            createHTML(chosenMems)
        else:
            print("Please input either 's' or 'f'.")

main()
