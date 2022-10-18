# Generates an alternative plot for a Hallmark movie
import cs50
import re
from sys import exit
import random
from collections import deque
import math
from cs50 import SQL


# Declare some globals
OPEN_TAG = "#["
CLOSE_TAG = "]#"
VOWELS = "aeiou"



def GetHallmarkSettings(defaultWanted):
    """Output a sentence resembling the plot of a Hallmark movie.
    
    Keyword arguments:
    defaultWanted -- boolean. True = return plot, image and title for the normal Hallmark plot; False = return modified plot, images and titles
    """
    # Configure CS50 Library to use SQLite database
    db = SQL("sqlite:///hallmark.db")
    
    # Begin with the actual plot of all Hallmark movies, with #[...]# tags around the changeable parts.
    basePlot = "#[]#an attractive young <strong>#[woman]#</strong> #[works]# hard in <strong>#[a well-paid and professional]#</strong> job in the big city, "
    basePlot += "until circumstances require #[her]# to return to the <strong>#[small town]#</strong> where #[she]# grew up. There #[she]# "
    basePlot += "#[meets]# <strong>#[an attractive young man]#</strong> who teaches #[her]# the true meaning of <strong>#[Christmas]#</strong>."

    # If the default was requested, we want the base plot (only without the tags) and a mostly empty varDict
    if defaultWanted:
        varDict = {}
        varDict["dictName"] = "original"
        myPlot = basePlot.replace(OPEN_TAG, "").replace(CLOSE_TAG, "")

    # Otherwise put together a, dare I say, significantly more interesting alternative plot
    else:
        # List with one element for each #[...]# tag, containing the dictionary key that must go inside.
        tagContents = ["bees", "mainChar", "work/s", "jobDesc", "pronounObj", "hometown", "pronounSubj", "pronounSubj", "meet/s", "lifeguide", "pronounObj", "topic"]

        # Split up the base plot, create a dictionary of variables to go inside the tags, then put it all together
        basePlotList = SplitTaggedStr(basePlot)
        varDict = GetVariables(db)
        myPlot = GetNewPlot(basePlotList, tagContents, varDict)

    # Declare a dictionary to hold the results and populate it
    result = {}
    result["plot"] = TidyUpString(myPlot)
    result["images"] = GetValidImages(db, varDict)
    result["titles"] = GetValidTitles(db, varDict)

    return result




def SplitTaggedStr(taggedStr):
    """Split up the base string via the #[...]# tags, so we can edit in some new bits."""
    # re.split uses "[" and "]", so for this to work it's necessary to insert the escape character inside the tags.
    # Just the open tag is sufficient (the "]" in the close tag doesn't cause any problems once the open tag's "[" is escaped. I assume due to it being unpaired)
    escOpenTag = OPEN_TAG[0] + "\\" + OPEN_TAG[1]
    splitStrArr = re.split(escOpenTag + "|" + CLOSE_TAG, taggedStr)
    return splitStrArr




def GetVariables(db):
    """Generate dictionary of variables for the Hallmark plot."""
    # The main character affects some grammar and the hometown, so settle on the main character first
    mainCharID = GetMainCharID(db)
    
    # Check if the "main char is actually a swarm of bees assuming a shape" plot twist is active and assign workingID accordingly
    beeID = ProbabilitiesPick(db, "toBeeOrNotToBee")[0]["words_id"]
    if beeID != None:
        beeStr = GetWords(db, beeID)
    else:
        beeStr = " "

    if beeStr != " ":
        workingID = beeID
    else:
        workingID = mainCharID

    # The subject pronoun is used as an argument for verbs and object pronouns
    # Get that next, so you don't need to worry about the order in which you populate the variables below
    subjectPronoun = GetSubjectPronoun(db, workingID)

    # Create a dictionary containing each unique variable in the sentence, then populate it
    myVars = {}
    myVars["dictName"] = "v2.0"
    myVars["bees"] = beeStr
    myVars["mainChar"] = GetWords(db, mainCharID)
    myVars["hometown"] = GetHometown(db, workingID)
    myVars["pronounObj"] = GetObjectPronoun(db, subjectPronoun)
    myVars["pronounSubj"] = subjectPronoun
    myVars["work/s"] = ConjugateVerb(db, "to work", subjectPronoun)
    myVars["meet/s"] = ConjugateVerb(db, "to meet", subjectPronoun)
    myVars["jobDesc"] = GetJobDesc(db)
    myVars["lifeguide"] = GetLifeguide(db)
    myVars["topic"] = GetTopic(db)

    return myVars




