# Populates Hallmark database
import cs50
import re
from sys import argv, exit



def main():
    """Import the contents of a correctly formatted .txt file into hallmark.db."""
    # Check for correct usage
    if len(argv) == 2:
        srcDataFile = "/home/ubuntu/project/sourceData/" + argv[1]
    else:
        print("Usage: python import.py filename.txt")
        exit()

    # Set the database
    db = cs50.SQL("sqlite:///hallmark.db")

    # Open the source data, stick it into a reader and turn it into a nice list
    with open(srcDataFile, "r") as reader:
        try:
            # Get rid of the newline characters, then send it to the database
            fileList = [line.rstrip("\n") for line in reader]
            ImportToDatabase(db, fileList)
        finally:
            reader.close()



def ImportToDatabase(db, fileList):
    """Select and call the correct import function, based on the contents of the first row of the .txt file."""
    # The first row of each input file always contains "#name" where the name is the name of (one of) the tables where the data should go
    if fileList[0][0] == "#":

        # Get the name, store it away nicely, then get rid of it from the data
        myTable = fileList[0].replace("#", "").replace("\n", "")
        contentsArr = fileList[1:]

        # Run the appropriate function to process the file and dunk it into the table(s)
        if myTable == "infinitives":
            ImportNames(db, myTable, contentsArr)

        elif myTable == "pronounGroupMembers":
            ImportPronounGroups(db, contentsArr)

        elif myTable == "words":
            ImportWords(db, contentsArr)

        elif myTable == "pronounSets":
            ImportPronounSets(db, contentsArr)

        elif myTable == "verbs":
            ImportVerbs(db, contentsArr)

        elif myTable == "characterSettings":
            ImportCharacterSettings(db, contentsArr)

        elif myTable == "probabilities":
            ImportProbabilities(db, contentsArr)

        elif myTable == "images":
            ImportImages(db, contentsArr)
        
        elif myTable == "wordsToImages":
            ImportWordsToImages(db, contentsArr)
            
        elif myTable == "titleTemplates":
            ImportTitleTemplates(db, contentsArr)



def ImportNames(db, myTable, fileContents):
    """Import .txt file into a table with two columns, "id" and "name".
    
    Source file requirements:
        Newline-separated names.
    """
    # Verify the table name, then prepare the SQL queries
    safeTableName = GetSafeTableName(myTable)
    countStr = "SELECT COUNT(id) FROM " + safeTableName + " WHERE name = ?"
    insertStr = "INSERT INTO " + safeTableName + "(name) VALUES (?)"

    for e in range(len(fileContents)):
        # Check if the task has changed; if so, switch task
        if "#" == fileContents[e][0]:
            PrintDone("names for " + safeTableName)
            ImportToDatabase(db, fileContents[e:])
            return
        
        # If not, check if the name already exists; if not, add it now
        elif 0 == db.execute(countStr, fileContents[e])[0]["COUNT(id)"]:
            db.execute(insertStr, fileContents[e])
            PrintAdded(e, safeTableName)

    PrintDone("names for " + safeTableName)



