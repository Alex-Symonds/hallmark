# Flask application for Hallmark webpage
import os
from flask import Flask, flash, redirect, render_template, request, session, Markup
from flask_session import Session
from tempfile import mkdtemp
from helpers import GetHallmarkSelection, apology
from hallmarkGenerator import GetHallmarkSettings
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/")
def index():
    """Render index page."""
    try:
        # Get settings for 3 x modified Hallmark movies
        mySettings = []
        for i in range(0,3):
            mySettings.append(GetHallmarkSettings(False))    
    
        # Arrange into a list of dictionaries, aiming for three different images and title templates
        myMovies = GetHallmarkSelection(mySettings)
        
        return render_template("index.html", movies=myMovies)
    except:
        return apology("Generation of improved Hallmark movies has failed. Hallmark is just really good as it is, apparently.", 403)
    
    
    
@app.route("/original", methods=["GET"])
def original():
    """Render page with the original Hallmark plot."""
    try: 
        # Get setting for the "original" Hallmark movie and arrange it into a dictionary
        originalMovie = GetHallmarkSettings(True)
        thisMovie = {}
        thisMovie["plot"] = Markup(originalMovie["plot"])
        thisMovie["image"] = originalMovie["images"][0]
        thisMovie["title"] = originalMovie["titles"][0]

        return render_template("original.html", myMovie = thisMovie)
    except:
        return apology("Attempt to lookup the original movie details failed.", 403)



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)



# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)