def GetNewPlot(originalAsList, keyForSlot, newWordsDict):
    """Combine the original Hallmark plot (as a list) with the dictionary of replacement words, via a list matching dictionary keys to replacement slots.
    
    Keyword arguments:
    originalAsList -- the "basePlot" as a list of strings, where odd indexes are to be replaced and evens are to be kept.
    keyForSlot -- a list with one element for each "replacement slot", each containing the dictionary key to be inserted.
    newWordsDict -- a dictionary of replacement words for the Hallmark plot.
    """
    if len(keyForSlot) != int((len(originalAsList) - 1) / 2):
        # Check there's a variable assigned to each slot.
        # If there isn't, who knows what mess we have. Return an alternative plot.
        return "ROCKS FALL; EVERYONE DIES. But before they die, they learn the true meaning of love."

    # Loop through the list of possible replacements replacing the words
    else:
        myStr = ""
        for i in range(len(keyForSlot)):

            # Original words list will have something to go in front of the replacement word/s, so add that to the string
            myStr += originalAsList[i * 2]

            # Add the replacement words
            if newWordsDict[keyForSlot[i]] == "":
                # "" means something went wrong. Fail gracefully by using the static text
                myStr += originalAsList[i * 2 + 1]
            else:
                # Replace with the more interesting alternative
                myStr += str(newWordsDict[keyForSlot[i]])

    # There's a fences-and-posts thing going on here, so add on the last "post" from the originalAsList
    myStr += originalAsList[len(originalAsList)-1]

    return myStr




def TidyUpString(myStr):
    """Format the sentence. Get rid of leading and trailing spaces, remove tags, capitalise the first letter of the first word."""
    myStr = myStr.strip()
    myArr = myStr.split(" ")
    myArr[0] = myArr[0].capitalize()

    # Put it back together, including all the spaces we lost
    myStr = " ".join(elem for elem in myArr)

    # Remove any tags that still remain
    myStr = myStr.replace(OPEN_TAG, "").replace(CLOSE_TAG, "")

    return myStr



def GetValidImages(db, varDict):
    """Make a prioritised list of all images which illustrate something in the new Hallmark plot."""
    # Init the queryStr and the "validPics" list, plus setup some default pics to return if this goes horribly wrong
    defaultPics = ["default0.png", "default1.png", "default2.png"]
    validPics = []
    queryStr = "SELECT i.filename, i.fextension FROM images i"

    # If it's the original plot, lookup the details for the original overlay and return that
    if varDict["dictName"] == "original":

        # Append text to look up the image based on the name
        queryStr += " WHERE i.name = ?"

        # Try to get the info from the database. Failing that, return the three hard-coded defaults as a last resort
        try:
            sqldata = db.execute(queryStr, varDict["dictName"])
            validPics.append(sqldata[0]["filename"] + "." + sqldata[0]["fextension"])
        except:
            validPics.extend(defaultPics)

    # Otherwise check all variables that can possibly affect the selected image and make a list of any images that come up
    else:
        # List of slots which can have pics assigned, in priority order
        picSlots = ["bees","mainChar","lifeguide","topic","jobDesc"]

        # Append text to lookup the image based on the words
        queryStr += " JOIN wordsToImages wti ON i.id = wti.images_id"
        queryStr += " JOIN words w ON w.id = wti.words_id"

        # Loop through the list of relevant slots, obtaining any relevant context-sensitive images for each
        try:
            for thisSlot in picSlots:
                # Some lifeguide options contain irrelevant adjectives before the character. To handle those, use INSTR.
                if thisSlot == "lifeguide":
                    loopQueryStr = queryStr + " WHERE INSTR(?, w.display) > 0"
                else:
                    loopQueryStr = queryStr + " WHERE w.display = ?"
                
                # Lookup the image for the words. If there is one, store it in the list
                sqldata = db.execute(loopQueryStr, varDict[thisSlot])
                if len(sqldata) == 1:
                    validPics.append(sqldata[0]["filename"] + "." + sqldata[0]["fextension"])

        except:
            pass

        # Try to add on the latest default pics from the database.
        try:
            sqldata = db.execute("SELECT i.filename, i.fextension FROM images i WHERE i.name LIKE 'default%'")
            for i in range(0, len(sqldata)):
                validPics.append(sqldata[i]["filename"] + "." + sqldata[i]["fextension"])
        
        # Failing that, add on the three hard-coded defaults as a last resort
        except:
            validPics.extend(defaultPics)

    return validPics



