# Object for turning document features/information into vectors of data
#   to make calculating cosine and similarity comparisons for different
#   webpages/documents

class docVector:

    vectorDict = dict()
    docLengths = dict()
    numberOfTerms = 0

    def __init__(self):
        self.vectorDict = dict()
        self.docLengths = dict()
        self.numberOfTerms = 0

    def setNumberOfTerms(self, n):
        self.numberOfTerms = n

    def insertDocumentsForTerm(self, termIndex, DocumentInfo):


        if (self.vectorDict.get(int(DocumentInfo[0])) == None):
            vec = [0.0] * self.numberOfTerms
            vec[termIndex] = float(DocumentInfo[1])

            self.vectorDict[int(DocumentInfo[0])] = vec
            self.docLengths[int(DocumentInfo[0])] = float(DocumentInfo[2])
        else:
            temp = self.vectorDict[int(DocumentInfo[0])]
            temp[termIndex] = float(DocumentInfo[1])

            self.vectorDict[int(DocumentInfo[0])] = temp
            self.docLengths[int(DocumentInfo[0])] = float(DocumentInfo[2])

