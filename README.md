# HALLMARK MOVIE PLOT GENERATOR
## Description:
The tool the writers of Hallmark movies never requested and don't want. Hallmark has produced a large number of movies which all share, broadly speaking, a single plot. This webpage aims to assist Hallmark's writing team by suggesting some minor modifications to their plot to help them continue reproducing the same movie over and over again for some time to come.

[Video demo](https://youtu.be/QcSA3JHbgBw)

## Summary:
* Mad Libs style sentence generator.
* The program maintains "Hallmarkiness" by applying weightings to the different replacement words, making the more colourful options rarer.
* Makes grammatical adjustments to pronouns and verbs depending on what's appropriate for the selected main character.
* Hallmarkiness requires the main character to return to a location of childhood significance, so rather than randomly selecting from a list of locations, the program always selects a location appropriate for the selected main character.
* The red notes scrawled across the sketchpad change depending on the contents of the plot sentence. Since there are three options loaded into the carousel, the program tries to return three different ones.
* The title changes depending on the contents of the plot sentence. Since there are three options loaded into the carousel, the program tries to return three different different types of titles.

## Requirements
* CS50 library
* Flask
* werkzeug