def ImportPronounGroups(db, fileContents):
    """Import pronoun groups and their definitions from a .txt file.
    
    Source file requirements:
        File contains pairs of lines.
        First line in each pair contains "~" followed by a pronounGroup name.
        Second line in each pair contains a tab, followed by "p=", followed by a CSV list of pronouns within the group.
        
    Notes:
        "pronounGroups" are used in verb conjugations. She, he and it are interchangeable for conjugation purposes: this gathers them under a single banner.
    """
    for e in range(len(fileContents)):
        # If the task has changed, run the next task
        if "#" == fileContents[e][0]:
            PrintDone("pronoun group names and definitions")
            ImportToDatabase(db, fileContents[e:])
            return

        # The line contains "~groupName". Update the groupID accordingly and, if necessary, add this new group to the list.
        elif fileContents[e][0] == "~":
            activeGroupName = fileContents[e].replace("~", "")
            activeGroupID = GetIdFromName(db, "pronounGroups", activeGroupName, True)

        # The line contains a list of pronouns for the current group in the format "\tp=pronoun1,pronoun2,..."
        elif fileContents[e][0] == "\t":
            pronounList = re.split('p=|,', fileContents[e])

            # pronounList[0] will contain the leading tab, so ignore that
            for p in pronounList[1:]:
                pronounID = 0

                # Go to the words table and find the ID for this pronoun
                try:
                    pronounID = GetWordsID(db, p)
                except:
                    exit()

                # Check if this pronoun-to-group link already exists. If not, add it.
                if 0 == db.execute("SELECT COUNT(id) FROM pronounGroupMembers WHERE group_id = :groupID AND pronoun_id = :pronounID",
                                    groupID = activeGroupID, pronounID = pronounID)[0]["COUNT(id)"]:
                    db.execute("INSERT INTO pronounGroupMembers(group_id, pronoun_id) VALUES (:groupID, :pronounID)", groupID = activeGroupID, pronounID = pronounID)
                    PrintAdded(p + "' to '" + activeGroupName + "' group", "pronounGroupMembers")


    PrintDone("pronoun group names and definitions")



def ImportWords(db, fileContents):
    """Import display words from a config file.
    
    Source file requirements:
        Specify the category; then specify a list of words in that category.
        New line separated. One line = one category or one words record.
        More than one category can appear in the same file.
        Lines beginning with "~" are categories; lines without are words records.
    """
    # Check if the words and category combo already exists in the words table. If not, add it.
    for w in range(len(fileContents)):
        if "#" == fileContents[w][0]:
            ImportToDatabase(db, fileContents[w:])
            return

        elif "~" == fileContents[w][0]:
            # Get the category name and ID
            categoryName = fileContents[w].replace("~", "")
            categoryID = GetIdFromName(db, "categories", categoryName, True)

        elif 0 == db.execute("SELECT COUNT(id) FROM words WHERE categories_id = :catID AND display = :newWord",
                            catID = categoryID, newWord = fileContents[w])[0]["COUNT(id)"]:
            db.execute("INSERT INTO words(categories_id, display) VALUES (:catID, :newWord)", 
                            catID = categoryID, newWord = fileContents[w])
            PrintAdded(fileContents[w] + "' in category '" + categoryName, "words")



def ImportPronounSets(db, fileContents):
    """Import pronoun sets from a config file.
    
    Source file requirements:
        Each line should have two comma-separated words. Subject pronoun on the left; object pronoun on the right. e.g. she,her
    """
    for l in range(len(fileContents)):
        # If the task has changed, run the next task
        if "#" == fileContents[l][0]:
            PrintDone("pronoun sets")
            ImportToDatabase(db, fileContents[l:])
            return        
        
        else:
            mySplit = fileContents[l].split(",")
    
            # Get IDs in the words table for the subject and object pronouns
            subjID = 0
            objID = 0
            try:
                # Get the IDs (and, if the pronoun doesn't exist, add it)
                subjID = GetWordsID(db, mySplit[0], catName="pronoun")
                objID = GetWordsID(db, mySplit[1], catName="pronoun")
            except Exception:
                pass
    
            # Check if the link between subject and object already exists. If not, add it now.
            if 0 == db.execute("SELECT COUNT(id) FROM pronounSets WHERE subjectPronoun_id = :subjID AND objectPronoun_id = :objID",
                                subjID = subjID, objID = objID)[0]["COUNT(id)"]:
                db.execute("INSERT INTO pronounSets(subjectPronoun_id, objectPronoun_id) VALUES (:subjID, :objID)", 
                                subjID = subjID, objID = objID)
                PrintAdded(mySplit[0] + "' + '" + mySplit[1], "pronounSets")
    
    PrintDone("pronoun sets")



