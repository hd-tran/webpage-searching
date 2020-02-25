# webpage-searching

Run indexer.py first:

  Creates an inverted index on a set of documents or scraped webpages
  
  Folder Format: first/second/document
  
  * Root of file path contains other directories which contain each of the webpages
  
Then, run search_engine.py on resulting inverted index:

  Asks for a search term or phrase to search for and uses cosine_similarity to calculate the most "relevant" document
