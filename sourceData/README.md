# Guide to sourceData files
## Commands
* "#" as the first character on a line describes the type of import
* "~" as the first character on a line means a new group/category

## Tasks
### Add a new main character
1. Ensure the words already exist in the words table. If not, add the new words (see words)
2. Ensure all pronouns already exist in words table. If not, add the new pronouns (see pronounSets)
3. Add main character settings. See characterSettings section
4. Optional: Consider linking to a title. (see titleTemplates)
5. Optional: Consider linking to an image. (see images, wordsToImages)

### Add more words
1. Add the words (see words section below)
2. Consider linking the new words to a title (see titleTemplates)
3. Consider linking the new words to an image (see wordsToImages)

### Add a new image
1. Import the image info (see images)
2. Ensure the activating words already exist in the words table. If not, add the new words (see words)
3. Link the image to appropriate words, so it can be triggered. See wordsToImages

### Add a new title
See titles

### Add more probabilities options
1. Ensure any resulting words and/or categories already exist in the relevant 
tables (see words)
2. See probabilities



## Import Types
### Character Settings
#### Command
\#characterSettings

#### Table/s affected
* characterSettings
* words (location)

#### Prerequisites
The characterSettings table requires:
* Character words to already exist in the words table
* Pronoun words to already exist in the words table

#### Layout
*characterWords*
    p=*pronouns_csv*    h=*hometowns_csv*

#### Example
woman
	p=she	h=small town,village,farm
demon
	p=she,he,it	h=fiery depths of Hell



### Images
#### Command
\#images

#### Table/s affected
* images

#### Prerequisites
None

#### Layout
*imageName*,*filename*,*fileExtension*

#### Example
darker,darker-and-grittier,png



### Infinitives
#### Command
\#infinitives

#### Table/s affected
* infinitives

#### Prerequisites
None

#### Layout
*infinitive_A*
*infinitive_B*

#### Example
to work
to meet



### PronounGroups
#### Command
\#pronounGroupMembers

#### Table/s affected
* pronounGroups
* pronounGroupMembers

#### Prerequisites
PronounGroups require:
* Pronouns must already exist in pronouns table

#### Layout
~*pronounGroupName_A*
	p=*pronoun_A*
~*pronounGroupName_B*
	p=*csvListOfPronouns_B*

#### Example
#pronounGroupMembers
~she/he/it
	p=she,he,it



### PronounSets
#### Command
\#pronounSets

#### Table/s affected
* pronounSets
* words (pronoun)
* categories

#### Prerequisites
None

#### Layout
*subjectPronoun_A*,*objectPronoun_A*
*subjectPronoun_B*,*objectPronoun_B*

#### Example
she,her
he,him



### Probabilities
#### Command
\#probabilities

#### Table/s affected
* probabilities
* choiceGroups

#### Prerequisites
The probabilities table requires:
* If referring to a words record, it must already exist in the words table
* If referring to a category, it must already exist in the categories table

#### Layout
~*choiceGroupName_A*
    *%ofA1* *flags*
    *%ofA2* *flags*
    *%ofA3* *flags*
~*choiceGroupName_B*
    *%ofB1* *flags*
    *%ofB2* *flags*

#### Optional Flags
* n -- add a note
* w -- link to a words record
* c -- link to a category (program will select a word from this category)
* p -- prefix string. Including `#[categoryName]#` in the string means the generator will pick a random words record assigned to the category `categoryName`

#### Example
~toBeeOrNotToBee
	0.92	n=not to bee	w= 
	0.08	n=to bee	w=a swarm of bees in the shape of
~lifeguide
	0.80	c=humanoid	p=#[adjective]# #[age]#
	0.08	c=animal	p=#[adjective]# talking
	0.08	c=inanimate	p=#[adjective]# sentient
	0.04	c=specialLifeguide

#### Notes
Ideally the probabilities decimals in a choiceGroup should add up to 1, but if 
they don't, the program will handle it.



### Words
#### Command
\#words

#### Table/s affected
* words (any category)
* categories

#### Prerequisites
None

#### Layout
~*categoryName_A*
*words_A1*
*words_A2*
~*categoryName_B*
*words_B1*
*words_B2*

#### Example
#words
~humanoid
woman
demon
~animal
fox



### Verbs
#### Command
\#verbs

#### Table/s affected
* verbs
* words (verb)

#### Prerequisites
The verbs table requires:
* Pronoun groups must already exist in the pronounGroups table
* Pronouns must already exist in the words table
* Infinitives must exist in the infinitives table

#### Layout
~*infinitive*
	*pronounGroup\_A*=*verb\_A*
	*pronounGroup\_B*=*verb\_B*

#### Example
~to work
	she/he/it=works
	they=work



### wordsToImages
#### Command
\#wordsToImages

#### Table/s affected
* wordsToImages

#### Prerequisites
The wordsToImages table requires:
* All words must already exist in the words table
* All images must already exist in the images table

#### Layout
*wordsDisplay*,*imageName*

#### Example
ethically questionable,darker


### titleTemplates
#### Command
\#titleTemplates

#### Table/s affected
* titleTemplates
* wordsToTitles

#### Prerequisites
The wordsToImages table requires:
* All words must already exist in the words table

#### Layout
*titleDisplay*//*wordsDisplay*
*titleBaseStr*//

#### Example
Romance at the Rural Apiary//rural apiary
A Dash of #[topic]#//
