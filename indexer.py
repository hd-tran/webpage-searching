# Performs Inverted Indexing on a collection of documents/scraped webpages so as to
#   create a way to search for particular documents/webpages using terms/phrases

import json
import os
import io
import re
from string import ascii_lowercase , ascii_uppercase
from string import digits
import tokenProcessor as tp
import posting
import math

import stemProcessor as sp

def indexing(filepath):
    # Change string in os.fsdecode() to whatever file path we need to parse over
    #directory = os.fsdecode(str("C:\\Users\\nashl\\Documents\\CS 121\\Project 3\\DEV\\"))
    directory = os.fsdecode(filepath)

    print(directory)
    counter = 0

    # Key = Doc Id Num
    # Value = Full URL
    url_mapping = dict()

    special_post_map = dict()
    body_post_map = dict()

    # Key = Token
    # Value = List<Posting> (List of Posting Objects)
    specialIndex = dict()
    bodyIndex = dict()

    batchCount = 0
    pIndex = 1
    for file in os.listdir(directory):
        # For the Root Directory

        # Append the Root Directory with the child file (e.g. ics.uci.edu == child)
        inner_directory = directory + "/" + file

        for inner_file in os.listdir(inner_directory):
            #'''
            # If Batch Count gets too large: write to file and reset Data Structures (in memory)
            if (batchCount >= 1000):
                print("Batch Size Reached " + str(batchCount) + ": Writing to file:")
                # SortAndWriteToFile
                # SORT
                sList = sorted( specialIndex )

                # WRITE
                with io.open('specialPartial' + str(pIndex) + '.txt', 'w', encoding = "utf-8") as pf:
                    for item in sList:
                        pf.write("%s : ["%(item))
                        for p in specialIndex[item]:
                            pf.write("(%s;%s), "%(p[0], p[1]))

                        pf.write("]\n")
                specialIndex.clear()
                # body
                bList = sorted(bodyIndex)
                # WRITE
                with io.open('bodyPartial' + str(pIndex) + '.txt', 'w', encoding = "utf-8") as pf:
                    for item in bList:
                        pf.write("%s : ["%(item))
                        for p in bodyIndex[item]:
                            pf.write("(%s;%s), "%(p[0], p[1]))

                        pf.write("]\n")
                # Reset Relevant Data Structures and Counters
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

                        specialStems, bodyStems = sp.stemmer( loaded_json['content'])
                        # Count the occurences for each unique token
                        #freqTable = tp.tokenCounter( tokens )

                        specialFreqTable = sp.stemCounter( specialStems )
                        bodyFreqTable = sp.stemCounter( bodyStems)

                        for item in specialFreqTable.items():
                            specialFreqTable[item[0]] = 1+math.log10(item[1])

                        for item in bodyFreqTable.items():
                            bodyFreqTable[item[0]] = 1+math.log10(item[1])

                        # Create Posting object with current docId and the document's tokenCounts
                        specialPost = posting.Posting(counter, specialFreqTable)
                        bodyPost = posting.Posting(counter, bodyFreqTable)

                        # Add post object to post_map for later use (when querying Index: gets DocId and use DocId on post_map to get full Posting object)
                        special_post_map[counter] = specialFreqTable
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
                                specialIndex[k].append( [specialPost.getDocId(), 1+math.log(v)] )

                        # Stores the body index
                        for k,v in bodyFreqTable.items():
                            # If the token k does not exist in the index yet...
                            if (bodyIndex.get(k) == None):
                                # Make a new entry with a <list of Postings> and place the Posting object associated with the current Document inside

                                # Compute IDF

                                bodyIndex[k] = [ [bodyPost.getDocId(), v] ]

                            # Else: (the token already exists in the index)
                            else:
                                # Append the Posting object associated with the current Document to the index's existing list of pages
                                bodyIndex[k].append( [bodyPost.getDocId(), 1+math.log(v)] )
                        # Copy loop for bodyIndex...

                        counter += 1
                        batchCount += 1

                continue
            else:
                continue

    print("Batch Size Reached " + str(batchCount) + ": Writing to file:")
    # SortAndWriteToFile
    # SORT
    sList = sorted(specialIndex)

    # WRITE
    with io.open('specialPartial' + str(pIndex) + '.txt', 'w', encoding="utf-8") as pf:
        for item in sList:
            pf.write("%s : [" % (item))
            for p in specialIndex[item]:
                pf.write("(%s;%s), " % (p[0], p[1]))
            pf.write("]\n")
    specialIndex.clear()
    # body
    bList = sorted(bodyIndex)
    # WRITE
    with io.open('bodyPartial' + str(pIndex) + '.txt', 'w', encoding="utf-8") as pf:
        for item in bList:
            pf.write("%s : [" % (item))
            for p in bodyIndex[item]:
                pf.write("(%s;%s), " % (p[0], p[1]))
            pf.write("]\n")
    # Reset Relevant Data Structures and Counters
    bodyIndex.clear()

    batchCount = 0
    pIndex += 1



    with open("url_index.txt",'w') as f:
        for item, value in url_mapping.items():
            f.write("%s : %s \n" %(item,value))
    with open("counter.txt",'w') as f:
        f.write(str(counter))
    # The DEV directory data has already been extracted

    # Begin to merge the partialIndexes
    # Initialize the first iteration of documents for special files
    special_ini = "specialPartial1.txt"
    special_sec = "specialPartial2.txt"
    special_merg = "specialMerge1.txt"
    while (True):
        # currentNumber  = secondDoc.rstrip(".txt")[-1]
        currentNumberForSecondDoc = re.findall(r'\d+', special_sec)[0]
        currentNumberForMergedDoc = re.findall(r'\d+', special_merg)[0]
        try:
            merge(special_ini, special_sec, special_merg)
        except:
            print("broken")
            if (special_merg == "specialMerge1.txt"):
                special_merg = "specialMerge2.txt"
            else:
                special_merg = "specialMerge1.txt"
            break
        # Increments the partialIndex value, e.g. from partialIndex2 -> partialIndex3
        newNumberForSecondDoc = str(int(currentNumberForSecondDoc) + 1)
        special_sec = "specialPartial" + newNumberForSecondDoc + ".txt"
        print(special_sec)

        if (special_ini == "specialPartial1.txt"):
            print("make change here first")
            special_ini = "specialMerge1.txt"
            special_merg = "specialMerge2.txt"
        elif (special_ini == "specialMerge1.txt"):
            print("make change when initialDoc is mergedDoc1")
            special_ini = "specialMerge2.txt"
            os.remove("specialMerge1.txt")
            special_merg = "specialMerge1.txt"
        else:
            print("make change when initialDoc is mergedDoc2")
            special_ini = "specialMerge1.txt"
            os.remove("specialMerge2.txt")
            special_merg = "specialMerge2.txt"

    # Compute the length with the given merged postings
    if(special_merg == "specialMerge1.txt"):
        computeLen("specialMerge1", "special_final", counter, special_post_map)
    else:
        computeLen("specialMerge2", "special_final", counter, special_post_map)

    # Initialize the first iteration for body files
    initialDoc = "bodyPartial1.txt"
    secondDoc = "bodyPartial2.txt"
    mergedDoc = "mergedDoc1.txt"
    while (True):
        # currentNumber  = secondDoc.rstrip(".txt")[-1]
        currentNumberForSecondDoc = re.findall(r'\d+', secondDoc)[0]
        currentNumberForMergedDoc = re.findall(r'\d+', mergedDoc)[0]
        try:
            merge(initialDoc, secondDoc, mergedDoc)
        except:
            print("broken")
            if (mergedDoc == "mergedDoc1.txt"):
                mergedDoc = "mergedDoc2.txt"
            else:
                mergedDoc = "mergedDoc1.txt"
            break
        # Increments the partialIndex value, e.g. from partialIndex2 -> partialIndex3
        newNumberForSecondDoc = str(int(currentNumberForSecondDoc) + 1)
        secondDoc = "bodyPartial" + newNumberForSecondDoc + ".txt"
        # mergedDoc = "mergedDoc" + newNumberForMergedDoc + ".txt"
        print(secondDoc)

        if (initialDoc == "bodyPartial1.txt"):
            print("make change here first")
            initialDoc = "mergedDoc1.txt"
            mergedDoc = "mergedDoc2.txt"
        elif (initialDoc == "mergedDoc1.txt"):
            print("make change when initialDoc is mergedDoc1")
            initialDoc = "mergedDoc2.txt"
            os.remove("mergedDoc1.txt")
            mergedDoc = "mergedDoc1.txt"
        else:
            print("make change when initialDoc is mergedDoc2")
            initialDoc = "mergedDoc1.txt"
            os.remove("mergedDoc2.txt")
            mergedDoc = "mergedDoc2.txt"

    # Compute the length with the given merged postings
    if(mergedDoc == "mergedDoc1.txt"):
        computeLen("mergedDoc1", "body_final", counter, body_post_map)
    else:
        computeLen("mergedDoc2", "body_final", counter, body_post_map)
    # Split the final partialIndex file into alphabetic files
    splitFinal("special_final")
    splitFinal("body_final")