def GetValidTitles(db, varDict):
    """Make a shuffled list of titles relating to something in the new Hallmark plot."""
    titleList = []   
    
    # If it's the original movie, return a single title
    if varDict["dictName"] == "original":
        titleList.append("Every Single Hallmark Movie")
    
    # Otherwise return a list of suitable titles
    else:
        # This query gets a list of titles. At the mo', titles are either:
        #   a) for any topic (so there is no words link, they just work for any title); b) for a specific hometown; c) special pun for bees; d) special pun for demons
        queryStr = "SELECT t.titleTemplate FROM titleTemplates t"
        queryStr += " LEFT JOIN wordsToTitles wtc ON wtc.titleTemplates_id = t.id"
        queryStr += " LEFT JOIN words w ON wtc.words_id = w.id"
        queryStr += " WHERE w.display IS NULL OR w.display = :hometown OR w.display = :bees OR INSTR(:lifeguide, w.display) > 0"
        
        # Populate the list
        try:
            # Run the query to get the list of templates
            templates = db.execute(queryStr, hometown=varDict["hometown"], bees=varDict["bees"], lifeguide=varDict["lifeguide"])
    
            # Loop through the templates replacing all instances of the "#[topic]#" placeholder with the actual topic
            for i in range(0, len(templates)):
                titleList.append(templates[i]["titleTemplate"].replace("#[topic]#", varDict["topic"]).title())
    
            # Now shuffle the list in a vague attempt to not always end up with the same titles
            random.shuffle(titleList)
            
        except:
            # If it all goes horribly wrong, here are some default titles that could apply to absolutely anything.
            titleList.append("Every Cloud Has A Silver Lining")
            titleList.append("Learning And Loving")
            titleList.append("Our Meaning Is What We Make")

    return titleList



def GetMainCharID(db):
    """Return a words ID for a randomly selected main character variable."""
    try:
        # Probabilities contains some alternative settings for this slot, with weightings. Select one.
        mySettings = ProbabilitiesPick(db, "mainChar")

        # Some "settings" simply tell you which words record to use. If one of those was chosen, return the words_id
        if mySettings[0]["words_id"] != None:
            return int(mySettings[0]["words_id"])

        # One option has a probability, but all settings are blank. This means "select any valid word".
        else:
            # SQL query to get a list of all words records which:
            #   a) have a pronoun, b) have a hometown, c) are in a category that could conceivably be a character
            queryStr = "SELECT DISTINCT w.id FROM words w"
            queryStr += " INNER JOIN charactersToPronouns ctp ON w.id = ctp.character_id"
            queryStr += " INNER JOIN charactersToHometowns cth ON w.id = cth.character_id"
            queryStr += " JOIN categories c ON w.categories_id = c.id"
            queryStr += " WHERE c.name IN ('humanoid', 'animal', 'inanimate')"

            # Run the query, then return one of the options (equal chance of each)
            sqldata = db.execute(queryStr)
            myPick = EqualPickList(sqldata)["id"]
            if myPick == None:
                return ""
            else:
                return int(myPick)

    # If it all goes wrong, return "" so the program will use the default text instead
    except:
        return ""



