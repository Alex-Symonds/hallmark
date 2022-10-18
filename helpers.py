# Takes multiple Hallmark settings as an argument, then returns one plot, image and title for each, trying to avoid the same title or image being used twice.
from flask import Markup, render_template



def GetHallmarkSelection(mySettings):
    """Return a list of three dictionaries, each containing a unique 'plot' and, ideally, a unique 'image' and 'title'."""
    # Prepare lists for storage of results and existing values
    MAX_SLIDES = 3;
    myMovies = []
    existingTitles = []
    existingImages = []

    # Enforce a maximum number of slides
    numSlides = len(mySettings)
    if numSlides > MAX_SLIDES:
        numSlides = MAX_SLIDES

    # Get one movie for each slide
    for i in range(numSlides):

        # Prepare a dictionary for this particular movie and add the markup-enabled plot (so the <strong>s work)
        thisMovie = {}
        thisMovie["plot"] = Markup(mySettings[i]["plot"])

        # Initialise the remaining fields to the first image and title (if something goes wrong, repeated images and titles are better than no images or titles)
        thisMovie["image"]=mySettings[0]["images"]
        thisMovie["title"]=mySettings[0]["titles"]
        
        # Loop through the list of relevant images, picking the first one that hasn't already been used
        for pic in mySettings[i]["images"]:
            if 0 == len(existingImages) or pic not in existingImages:
                thisMovie["image"] = pic
                existingImages.append(pic)
                break

        # Loop through the list of relevant titles, picking the first one that hasn't already been used based on the first 6 characters
        for titleOpt in mySettings[i]["titles"]:
            if 0 == len(existingTitles) or titleOpt[:5] not in existingTitles:
                thisMovie["title"] = titleOpt
                existingTitles.append(titleOpt[:5])
                break

        myMovies.append(thisMovie)

    return myMovies




def apology(errMsg, errcode):
    """Render the apology page."""
    return render_template("apology.html", theError=errMsg), errcode