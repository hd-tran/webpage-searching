# Posting object to help keep track of certain aspects for indexing and searching
#   for terms or webpages

class Posting:

    docId = -1
    freqTable = dict()
    tfidfTable = dict()
    length = 0.0

    def __init__(self, docId, freqTable):
        self.docId = docId
        self.freqTable = freqTable

    def hasToken(self, token):
        return (self.freqTable.get(token) != None)

    def getDocId(self):
        return self.docId

    def setLength(self, input):
        self.length = input
    def getFreqTable(self):
        return self.freqTable

    def setTFIDF(self, tfidfTable):
        self.tfidfTable = tfidfTable

    def getTFIDF(self):
        return self.tf_idf
    def __str__(self):
        return str(self.docId)

    def __repr__(self):
        return "<Posting DocId:%i>" % (self.docId)