def GetSubjectPronoun(db, wid):
    """Return display text for a subject pronoun.
    
    Keyword arguments:
    db -- the database connection for Hallmark
    wid -- an ID in the words table for a words record with at least one subject pronoun assignment.
    """
    # SQL query to get a list of pronouns tagged as valid for this character type
    queryStr = "SELECT w.display FROM words w"
    queryStr += " INNER JOIN charactersToPronouns ctp ON ctp.subjectPronoun_id = w.id"
    queryStr += " WHERE ctp.character_id = ?"

    # Return the/a result of the query
    try:
        results = db.execute(queryStr, wid)
        return EqualPickList(results)["display"]

    # If it all goes wrong, return "" so the program will use the default text instead
    except:
        return ""



def GetHometown(db, myCharID):
    """Return display text for a suitable location of childhood significance for the main character.
    
    Keyword arguments:
    db -- the database connection for Hallmark
    myCharID -- an ID in the words table for a words record with at least one hometown assignment.
    """
    # SQL query to get a list of display words which are flagged as suitable hometowns for this character type
    queryStr = "SELECT w.display FROM words w"
    queryStr += " JOIN charactersToHometowns cth ON w.id = cth.location_id"
    queryStr += " WHERE cth.character_id = ?"

    # Return the/a result of the query (some characters have more than one possible hometown)
    try:
        results = db.execute(queryStr, myCharID)
        return EqualPickList(results)["display"]

    # If it all goes wrong, return "" so the program will use the default text instead
    except:
        return ""
        
        

def GetObjectPronoun(db, subjWords):
    """Return display text for an object pronoun, based on the subject pronoun display text."""
    # SQL query to get the display text for the object pronoun, based on the subject pronoun that was passed in
    queryStr = "SELECT wo.display FROM words wo"
    queryStr += " JOIN pronounSets ps ON ps.objectPronoun_id = wo.id"
    queryStr += " JOIN words ws ON ps.subjectPronoun_id = ws.id"
    queryStr += " WHERE ws.display = ?"

    # Return the result of the query
    try:
        return db.execute(queryStr, subjWords)[0]["display"]

    # If it all goes wrong, return "" so the program will use the default text instead
    except:
        return ""



def ConjugateVerb(db, infinitive, subjectPronoun):
    """Conjugate a verb based on the infinitive and subject."""
    # SQL query to get the display text of the correct verb, based on the infinitive name and subject pronoun display text
    queryStr = "SELECT w.display FROM words w"
    queryStr += " JOIN verbs v ON w.id = v.result_id"
    queryStr += " JOIN infinitives i ON i.id = v.infinitives_id"
    queryStr += " JOIN pronounGroups pg ON pg.id = v.pronounGroups_id"
    queryStr += " JOIN pronounGroupMembers pgm ON pgm.group_id = pg.id"
    queryStr += " JOIN words wp ON wp.id = pgm.pronoun_id"
    queryStr += " WHERE i.name = ? AND wp.display = ?"

    # Run that and return it
    try:
        return db.execute(queryStr, infinitive, subjectPronoun)[0]["display"]

    # If it all goes wrong, return "" so the program will use the default text instead
    except:
        return ""



def GetJobDesc(db):
    """Return display text describing the main character's job in the big city."""
    # Grab some probabilities settings. All jobDesc probabilities settings have a words_id, so return that
    try:
        mySettings = ProbabilitiesPick(db, "jobDesc")
        
        if mySettings[0]["words_id"] != None:
            myDesc = GetWords(db, int(mySettings[0]["words_id"]))
            return GetAOrAn(myDesc) + " " + myDesc

        # If probabilities pick went wrong, return "" so the program will use the default text instead
        else:
            return ""

    # If something else goes wrong, return "" so the program will use the default text instead
    except:
        return ""