def ImportVerbs(db, fileContents):
    """Import verb settings from a config file.
    
    Source file requirements:
        Lines parsed in sets.
        The first line in each set begins with "~" followed by an infinitive.
        Then one line for each pronounGroup. 
        Each begins with a tab, then the pronounGroup name, then "=", then the conjugated verb.
        e.g.
        ~to work
            she/he/it=works
            they=work
    """
    for v in range(len(fileContents)):
        # If the task has changed, run the next task
        if "#" == fileContents[v][0]:
            PrintDone("verb conjugation links")
            ImportToDatabase(db, fileContents[v:])
            return 
        
        # This row contains an infinitive, e.g. "~to work". This will apply to all upcoming rows (until the next infinitive).
        elif fileContents[v][0] == "~":
            infName = fileContents[v].replace("~", "")

            # Get the infinitive ID but only if it already exists (this is not where we add new infinitives)
            try:
                infID = GetIdFromName(db, "infinitives", infName, False)
            except:
                exit()

        # This row contains a pronounGroup/result pair, e.g. "she/he/it=works"
        else:
            pairSplit = fileContents[v].replace("\t", "").split("=")

            # Get the pronounGroup ID
            pronounGrpID = 0
            try:
                pronounGrpID = int(db.execute("SELECT id FROM pronounGroups WHERE name = ?", 
                                                pairSplit[0])[0]["id"])
            except:
                exit()

            # Get the words ID for the resulting conjugated verb (if it doesn't exist, add it)
            resultID = 0
            try:
                resultID = GetWordsID(db, pairSplit[1], catName="verb")
            except:
                exit()

            # Check if a record linking this infinitive, pronounGroup and verb word already exists. If not, add it now
            if 0 == db.execute("SELECT COUNT(id) FROM verbs WHERE infinitives_id = :infID AND pronounGroups_id = :pronounGrpID AND result_id = :resultID",
                                infID = infID, pronounGrpID = pronounGrpID, resultID = resultID)[0]["COUNT(id)"]:
                db.execute("INSERT INTO verbs(infinitives_id, result_id, pronounGroups_id) VALUES (:infID, :resultID, :pronounGrpID)",
                                infID = infID, pronounGrpID = pronounGrpID, resultID = resultID)
                PrintAdded(infName + "' + '" + pairSplit[0] + "' + '" + pairSplit[1], "verbs")

    PrintDone("verb conjugation links")



def ImportCharacterSettings(db, fileContents):
    """Import 'character settings' (i.e. acceptable values for subject pronoun and hometown for a given character words ID).
    
    Source file requirements:
        Lines parsed in sets of two.
        The first line in each set contains the display words for the character and nothing else.
        The second line in each set begins with a tab, then contains tab-separated lists of comma-separated options.
        e.g.
        woman
	        p=she	h=small town,village,farm
    """
    characterID = 0
    for line in range(len(fileContents)):
        # If the task has changed, run the next task
        if "#" == fileContents[line][0]:
            PrintDone("character settings")
            ImportToDatabase(db, fileContents[line:])
            return 
        
        # This means it's the row with the character word on it (no prefix this time), so get the ID.
        elif fileContents[line][0] != "\t":
            characterID = 0
            try:
                characterID = GetWordsID(db, fileContents[line])
            except:
                print("Import the character words and category into the words table first.")
                exit()

        # This means it's the row with all the settings on it
        # e.g. "\tp=pronoun1,pronoun2,...\th=hometown1,hometown2,..."
        else:
            # Break it up by \t so each array element contains one type of settings
            tabSplit = fileContents[line].split("\t")

            for t in tabSplit[1:]:
                # Split apart the header and the list of valid options
                headSplit = t.split("=")
                varList = headSplit[1].split(",")

                # Send the list of valid options to the appropriate table
                for var in varList:
                    if headSplit[0] == "p":
                        AddCharacterPronoun(db, characterID, var)

                    elif headSplit[0] == "h":
                        AddCharacterHometown(db, characterID, var)

    PrintDone("character settings")



def AddCharacterPronoun(db, characterID, subj):
    """Create a record in the "charactersToPronouns" table linking one character words ID to one pronoun words ID."""
    subjID = 0
    try:
        subjID = GetWordsID(db, subj)
    except:
        exit()

    # Check if it already exists and, if not, add it to the charactersToPronouns tables
    if 0 == db.execute("SELECT COUNT(id) FROM charactersToPronouns WHERE subjectPronoun_id = :subjID AND character_id = :characterID",
                        subjID = subjID, characterID = characterID)[0]["COUNT(id)"]:
        db.execute("INSERT INTO charactersToPronouns(subjectPronoun_id, character_id) VALUES (:subjID, :characterID)",
                        subjID = subjID, characterID = characterID)



