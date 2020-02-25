import json

from bs4 import BeautifulSoup
import nltk
# Testing Imports
import os
import io
import re
import posting
import math

# This downloads some resource that nltk uses to process the text;
# This line only needs to be run once but leaving it in should be fine
nltk.download('punkt')

def stemmer(content):
    """
    Function for reading in the content of a website's html text and performs PorterStemmer on the text.
    Also separates stems into 2 different lists for special Tags and normal body text.
    """
    ps = nltk.PorterStemmer()

    bodyStems = []

    specialStems = []

    specialWhitelist = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                        'strong',
                        'title',
                        'b',
                        'i',
                        'em'
                        ]

    bodyWhitelist = ['html',
                    'span',
                    'p',
                    'a'
                    'ul', 'li', 'ol',
                    'small'
                    ]

    bodyOutput = ''
    specialOutput = ''

    soup = BeautifulSoup(content, 'lxml')
    text = soup.find_all(text = True)

    for t in text:
        # filters special tags we want
        if t.parent.name in specialWhitelist:

            specialOutput += '{} '.format(t)
        # filters 'body' tags we want
        elif t.parent.name in bodyWhitelist:

            bodyOutput += '{} '.format(t)  # appends the text



    specialWords = nltk.word_tokenize(specialOutput)
    bodyWords = nltk.word_tokenize(bodyOutput)

    for sw in specialWords:
        # Append stems from special Tags
        if (sw.isascii()):
            specialStems.append(ps.stem(sw))
    for bw in bodyWords:
        # Append stems from body Tags
        if (bw.isascii()):
            bodyStems.append(ps.stem(bw))



    return specialStems, bodyStems


def stemCounter(tokens):
    """
    Takes in a stems List and counts the number of occurences
    that stem appears
    """

    stemCount = dict()

    for t in tokens:
        if (stemCount.get(t) == None):
            stemCount[t] = 1
        else:
            stemCount[t] += 1

    return stemCount


