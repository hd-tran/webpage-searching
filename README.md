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