def AddCharacterHometown(db, characterID, hometown):
    """Add a hometown to the words table and create a record in the "charactersToHometowns" table linking it to the character words ID."""
    hometownID = 0
    try:
        # Get the hometown ID; if it doesn't alreay exist, add it as a "location"
        hometownID = GetWordsID(db, hometown, catName="location")

    except:
        exit()

    # Check if the link already exists and, if not, add it to the charactersToHometowns table
    if 0 == db.execute("SELECT COUNT(id) FROM charactersToHometowns WHERE location_id = :hometownID AND character_id = :characterID",
                        hometownID = hometownID, characterID = characterID)[0]["COUNT(id)"]:
        db.execute("INSERT INTO charactersToHometowns(location_id, character_id) VALUES (:hometownID, :characterID)",
                        hometownID = hometownID, characterID = characterID)



def ImportProbabilities(db, fileContents):
    """Import data to "probabilities" table from a .txt file.
    
    Source file requirements:
        Lines parsed in sets.
        The first line in each set begins with "~" followed by the name of a "choice group".
        Subsequent lines are one line per record in the probabilities table sharing this choice group. Each of these:
            Begins with a tab, then tab-separated settings.
            First setting is always a percentage, expressed as a decimal between 0 and 1.
            Afterwards it's flexible. There are four possible types of settings, flagged as n, w, c and p.
                n -- add a note to this probabilities record
                w -- stores an ID from the words table. If selected, those words will be displayed.
                c -- stores an ID from the categories table. If selected, a words record with that category will be randomly selected.
                p -- stores a string describing a prefix to go in front of a character selected by either the words ID or category ID.

        e.g.
        ~mainChar
	        0.85	w=woman
        	0.05	w=demon
	        0.10	n=has pronoun, has hometown, is humanoid|animal|inanimate
	        
    Note: duplicate choiceGroup names are not allowed. If the choiceGroup name already exists, the program will skip that portion of the import.
    """
    # Set flag (used to avoid duplicating records)
    importIsActive = False
    
    for line in range(len(fileContents)):
        # If the task has changed, run the next task
        if "#" == fileContents[line][0]:
            PrintDone("probabilities")
            ImportToDatabase(db, fileContents[line:])
            return 
        
        # This row contains the name of a choice group, which applies to all rows below until the next row containing "~choiceGroup name"
        elif "~" == fileContents[line][0]:
            choiceGroupName = fileContents[line].replace("~", "")

            # If this group name already exists, skip it; otherwise, prepare for the upload by setting the choiceGroup ID
            if 0 == db.execute("SELECT COUNT(id) FROM choiceGroups WHERE name = ?", choiceGroupName)[0]["COUNT(id)"]:
                importIsActive = True
                choiceGroupID = GetIdFromName(db, "choiceGroups", choiceGroupName, True)
            else:
                importIsActive = False
            
        # This row contains tab-separated info for a single probabilities record
        elif importIsActive and "\t" == fileContents[line][0]:
            choiceGroupName = fileContents[line].replace("~", "")
            recordSettings = fileContents[line].split("\t")

            # [0] will always be empty; [1] should always be a probability, so convert to a float and store it
            myProbability = float(recordSettings[1])

            # Insert the non-optional bits into the database and get the ID of that record
            db.execute("INSERT INTO probabilities(choiceGroups_id, probability) VALUES (?, ?)",
                        choiceGroupID, myProbability)
            thisRecordID = int(db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"])

            # Loop through the optional bits, undating the record as we go
            for thisTab in recordSettings[2:]:
                mySplit = thisTab.split("=")

                if mySplit[0] == "n":
                    db.execute("UPDATE probabilities SET note = ? WHERE id = ?",
                                mySplit[1], thisRecordID)

                elif mySplit[0] == "w":
                    db.execute("UPDATE probabilities SET words_id = ? WHERE id = ?",
                                GetWordsID(db, mySplit[1]), thisRecordID)

                elif mySplit[0] == "c":
                    db.execute("UPDATE probabilities SET categories_id = ? WHERE id = ?",
                                GetIdFromName(db, "categories", mySplit[1], False), thisRecordID)

                elif mySplit[0] == "p":
                    db.execute("UPDATE probabilities SET prefixStr = ? WHERE id = ?",
                                mySplit[1], thisRecordID)


    PrintDone("probabilities")



def ImportImages(db, fileContents):
    """Import links between words and images.
    
    Source file requirements:
    Each row contains three comma-separated values: first is an name for the image record in the table; second is the filename; third is the file extension.
    """
    for line in range(len(fileContents)):
        # If the task has changed, run the next task
        if "#" == fileContents[line][0]:
            PrintDone("images import")
            ImportToDatabase(db, fileContents[line:])
            return 
        
        # Split the line and check it has the correct number of variables
        splitLine = fileContents[line].split(",")
        if len(splitLine) != 3:
            exit()

        try:
            # Check if the record with this name already exists. If not, add it now
            if 0 == db.execute("SELECT COUNT(id) FROM images WHERE name = ?",
                                splitLine[0])[0]["COUNT(id)"]:
                db.execute("INSERT INTO images(name, filename, fextension) VALUES (?, ?, ?)",
                            splitLine[0], splitLine[1], splitLine[2])
                PrintAdded(splitLine[0], "images")
        except:
            exit()

    PrintDone("images import")



def ImportWordsToImages(db, fileContents):
    """Import links between words and images.
    
    Source file requirements:
    Each line contains two comma-separated values: left is the display text of a words record; right is the name of an image in the images table.
    """
    # The source file should have a word,imageName pair on each row.
    for line in range(len(fileContents)):
        print(fileContents[line])
        
        # If the task has changed, run the next task
        if "#" == fileContents[line][0]:
            PrintDone("images import")
            ImportToDatabase(db, fileContents[line:])
            return 
        
        # Otherwise prep for importing some word-to-image links
        splitLine = fileContents[line].split(",")
        
        # Check the line has the right number of elements (a comma could mess things up)
        if len(splitLine) != 2:
            exit()
    
        # Get IDs for the words and the image
        try:
            wordsID = GetWordsID(db, splitLine[0])
            imgID = GetIdFromName(db, "images", splitLine[1], False)
            
            # Check if this combo already exists. If not, add it now.
            if 0 == db.execute("SELECT COUNT(id) FROM wordsToImages WHERE words_id = ? AND images_id = ?",
                                wordsID, imgID)[0]["COUNT(id)"]:
                db.execute("INSERT INTO wordsToImages(words_id, images_id) VALUES (?, ?)", wordsID, imgID)
                PrintAdded(splitLine[0] + "'s pic = '" + splitLine[1] + "'", "wordsToImages")

        except Exception:
            pass



def ImportTitleTemplates(db, fileContents):
    """Import title templates and links between title templates and words.
    
    Source file requirements:
    Each line either:
        has a pair of values separated by "//"
        has a single value followed by "//"
    The first or only value is a potential title, optionally containing "#[topic]#".
    The second value, if there is one, is the display text of a words record which activates the potential title.
    """

    # Loop through the file contents importing the data
    for line in range(len(fileContents)):
        # If the task has changed, run the next task
        if "#" == fileContents[line][0]:
            PrintDone("titles import")
            ImportToDatabase(db, fileContents[line:])
            return 
        
        # Each line has the format:
        #   Title template//words
        splitLine = fileContents[line].split("//")
        
        # Even templates without any particular link to words should end in //, so print an error if there aren't 2 array elements
        if len(splitLine) != 2:
            exit()
        
        # Add this row's title template to titleTemplates if it doesn't already exist
        if 0 == db.execute("SELECT COUNT(id) FROM titleTemplates WHERE titleTemplate = ?", splitLine[0])[0]["COUNT(id)"]:
            db.execute("INSERT INTO titleTemplates(titleTemplate) VALUES(?)", splitLine[0])
            PrintAdded(splitLine[0], "titleTemplates")
        
        # If there's a link to a particular words record, check if it already exists and, if not, create the link
        if splitLine[1] != "":
            queryStr = "SELECT COUNT(wtt.id) FROM wordsToTitles wtt"
            queryStr += " JOIN words w ON w.id = wtt.words_id"
            queryStr += " JOIN titleTemplates tt ON tt.id = wtt.titleTemplates_id"
            queryStr += " WHERE tt.titleTemplate = ? AND w.display  = ?"
            
            if 0 == db.execute(queryStr, splitLine[0], splitLine[1])[0]["COUNT(wtt.id)"]:
                try:
                    wordsID = GetWordsID(db, splitLine[1])
                    titleTemplateID = db.execute("SELECT id FROM titleTemplates WHERE titleTemplate = ?",
                                                splitLine[0])[0]["id"]
                    db.execute("INSERT INTO wordsToTitles(words_id, titleTemplates_id) VALUES (?, ?)",
                                wordsID, titleTemplateID)
                    PrintAdded("link between " + splitLine[0] + " and " + splitLine[1], "wordsToTitles")
                except Exception:
                    pass

    PrintDone("titles import")



def GetIdFromName(db, tableCode, targetName, wantToAddNew):
    """Return an ID in one of the hallmark.db tables, based on the 'name'.
    
    Keyword arguments:
    db -- a connection to the Hallmark database.
    tableCode -- the table containing the required record. Called "a code" because it won't be used directly.
    targetName -- the contents of the name field in the required record.
    wantToAddNew -- boolean. If this name does not exist in the specified table: True = add it; False = exit.
    """
    # To protect against SQL injections, we're not going to use the table name given by the user, we're going to use one from a vetted list.
    safeTableName = GetSafeTableName(tableCode)

    # If the user indicated they want to add a new record if this name isn't found, 
    if wantToAddNew:
        countStr = "SELECT COUNT(id) FROM " + safeTableName + " WHERE name = ?"
        insertStr = "INSERT INTO " + safeTableName + "(name) VALUES (?)"

        if 0 == db.execute(countStr, targetName)[0]["COUNT(id)"]:
            db.execute(insertStr, targetName)
            PrintAdded(targetName, safeTableName)

    # Get the ID
    selectStr = "SELECT id FROM " + safeTableName + " WHERE name = ?"
    try:
        return int(db.execute(selectStr, targetName)[0]["id"])
    except:
        exit()



def GetSafeTableName(inputTableName):
    """Check the inputTableName against a list of valid Hallmark table names and return it if it's on the list."""
    validTableNames = ["categories", "charactersToHometowns", "charactersToPronouns", "choiceGroups", "infinitives", "probabilities",
                        "pronounGroupMembers", "pronounGroups", "pronounSets", "verbs", "words", "wordsToImages", "images",
                        "titleTemplates", "wordsToTitles"]

    if inputTableName in validTableNames:
        return inputTableName

    exit()



def GetWordsID(db, theWords, **kwargs):
    """Return the words ID associated with 'theWords'; optionally add 'theWords' if they don't exist."""
    try:
        # If the user indicated they want to add a new record if this name isn't found 
        if "catName" in kwargs:
            categoryID = GetIdFromName(db, "categories", kwargs.get("catName"), True)
    
            if 0 == db.execute("SELECT COUNT(id) FROM words WHERE display = ?", theWords)[0]["COUNT(id)"]:
                db.execute("INSERT INTO words(display, categories_id) VALUES (?,?)", theWords, categoryID)

        # Now return it
        return int(db.execute("SELECT id FROM words WHERE display = ?", theWords)[0]["id"])
    except:
        exit()



def PrintDone(whatIsDone):
    """Print a message to say processing is complete."""
    print("Finished processing " + str(whatIsDone) + ".")



def PrintAdded(whatWasAdded, toTable):
    """Print a message to say something has been added to a particular table."""
    print("Added '" + str(whatWasAdded) + "' to " + str(toTable) + " table.")



main()


