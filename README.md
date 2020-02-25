# webpage-searching

Run indexer.py first:

  * Creates an inverted index on a set of documents or scraped webpages

    - Input Format: path/to/directory

      * File path to directory contains other directories which contain each of the webpages

      * i.e. path/to/directory

        - ./subdirectory1

        - ./subdirectory2

          * ./webpage1

          * ./webpage2

          * ./etc

        - ./etc

    - Creates the Index in batches then performs merging on it to form the completed Index


Then, run search_engine.py on resulting inverted index:

  * Asks for a search term or phrase to search for and uses cosine_similarity to calculate the most "relevant" document

-----

Other files are helpers/Objects required for both programs to function

  * stemProcessor.py: performs stemming on the contents of the webpages/documents

    - used for both Indexing and Searching

  * posting.py: the Posting Object which is used to keep track of a particular webpage's/document's statistics or features, such as word count

    - used for Indexing

  * DocumentVector.py: docVector object for placing Document statistics into a vector form that is used to calculate cosine_similarity

    - used for Searching