def GetAOrAn(nextStr):
    """Return "a" or "an", depending on the next word in the sentence.
    
    Note: this is very simple, it doesn't work for numbers, acronyms or initialisations).
    """
    if BeginsWithVowel(nextStr):
        return "an"
    else:
        return "a"




def BeginsWithVowel(myStr):
    """Return boolean indicating if "myStr" begins with a vowel."""
    try:
        # Get rid of variable tags and/or spaces so the first character is the first letter
        myStr = myStr.replace(OPEN_TAG, "").replace(CLOSE_TAG, "").strip()
    
        if not myStr[0].isalpha():
            return False
        else:
            return myStr[0].lower() in VOWELS
    
    # If something goes wrong, grammatically incorrect is preferable to something crashing
    except:
        return False



def GetLifeguide(db):
    """Return display text describing the 'lifeguide'"""
    # Select a row of settings from probabilities. For lifeguide they should all have a category ID; most will also have a prefix string
    mySettings = ProbabilitiesPick(db, "lifeguide")

    # Get display text for the prefixStr, if there is one
    myPrefix = HandlePrefix(db, mySettings[0]["prefixStr"])

    # SQL query to get a list of words with a particular catgeories_id
    queryStr = "SELECT w.display FROM words w"
    queryStr += " WHERE w.categories_id = ?"

    # Run it with the categories_id from probabilities passed in as the argument.
    try:
        if mySettings[0]["categories_id"] != None:
            guideOptions = db.execute(queryStr, mySettings[0]["categories_id"])
    
            # Append the prefix
            lifeguide = myPrefix + " " + EqualPickList(guideOptions)["display"]
            
            # Return a or an, followed by the lifeguide text
            return GetAOrAn(lifeguide) + " " + lifeguide
        
        # If ProbabilitiesPick failed, return "" so the program will use the default text instead
        else:
            return ""
    
    # If it all goes wrong, return "" so the program will use the default text instead
    except:
        return ""



def HandlePrefix(db, myPrefix):
    """Return display text for a prefix embellishing the lifeguide.
    
    Keyword arguments:
    db -- connection to the Hallmark database.
    myPrefix -- a settings string.
    
    Settings string example:
    prefixStr = #[adjective]# talking
    "adjective" is surrounded by #[ ]# tags, indicating it's a category name.
    " talking" is not, indicating it's a static string.
    HandlePrefix will lookup all words in the adjective category, randomly select one, then use it to replace "#[adjective]#", leaving " talking" alone.
    """
    # It's possible for the prefix to be empty, so check for that
    if myPrefix == None or myPrefix == "":
        return ""

    # If there is a prefix, split it up and replace the variables with something suitable
    else:

        # SQL query to get a list of words with a particular category name
        queryStr = "SELECT w.display FROM words w"
        queryStr += " JOIN categories c ON c.id = w.categories_id"
        queryStr += " WHERE c.name = ?"
    
        # Split up the prefix based on the variable tags
        prefixArr = SplitTaggedStr(myPrefix)
    
        # Generate the string
        myStr = ""
        for i in range(0, len(prefixArr)):
    
            # Evens = static text, so just dunk it into the string
            if i % 2 == 0:
                myStr += prefixArr[i]
    
            # Odds = the category name for the variable we want. Run the SQL query we prepared earlier, then pick a result
            else:
                try:
                    sqldata = db.execute(queryStr, prefixArr[i])
                    myStr += EqualPickList(sqldata)["display"]
                
                # "Adjective" is the most common prefix category and if you describe the Lifeguide as a "happy happy man" it'd sort of make sense, so...
                except:
                    myStr += "happy"
    
        return myStr



