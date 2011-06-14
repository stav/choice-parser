
System Overview
===============
 
* *Project Lead*: **Greg Dingle**
* *Author*: **Steven Almeroth** sroth77@gmail.com
* *Repository*: https://github.com/stav/choice-parser
 
This project began when `Greg Dingle <https://github.com/gregdingle>`_
contacted the author on `oDesk <https://www.odesk.com/jobs/~~50ae539e104cafa1>`_
about building a Python application.  A `github project <https://github.com/stav/choice-parser>`_
was setup with the first commit commit on 22 April 2011.

It has been determined by the author that the :class:`~choice.router.Router`
class should be redesigned to handle multiple PDF converters in improve the
performace of the parsers.  The project leader has determined that this work
will be postponed indefinitely.

PDF Conversion
--------------

Right now the system only uses one converter, namely the command-line application
``pdftotext`` to convert binary PDF data to plain text.  Adding more converters
to the system gives the parsers a better chance of coming up with the correct
format.

PDF converter options:

* pdftotext - http://www.foolabs.com/xpdf/
* pyPdf - http://pybrary.net/pyPdf/
* PDFMiner - http://www.unixuser.org/~euske/python/pdfminer/
* slate (PDFMiner) - http://pypi.python.org/pypi/slate
* gfx - http://www.swftools.org/gfx_tutorial.html

Github
------

A new branch `fatty <https://github.com/stav/choice-parser/tree/fatty>`_
was created on 14 June 2011 to usher in the redesign which allows for multiple
PDF converters to submit their renderings for a single file.  The branch
is so-named because the :class:`~choice.router.Router` will maintain in-memory
all the input data, including multiple rendered PDF conversions, instead of
discarding them after parsing.
