#!/usr/bin/env python3

import re
from urllib.request import urlopen
from english_words import english_words_lower_alpha_set

# read the cursed words
badWords = {ii.decode('utf-8').strip() for ii in urlopen("https://www.cs.cmu.edu/~biglou/resources/bad-words.txt")}

lcEnglishWordsWithCurses = badWords | english_words_lower_alpha_set

# 1337 subs, from https://nedbatchelder.com/text/hexwords.html
sub1337 = [
    ('for', '4'),
    ('four', '4'),
    ('to', '2'),
    ('ate', '8'),
    ('ten', '10'),
    ('g', '6'),
    ('l', '1'),
    ('i', '1'),
    ('o', '0'),
    ('s', '5'),
    ('t', '7')
]

isHexCharsRegex = re.compile('^[0-9a-f]+$')
guidGenRegex = re.compile('^([0-9a-f]{0,8})([0-9a-f]{0,4})([0-9a-f]{0,4})([0-9a-f]{0,4})([0-9a-f]{0,12})$')

# return a set of all GUID compliant ([0-9a-f]) 1337 words for argument *word*
def guidify(word):
    ret = set()
    
    # iterate through every combination of 1337 substitutions
    for use1337Sub in range(0, 2 ** len(sub1337)):
        subWord = word

        # attempt to apply each replacement in turn
        for ii in range(len(sub1337)):
            if (2**ii) & use1337Sub:
                subWord = subWord.replace(sub1337[ii][0], sub1337[ii][1])
        
        # if we are 0-9a-f, then accept
        if isHexCharsRegex.match(subWord):
            ret |= { subWord }
    return ret

# add guid words to cwords collection, as long as there is lenAvail space to add
# recurse like hell
# return true if we've added words to the collection, so we get the biggest collection 
# possible
def addWords(cwords, lenAvail):
    # donezo test
    if lenAvail <= 0:
        return False

    wordsAdded = False
    for word in lcEnglishWordsWithCurses:
        for gword in guidify(word):
            if len(gword) <= lenAvail:
                wordsAdded = True
                cwordsAdd = cwords + [{'word':word, 'gword':gword}]
                # try to add words. if we can't add any more, "process" them
                if not addWords(cwordsAdd, lenAvail - len(gword)):
                    processGuidSentence(cwordsAdd)
    
    return wordsAdded

# a GUID word was found. process it.
def processGuidSentence(cwords):
    # are gword boundries aligned with GUID -'s (found at positions 8, 12, 16, 20)?
    bpos = 0    # word break position
    guidDashPos = [8, 12, 16, 20]   # GUID dash positions
    hasBadWords = False
    for ii in cwords:
        bpos += len(ii['gword'])
        hasBadWords |= ii['word'] in badWords
        if len(guidDashPos) == 0:   # we have a winner!
            break
        elif bpos > guidDashPos[0]: # we overlapped a -. sorry
            break
        elif bpos == guidDashPos[0]: # we aligned to a -, move to next one
            guidDashPos.pop(0)
    dashAligned = len(guidDashPos) == 0

    # generate GUID and some attributes about GUID in a dict
    m = guidGenRegex.match(''.join([ii['gword'] for ii in cwords]))
    out = {
        'GUID': f"{m[1]:0<8}-{m[2]:0<4}-{m[3]:0<4}-{m[4]:0<4}-{m[5]:0<12}",
        'words': ' '.join([ii['word'] for ii in cwords]),
        'wordCount': len(cwords),
        'zfill': len(m[0])!=32,
        'dashAligned': dashAligned,
        'hasBadWords': hasBadWords,
    }
    print(out)

# start the recursive process
addWords([], 32)