def GetTopic(db):
    """Return display words for a topic of conversation."""
    # Prepare SQL query to make a list of all words records in the "topic" category
    queryStr = "SELECT w.display FROM words w"
    queryStr += " JOIN categories c ON c.id = w.categories_id"
    queryStr += " WHERE c.name = 'topic'"

    # Run the query, then pick an option
    try:
        topicOptions = db.execute(queryStr)
        return EqualPickList(topicOptions)["display"]

    # If it all goes wrong, return "" so the program will use the default text instead
    except:
        return ""



def EqualPickList(myList):
    """Return a random element from a list."""
    # If the list only has one variable, return that
    if len(myList) == 1:
        return myList[0]

    # If it has more than one, pick one at random
    elif len(myList) > 1:
        return myList[random.randint(0, len(myList)-1)]

    # If it all goes horribly wrong, return a dummy dictionary of blankness
    else:
        fail = {}
        fail["display"] = None
        fail["id"] = None
        return fail



def ProbabilitiesPick(db, choiceGroupName):
    """Return the results fields from a weighted randomly select a record from the probabilities table.
    
    Keyword arguments:
    db -- connection to the Hallmark database
    choiceGroupName -- the name identifying the group of probabilities records to choose between
    """
    try:
        sqlData = db.execute("SELECT p.id, p.probability FROM probabilities p INNER JOIN choiceGroups cg ON cg.id = p.choiceGroups_id WHERE cg.name = ?", choiceGroupName)
        chosenID = WeightedPick(sqlData)
        return db.execute("SELECT words_id, categories_id, prefixStr FROM probabilities WHERE id = ?", chosenID)

    # If something goes wrong, return a dummy dictionary of blankness
    except:
        fail = {}
        fail["words_id"] = None
        fail["categories_id"] = None
        fail["prefixStr_id"] = None
        return fail   



def GetWords(db, wid):
    """Return the display words for a given words ID."""
    try:
        return db.execute("SELECT display FROM words WHERE id = ?", wid)[0]["display"]
    except:
        return "- KABOOM! -"



def WeightedPick(idsAndWeights):
    """Select an ID randomly, but with weightings applied.

    Keyword arguments:
    idsAndWeights -- a list of dictionaries with two fields, "id" and "probability"
    """
    # If this is somehow run with only one option, return it.
    if len(idsAndWeights) == 1:
        return idsAndWeights[0]["id"]

    # Otherwise apply alias algorithm to perform a weighted selection
    else:
        # The probabilities should already be percentages, but make sure.
        idsAndWeights = ConvertToPercentages(idsAndWeights)
        
        # Create a biased coin and flip it
        myCoin = CreateUnfairCoin(idsAndWeights)
        thisSideUp = UnfairCoinFlip(myCoin["probOfHeads"])
        return myCoin["sides"][thisSideUp]



