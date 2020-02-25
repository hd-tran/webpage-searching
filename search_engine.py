# Search engine to run on a set of indexed documents/webpages to find documents
#   using terms and/or phrases

import re
import numpy as np
from collections import Counter
import math
from nltk.stem import PorterStemmer, SnowballStemmer

from string import ascii_lowercase, ascii_uppercase
from string import digits
import time
import DocumentVector

def main():

    i = 20
    url_dic = dict()
    docId = []
    counter = 0
    with open("counter.txt",'r', encoding='utf-8') as ff:
        counter = int(ff.read())

    with open("url_index.txt",'r', encoding='utf-8') as f:
        text = f.read()
        text_2 = text.split("\n")

        for line in text_2:
            if( len(line) != 0):
                result_url = line.split(" : ")
                #print(result_url)
                url_dic[int(result_url[0])] = result_url[1]
        # docID -> URL

    while(True):
        query = input("what do you want to query: ")
        start_time = time.time()
        q_spec_vec, spec_post= querying(query,"special_final", counter)
        q_body_vec, body_post = querying(query,"body_final", counter)

        d_spec_vec = calculate_cosine(q_spec_vec, spec_post)
        #print("Testing d_spec_vec = ", d_spec_vec[:20])
        d_body_vec = calculate_cosine(q_body_vec,body_post)

       # print("Testing d_body_vec = ", d_body_vec[:20])

        for index in range(len(d_spec_vec)):
            if index < 20:
                docId.append(d_spec_vec[index][0])
                i -= 1
        for index in range(len(d_body_vec)):
            if (i > 0):
                docId.append(d_body_vec[index][0])
                i -=1
            else:
                break

        for count in range(len(docId)):
            print(count, " : ", url_dic[docId[count]])
        print("Time for query = %s" %(time.time()-start_time))
        docId.clear()

def calculate_cosine(query_vector, postings):
    # Change the opening of file to extract first letter of query_word and then open the file based on that first letter
    calc_result = dict()
    result_vec = []
    docVec = DocumentVector.docVector()
    docVec.setNumberOfTerms(len(postings.items()))

    for entry in postings.items():
        e = entry[1].strip("\n")

        result = entry[1].strip("][").split(", ")
        del result[-1]
        # result[0] = word, result[1] = [(docId, tf-idf, length)]
        for item in result:
            # item[0] = docId, item[1] = tf-idf, item[2] = length
            if(len(item) != 0):
                item = item.strip(')(').split(";")

                docVec.insertDocumentsForTerm(entry[0], item)


    for item in docVec.vectorDict.items():
        result_vec = np.array(item[1])/docVec.docLengths[item[0]]
        result_vec = np.dot(query_vector,result_vec)
        calc_result[item[0]] = result_vec


    sorted_result = sorted(calc_result.items(), key= lambda kv: (kv[1], kv[0]))

    return(sorted_result)


def querying(input, type_name, counter):

    # this chunk of the code mainly just opens the files up to be read
    posts = dict()
    startsWithLowerCaseString = re.compile("[a-z]")
    startsWithUpperCaseString = re.compile("[A-Z]")
    startsWithInt = re.compile("[0-9]")
    listOfOpens = []  # this is a list of open files we want to write into!
    # counter = -1
    for number in digits:
        respFile = open(type_name + str(number) + ".txt", "r")
        listOfOpens.append(respFile)
        # counter += 1
        # print(str(number) + " "  + str(counter))
    for letter in ascii_uppercase:
        respFile = open(type_name + letter + ".txt", "r")
        # counter += 1
        # print(letter + " " + str(counter))
        listOfOpens.append(respFile)
    for letter in ascii_lowercase:
        respFile = open(type_name + "_" + letter + ".txt", "r")
        # counter += 1
        # print(letter + " " + str(counter))
        listOfOpens.append(respFile)

    respFile = open(type_name + "theRest.txt", "r")
    listOfOpens.append(respFile)

    respFile = open(type_name + "Maven.txt", "r")
    listOfOpens.append(respFile)
    # ask for query
    query = input
    # split the query so we can find the words
    listOfWords = query.split()

    # use porter stemmer
    ps = PorterStemmer()

    # stem the word
    stemmedWords = [ps.stem(word) for word in listOfWords]

    # put into a counter dict so we can get the frequency of word in the query
    dictCounter = Counter(stemmedWords)
    #print(dictCounter)
    docCounter = counter  # this is a placeholder, supposed to contain the document Counter
    tfidf = list()
    length = 0
    wordIndex = 0
    for word, wordCount in dictCounter.items():
        if (startsWithLowerCaseString.match(word[0]) != None):  # if first char starts with lower case character
            #print(word)
            if (word[0:5] != "maven"):
                whichIndex = ord(word[0]) - 61  # get the index of which file the first char letter is located
            else:
                whichIndex = 63
            for line in listOfOpens[whichIndex]:
                #print(line)
                line = line.split(" :")  # split the line to parse
              #  print(" test line = ", line[0].strip())
                if word == line[0].strip():  # if one of the query words is the same , calculate
                    #print(line)
                    posts[wordIndex] = line[1]
                    docFreq = len(line[1].split(",")) - 1
                    #print(docFreq)
                    # tfidf= (1+ math.log(wordCount)) * math.log(docCounter / docFreq)
                    # print(tfidf)
                    # length =
                    tfidf.append(1 + math.log(wordCount) * math.log(docCounter / docFreq))
                    wordIndex += 1
                    break
        elif (startsWithUpperCaseString.match(word[0]) != None):  # if first char starts with upper case character
            whichIndex = ord(word[0]) - 55
            for line in listOfOpens[whichIndex]:
                line = line.split(" :")
                if word == line[0].strip():  # if one of the query words is the same , calculate
                   # print(line)
                    posts[wordIndex] = line[1]
                    docFreq = len(line[1].split(",")) - 1
                    #print(docFreq)
                    # tfidf= (1+ math.log(wordCount)) * math.log(docCounter / docFreq)
                    # print(tfidf)
                    # length =
                    tfidf.append(1 + math.log(wordCount) * math.log(docCounter / docFreq))
                    wordIndex += 1
                    break
        elif (startsWithInt.match(word[0]) != None):  # if first char starts with number
            whichIndex = ord(word[0]) - 48
            for line in listOfOpens[whichIndex]:  # if one of the query words is the same , calculate
                line = line.split(" :")
                if word == line[0].strip():
                    #print(line)
                    posts[wordIndex] = line[1]
                    docFreq = len(line[1].split(",")) - 1
                    tfidf.append(1 + math.log(wordCount) * math.log(docCounter / docFreq))
                    wordIndex += 1
                    break
        else:  # else
            print("we hit else")
            for line in listOfOpens[62]:
                line = line.split(":")
                if word == line[0].strip():  # if one of the query words is the same , calculate
                    #print(line)
                    posts[wordIndex] = line[1]
                    docFreq = len(line[1].split(",")) - 1
                    #print(docFreq)
                    # tfidf= (1+ math.log(wordCount)) * math.log(docCounter / docFreq)
                    # print(tfidf)
                    tfidf.append(1 + math.log(wordCount) * math.log(docCounter / docFreq))
                    wordIndex += 1
                    break
        length += wordCount ** 2
    tf_idf = np.array(tfidf)
    len_vec = np.array(math.sqrt(length))

    for openFile in listOfOpens:
        openFile.close()
    result_vec = tf_idf/math.sqrt(length)

    return(result_vec, posts)


if __name__ == '__main__':
    main()