def computeLen(filename , type_name, counter, postmap):

    n = counter
    tfidf_count = 0
    doc_ids = {}
    curr_id = []
    curr_tfidf = []
    tfIdfTable = dict()
    with open(str(filename) + ".txt", 'r', encoding = 'utf-8' ) as f:
        text = f.read()
        text_2 = text.split("\n")
        result = ''
        df = ''
        location_index = 0
        ff = open("result.txt", 'w+', encoding='utf-8')
        for line in text_2:
            result = line

            # result[0] = the word, result[1] = docID and tf values
            if (len(result) == 0):
                print("Result is empty!")
                break
            result = result.split(" : ")
            #Split and strips the result to obtain a list of corresponding docId and its tf values

            test = result[1].strip('][').split(", ")
            # Delete the extra [, ] at the end of each set
            del test[-1]
            # Calculates the idf value of that word
            idf = math.log10(n/len(test))


            # To extract the docId and the tf value from each individual item in the posting
            for item in test:
                item = item.strip(')(').split(';')
                # Find a better way to store curr_id and curr_tfidf
                # Stores the current docId into the list
                curr_id.append(item[0])
                # Calculate tfidf value from the docId
                tfidf = (float(item[1]) * idf)
                # Store the corresponding tf-idf value of the docId
                curr_tfidf.append(tfidf)
                # Set the post map of curr_docId 's tf-idf value
                if item[0] not in tfIdfTable.keys():
                    tfIdfTable[item[0]] = [tfidf]
                else:
                    tfIdfTable[item[0]].append(tfidf)
        # Write the docId and tf-idf value into another document
            # Writting currently removes the previous version, thus, only 1 result

        # All tf-idf values should be computed
        # Now we iterate through the entire postingmap to calculate its length
            ff.write("%s : ["%(result[0]))
            for item in curr_id:
                ff.write("(%s;%s), " % (item, curr_tfidf[tfidf_count]))
                tfidf_count += 1
            ff.write("]\n")
            tfidf_count = 0
            curr_tfidf.clear()
            curr_id.clear()
        ff.close()


    # Add lengthVectorDict[index] to write into new document file with format word : [(docId, tf-idf, len)]
    lengthVectorDict = dict()
    for docId, listOfTfIdf in tfIdfTable.items():
        squaredSum = 0
        for tfidf in listOfTfIdf:
            print(tfidf)
            squaredSum += tfidf ** 2
        answer = math.sqrt(squaredSum)
        lengthVectorDict[docId] = answer
       # print( "Tester Lenght of docId ",docId, " = ", lengthVectorDict[docId])

