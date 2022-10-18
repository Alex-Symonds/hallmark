-- Create tables for Hallmark project
CREATE TABLE categories(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE choiceGroups(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE infinitives (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE pronounGroups(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE pronounGroupMembers(
    id INTEGER PRIMARY KEY,
    group_id INTEGER,
    pronoun_id INTEGER,
    FOREIGN KEY(group_id)
        REFERENCES pronounGroups(id),
    FOREIGN KEY(pronoun_id)
        REFERENCES words(id)
);

CREATE TABLE words(
    id INTEGER PRIMARY KEY,
    categories_id INTEGER NOT NULL,
    display TEXT NOT NULL,
    FOREIGN KEY(categories_id)
        REFERENCES categories (id)
);

CREATE TABLE charactersToPronouns(
    id INTEGER PRIMARY KEY,
    character_id INTEGER NOT NULL,
    subjectPronoun_id INTEGER NOT NULL,
    FOREIGN KEY (character_id)
        REFERENCES words (id),
    FOREIGN KEY (subjectPronoun_id)
        REFERENCES words (id)
);

CREATE TABLE charactersToHometowns(
    id INTEGER PRIMARY KEY,
    character_id INTEGER,
    location_id INTEGER,
    FOREIGN KEY (character_id)
        REFERENCES words (id),
    FOREIGN KEY (location_id)
        REFERENCES words (id)
);

CREATE TABLE probabilities(
    id INTEGER PRIMARY KEY,
    choiceGroups_id INTEGER NOT NULL,
    probability REAL NOT NULL,
    note TEXT,
    words_id INTEGER,
    categories_id INTEGER,
    prefixStr TEXT,
    FOREIGN KEY (choiceGroups_id)
        REFERENCES choiceGroups (id),
    FOREIGN KEY (words_id)
        REFERENCES words (id),
    FOREIGN KEY (categories_id)
        REFERENCES categories (id)
);

CREATE TABLE pronounSets(
    id INTEGER PRIMARY KEY,
    subjectPronoun_id INTEGER,
    objectPronoun_id INTEGER,
    FOREIGN KEY (subjectPronoun_id)
        REFERENCES words (id),
    FOREIGN KEY (objectPronoun_id)
        REFERENCES words (id)
);

CREATE TABLE verbs(
    id INTEGER PRIMARY KEY,
    infinitives_id INTEGER,
    result_id INTEGER,
    pronounGroups_id INTEGER,
    FOREIGN KEY (infinitives_id)
        REFERENCES infinitives (id),
    FOREIGN KEY (result_id)
        REFERENCES words (id),
    FOREIGN KEY (pronounGroups_id)
        REFERENCES pronounGroups (id)
);

CREATE TABLE images(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    filename TEXT NOT NULL,
    fextension VARCHAR(4) NOT NULL
);

CREATE TABLE wordsToImages(
    id INTEGER PRIMARY KEY,
    words_id INTEGER,
    images_id INTEGER,
    FOREIGN KEY(words_id)
        REFERENCES words(id),
    FOREIGN KEY(images_id)
        REFERENCES images(id)
);

CREATE TABLE titleTemplates(
    id INTEGER PRIMARY KEY,
    titleTemplate TEXT NOT NULL
);

CREATE TABLE wordsToTitles(
    id INTEGER PRIMARY KEY,
    words_id INTEGER,
    titleTemplates_id INTEGER,
    FOREIGN KEY(words_id)
        REFERENCES words(id),
    FOREIGN KEY(titleTemplates_id)
        REFERENCES titleTemplates(id)
);

-- Create indexes for hallmark.db
CREATE INDEX words_index ON words(id, display, categories_id);
CREATE INDEX ctp_index ON charactersToPronouns(character_id);
CREATE INDEX cth_index ON charactersToHometowns(character_id);
CREATE INDEX cat_index ON categories(id, name);
CREATE INDEX verb_index ON verbs(infinitives_id, pronounGroups_id);
CREATE INDEX inf_index ON infinitives(name);
CREATE INDEX probs_index ON probabilities(id);
CREATE INDEX cg_index ON choiceGroups(name);
CREATE INDEX img_index ON images(name);