def CreateUnfairCoin(idsAndWeights):
    """Return a dictionary with two values, representing an unfair coin:
        "probOfHeads" (a float between 0 and 1)
        "sides" (a two-element list where [0] contains the result of heads and [1] the result of tails)
    
    Keyword arguments:
    idsAndWeights -- a list of dictionaries with two fields, "id" and "probability"
    
    Note: implementation of the alias algorithm, as explained at https://www.keithschwarz.com/darts-dice-coins/.
    """
    myCoin = {}

    # If there are only two options, set up the biased coin immediately.
    if len(idsAndWeights) == 2:
        myCoin["probOfHeads"] = idsAndWeights[0]["probability"]
        myCoin["sides"] = [idsAndWeights[0]["id"], idsAndWeights[1]["id"]]

    # If there are more than 2 options, decide which two options are going into the biased coin, then set it up.
    else:
        # Setup arrays to store the probabilities and aliases
        sizeOfSrc = len(idsAndWeights)
        aliasIds = [None] * sizeOfSrc
        prob = [None] * sizeOfSrc

        # Use deque for the worklists, to improve performance when popping values from the start
        smallWork = deque([])
        largeWork = deque([])

        # Populate the two working lists
        for pos in range(0, sizeOfSrc):
            # Scale the probabilities so the average probability = 1
            idsAndWeights[pos]["probability"] = idsAndWeights[pos]["probability"] * sizeOfSrc

            # Assign elements to large or small depending on if their probability is above or below average
            if idsAndWeights[pos]["probability"] >= 1:
                largeWork.append(pos)
            else:
                smallWork.append(pos)

        # While both working lists have values, loop through using the next largeWork option to fill up the space above the next smallWork option
        while len(largeWork) > 0 and len(smallWork) > 0:
            tPos = smallWork.popleft()
            aPos = largeWork.popleft()

            # Add these to the results lists
            prob[tPos] = idsAndWeights[tPos]["probability"]
            aliasIds[tPos] = idsAndWeights[aPos]["id"]

            # Filling the gap above tPos "used up" some of aPos's probability. Adjust, then reassign the remainder of aPos to a work list
            idsAndWeights[aPos]["probability"] = (idsAndWeights[aPos]["probability"] + idsAndWeights[tPos]["probability"]) - 1

            if idsAndWeights[aPos]["probability"] < 1:
                smallWork.append(aPos)
            else:
                largeWork.append(aPos)

        # In theory smallWork should always empty first, leaving some "larges" that don't need an alias because they have a value of 1.
        while len(largeWork) > 0:
            lPos = largeWork.popleft()
            prob[lPos] = 1

        # In practice numerical instability can result in some "larges" being assigned to smallWork by accident. Handle those too.
        while len(smallWork) > 0:
            sPos = smallWork.popleft()
            prob[sPos] = 1

        # Perform a fair "dice roll" to determine which pair/probabilities we're going to use to setup our biased coin
        diceResult = random.randint(0, sizeOfSrc-1)

        # Setup the biased coin based on the dice roll's selection
        myCoin["probOfHeads"] = prob[diceResult]
        myCoin["sides"] = [idsAndWeights[diceResult]["id"], aliasIds[diceResult]]
    
    return myCoin



def UnfairCoinFlip(probOfHeads):
    """Return 0 ("heads") or 1 ("tails") with the probability of heads being as per the argument."""

    # Pick a float between 0 and 1
    randProb = random.random()

    # Check if that beats the unfair odds of heads
    if randProb < probOfHeads:
        return 0
    else:
        return 1



def ConvertToPercentages(idsAndWeights):
    """Return a list of dictionaries where the probability values sum up to 1."""
    # See if it already sums to 1 (maybe they're already percentages)
    startTotal = sum(item["probability"] for item in idsAndWeights)

    # If it doesn't, adjust the values so it does
    if 1 != startTotal:
        # Adjust the values proportionately
        for r in idsAndWeights:
            r["probability"] = r["probability"] / startTotal

        # Round down the proportionate probabilities in idsAndWeights to 2 dp, storing the remainders
        remainders = []
        for r in range(len(idsAndWeights)):
            thisCombo = {}
            prob2dp = math.floor(idsAndWeights[r]["probability"] * 100) / 100.0
            thisCombo["pos"] = r
            thisCombo["remainder"] = idsAndWeights[r]["probability"] - prob2dp
            idsAndWeights[r]["probability"] = prob2dp
            remainders.append(thisCombo)
        
        # Calculate how much was lost via rounding down
        difference = 1 - sum(item["probability"] for item in idsAndWeights)

        # Sort the remainders in descending size order
        remainders.sort(key=GetRemainder, reverse=True)

        # While the difference exists, add 0.01 to the next highest remainder
        loopNum = 0
        while difference > 0:
            idsAndWeights[remainders[loopNum]["pos"]]["probability"] += 0.01
            difference -= 0.01
            loopNum += 1

    return idsAndWeights



def GetRemainder(remainder):
    """Return the key value for remainder."""
    return remainder.get("remainder")