# CODE ADDED ON 11/20/2019  6:11PM  Objective = to write to a file with format word : [( docId, tf-idf, len )]
    test.clear()
    curr_id.clear()
    curr_tfidf.clear()
    tfidf_count = 0
    with open("result.txt", 'r', encoding = 'utf-8' ) as f:
        f_text = f.read()
        f_text2 = text.split("\n")
        result = ''
        location_index = 0
        last = open(type_name +".txt", 'w+', encoding='utf-8')
        for line in f_text2:
            result = line

            # result[0] = the word, result[1] = docID and tf values
            if (len(result) == 0):
                print("Result is empty!")
                break
            result = result.split(" : ")
            #Split and strips the result to obtain a list of corresponding docId and its tf values

            test = result[1].strip('][').split(", ")
            # Delete the extra [, ] at the end of each set
            del test[-1]

            # To extract the docId and the tf-idf value from each individual item in the posting
            for item in test:
                item = item.strip(')(').split(';')
                # Stores the current docId into the list
                curr_id.append(item[0])
                # Calculate tfidf value from the docId
                curr_tfidf.append(item[1])
            #Write the word
            last.write("%s :[" % (result[0]))
            #Iterate through the docIds and tf-idf values of eat item
            for item in curr_id:
                last.write("(%s;%s;%s), " % (item, curr_tfidf[tfidf_count],lengthVectorDict[(item)]))
                tfidf_count += 1
            last.write("]\n")
            tfidf_count = 0
            curr_tfidf.clear()
            curr_id.clear()