# Some basic testing scripts: runs only if this file is "main"
if (__name__ == "__main__"):

    directory = os.fsdecode(str("/home/hoan/CS121/HW/HW3-1/test/testInput"))

    url_mapping = dict()
    special_post_map = dict()
    body_post_map = dict()

    specialIndex = dict()
    bodyIndex = dict()

    counter = 0
    batchCount = 0
    pIndex = 1

    for file in os.listdir(directory):
        # For the Root Directory

        # Append the Root Directory with the child file (e.g. ics.uci.edu == child)
        inner_directory = directory + "/" + file
        #inner_directory = os.fsdecode("/home/hoan/CS121/HW/HW3-1/test/testInput/aiclub_ics_uci_edu")
        print("Directory: ", inner_directory)


        for inner_file in os.listdir(inner_directory):
            if (batchCount >= 10):
                print("Batch Size Reached " + str(batchCount) + ": Writing to file:")
                # SortAndWriteToFile
                # SORT
                iSpecialList = sorted( specialIndex )
                iBodyList = sorted( bodyIndex )

                # WRITE
                with io.open('partialSpecialIndex' + str(pIndex) + '.txt', 'w', encoding = "utf-8") as pf:
                    for item in iSpecialList:
                        pf.write("%s : ["%(item))
                        for p in specialIndex[item]:
                            pf.write("(%s;%s), "%(p[0], p[1]))
                        print(item, " : ", specialIndex[item])
                        pf.write("]\n")

                with io.open('partialBodyIndex' + str(pIndex) + '.txt', 'w', encoding = "utf-8") as pf:
                    for item in iBodyList:
                        pf.write("%s : ["%(item))
                        for p in bodyIndex[item]:
                            pf.write("(%s;%s), "%(p[0], p[1]))
                        print(item, " : ", bodyIndex[item])
                        pf.write("]\n")

                # Reset Relevant Data Structures and Counters
                print("Print Special Tags Index: ",specialIndex)
                print("Print Body Index: ", bodyIndex)

                specialIndex.clear()
                bodyIndex.clear()

                batchCount = 0
                pIndex += 1
            #'''
            # For the Child Directory
            filename = os.fsdecode(inner_file)

            # Checks the file if it is a json file
            if filename.endswith(".json"):
                file_path = inner_directory + "/" + filename
                #print("File Path: ", file_path)
                with open(file_path, 'r') as f:
                    loaded_json = json.load(f)
                    if loaded_json['encoding'] in set(['utf-8','ascii']):
                        url_mapping[counter] = loaded_json['url']

                        ### Text Parsing Here ###
                        # Get the tokens on the Document's contents
                        specialStems, bodyStems = stemmer( loaded_json['content'] )
                        # Count the occurences for each unique token
                        specialFreqTable = stemCounter( specialStems )
                        bodyFreqTable = stemCounter( bodyStems )

                        # Convert word counts ==> tf values
                        for item in specialFreqTable.items():
                            specialFreqTable[item[0]] = 1+math.log10(item[1])

                        for item in bodyFreqTable.items():
                            bodyFreqTable[item[0]] = 1+math.log10(item[1])

                        # Create Posting object with current docId and the document's tokenCounts
                        specialPost = posting.Posting(counter, specialFreqTable)
                        bodyPost = posting.Posting(counter, bodyFreqTable)

                        # Add post object to post_map for later use (when querying Index: gets DocId and use DocId on post_map to get full Posting object)
                        special_post_map[counter] = specialPost
                        body_post_map[counter] = bodyPost

                        # Add this Posting object's DocId to the Index
                        # For each unique token (from the Document's freqTable),
                        for k,v in specialFreqTable.items():
                            # If the token k does not exist in the index yet...
                            if (specialIndex.get(k) == None):
                                # Make a new entry with a <list of Postings> and place the Posting object associated with the current Document inside

                                # Compute IDF

                                specialIndex[k] = [ [specialPost.getDocId(), v] ]

                            # Else: (the token already exists in the index)
                            else:
                                # Append the Posting object associated with the current Document to the index's existing list of pages
                                specialIndex[k].append( [specialPost.getDocId(), v] )

                            #print(Index[k])

                        for k, v in bodyFreqTable.items():
                            if (bodyIndex.get(k) == None):
                                bodyIndex[k] = [ [bodyPost.getDocId(), v] ]
                            else:
                                bodyIndex[k].append( [bodyPost.getDocId(), v])

                        counter += 1
                        batchCount += 1

                continue
            else:
                continue

    print("Batch Size Reached " + str(batchCount) + ": Writing to file:")
    # SortAndWriteToFile
    # SORT
    iSpecialList = sorted( specialIndex )
    iBodyList = sorted( bodyIndex )

    # WRITE
    # Special Tags Index...
    with io.open('partialSpecialIndex' + str(pIndex) + '.txt', 'w', encoding = "utf-8") as pf:
        for item in iSpecialList:
            pf.write("%s : ["%(item))
            for p in specialIndex[item]:
                pf.write("(%s;%s), "%(p[0], p[1]))
            print(item, " : ", specialIndex[item])
            pf.write("]\n")

    # Body Text Index...
    with io.open('partialBodyIndex' + str(pIndex) + '.txt', 'w', encoding = "utf-8") as pf:
        for item in iBodyList:
            pf.write("%s : ["%(item))
            for p in bodyIndex[item]:
                pf.write("(%s;%s), "%(p[0], p[1]))
            print(item, " : ", bodyIndex[item])
            pf.write("]\n")

    # Reset Relevant Data Structures and Counters
    print("Print Special Tags Index: ",specialIndex)
    print("Print Body Index: ", bodyIndex)

    specialIndex.clear()
    bodyIndex.clear()

    batchCount = 0
    pIndex += 1
