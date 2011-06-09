===========================
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

Installation
============

Two External components are used to convert Portable Document Format (PDF) files to plain text for consumption buy the parsers.  Either component will work and both will be used if available offering better odds of successful parsing.  If neither component is available, PDF files will not be processed.

PdfToText
---------

``pdftotext`` is part of the `Xpdf <http://www.foolabs.com/xpdf/>`_ software suite.  On most Linux distributions pdftotext is included as part of the `poppler-utils package <http://poppler.freedesktop.org/>`_.  Xpdf runs under the X Window System on UNIX, VMS, and OS/2. The non-X components (pdftops, pdftotext, etc.) also run on Win32 systems and should run on pretty much any system with a decent C++ compiler.

PyPdf
-----

``pyPdf`` from Mathieu Fenniak is a Pure-Python library built as a PDF toolkit.

http://pybrary.net/pyPdf/