def merge(textFile1, textFile2, writeFile):
    tempFile1 = open(textFile1, "r")  # open the first file
    tempFile2 = open(textFile2, "r")  # open the second
    line1 = tempFile1.readline()  # grab the first line of first file
    line2 = tempFile2.readline()  # grab the second line of second file
    openWriteFile = open(writeFile, "w+")
    while (line1 != "" and line2 != ""):  # while we iterate through the lines
        if (line1[0] != ":"):
            splitLine1 = line1.split(":")
            token1 = splitLine1[0]
            stringList = splitLine1[1].strip("\[\] \n")
            listOfIndexes1 = stringList.split(" ,")
        else:  # in case we split this off
            splitLine1 = line1[1:].split(":")  #
            token1 = splitLine1[0]
            stringList = splitLine1[1].strip("\[\] \n")
            listOfIndexes1 = stringList.split(" ,")

        if (line2[0] != ":"):
            splitLine2 = line2.split(":")
            token2 = splitLine2[0]
            stringList = splitLine2[1].strip("\[\] \n")
            listOfIndexes2 = stringList.split(" ,")
        else:  # in case we split this off
            splitLine2 = line2[1:].split(":")
            token2 = splitLine2[0]
            stringList = splitLine2[1].strip("\[\] \n")
            listOfIndexes2 = stringList.split(" ,")

        if (token1 == token2):
            # myList.append(token1)
            openWriteFile.write(line1.strip()[:-1] + listOfIndexes2[0] + " ]\n")
            line1 = tempFile1.readline()
            line2 = tempFile2.readline()
        elif (token1 < token2):
            # myList.append(token1)
            openWriteFile.write(line1)
            line1 = tempFile1.readline()
        else:
            # myList.append(token2)
            openWriteFile.write(line2)
            line2 = tempFile2.readline()

    tempFile1.close()
    tempFile2.close()
    openWriteFile.close()


def splitFinal(type_name):
    mainFile = open(type_name + ".txt", "r", encoding="utf-8")  # open the computed length file
    startsWithLowerCaseString = re.compile("[a-z]")
    startsWithUpperCaseString = re.compile("[A-Z]")
    startsWithInt = re.compile("[0-9]")
    listOfOpens = []  # this is a list of open files we want to write into!
    # counter = -1
    for number in digits:
        respFile = open(type_name + str(number) + ".txt", "w")
        listOfOpens.append(respFile)
        # counter += 1
        # print(str(number) + " "  + str(counter))
    for letter in ascii_uppercase:
        respFile = open(type_name + letter + ".txt", "w")
        # counter += 1
        # print(letter + " " + str(counter))
        listOfOpens.append(respFile)
    for letter in ascii_lowercase:
        respFile = open(type_name + "_" + letter + ".txt", "w")
        # counter += 1
        # print(letter + " " + str(counter))
        listOfOpens.append(respFile)

    respFile = open(type_name + "theRest.txt", "w")
    listOfOpens.append(respFile)

    respFile = open(type_name + "Maven.txt",'w')
    listOfOpens.append(respFile)
    # counter += 1
    # print (counter)
    # print(len(listOfOpens))

    try:
        for line in mainFile:
            # for eveery line, check its first letter, if it starts with a certain char
            # put it in that file, if its like a special charcacter put it in the "splitFileTheRest"
            splitLine = line.split()
            token = splitLine[0]  # shouldnt have spaces regardless but just in case
            # print(splitLine[0].strip())
            print(token)
            if (startsWithLowerCaseString.match(token[0]) != None):  # if first char starts with lower case character
                if( token[0:5] != "maven"):
                    whichIndex = ord(token[0]) - 61  # this is just for indexing
                    listOfOpens[whichIndex].write(line)
                else:
                    listOfOpens[63].write(line)
            elif (startsWithUpperCaseString.match(token[0]) != None):  # if first char starts with upper case character
                whichIndex = ord(token[0]) - 55
                listOfOpens[whichIndex].write(line)
            elif (startsWithInt.match(token[0]) != None):  # if first char starts with number
                whichIndex = ord(token[0]) - 48
                listOfOpens[whichIndex].write(line)
            else:
                listOfOpens[62].write(line)
    except:
        print("error has occured")
        print(line)
        for openFile in listOfOpens:
            openFile.close()
    mainFile.close()

    for openFile in listOfOpens:
        openFile.close()


def extract_id(input):
    input = input.strip('][').split(", ")
    output = []
    for item in input:
        if item == "":
            # An empty set at the end of the list
            break

        elem = item.strip(")(").split(";")
        output.append(elem[0])
    return output

def print_index(index):
    with open('url_index.txt','r', encoding='utf-8') as f:
        test = f.readlines()
        print(test[index])

def main():
    filepath = input("File Path To Locally Saved Webpages: ")
    indexing(str(filepath))


if __name__ == '__main__':
    main()

'''
Things to add:

    1. Change cosine method for more than 1 word
    2. Combine all functions into one
    3. Stemming for index and query
    4. Configure stop-words, either using nltk or tf-idf value
    5. Return top 20 URLs based on important words and cosine similarity
    
'''
