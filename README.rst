
Multiple Choice Test Parser
===========================

Project designed by `Greg Dingle <https://github.com/gregdingle>`_

    I'd like to build a program that will take in a multiple choice test in free form text and output it in a structured form of stem and options. See http://en.wikipedia.org/wiki/Multiple_choice_test for more background.

    The program should be designed to work well with any student or teacher who 
    has a multiple choice test. It must be tolerate of input and provide some kind of human validation step. See Excel's "split into cells" feature for a good example of how to do human-lead parsing.

    I think the best way to tackle this problem is to iterate on a known corpus
    of real-world tests. You can then try different approaches such as regex and natural language parsing. Luckily Scribd.com has a large corpus of such tests accessible by API. 

    Take a look at:
        * http://www.scribd.com/search?query=multiple+choice
        * http://www.scribd.com/doc/5057238/spreadsheet-multiple-choice-quiz
        * http://www.scribd.com/developers
        * http://www.scribd.com/developers/api?method_name=docs.getDownloadUrl

    The project scope will start small and hopefully grow big. The first deliverable would only be a command line script that takes in text and outputs structured text (JSON, XML or something), along with unit tests. 

    Next would be integration with the scribd API and a database, so we could try to convert any set of scribd documents at will and store the results. 

    Getting more general, it would be great to have the ability to parse tests hosted on other sites in HTML format. See http://dmv.ca.gov/pubs/interactive/tdrive/clm1written.htm for an example.

    Finally, I'd like to make the core algorithm of this project an open source project so others who have the same need can benefit. I see this as a benefit to any developer on the project also since they would get their name promoted.