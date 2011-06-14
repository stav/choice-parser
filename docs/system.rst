
System
******

The system is written in the `Python <http://www.python.org/>`_ programming
language.

Installation
============

::

    $ git clone https://stav@github.com/stav/choice-parser.git

Requirements
============

* **Python**
    - 2.5+

Two External components are used to convert Portable Document Format (PDF)
files to plain text for consumption buy the parsers.  Either component will
work and both will be used if available offering better odds of successful
parsing.  If neither component is available, PDF files will not be processed.

PdfToText
---------

``pdftotext`` is part of the `Xpdf <http://www.foolabs.com/xpdf/>`_ software
suite.  On most Linux distributions pdftotext is included as part of the
`poppler-utils package <http://poppler.freedesktop.org/>`_.  Xpdf runs under
the X Window System on UNIX, VMS, and OS/2. The non-X components (pdftops,
pdftotext, etc.) also run on Win32 systems and should run on pretty much any
system with a decent C++ compiler.

PyPdf
-----

``pyPdf`` from Mathieu Fenniak is a Pure-Python library built as a PDF toolkit.

http://pybrary.net/pyPdf/

Configuration
=============

No configuration file setup.

Interface
=========

A normal command-line interface is used.

Components
==========

The Router is the top-level component and Parser has the main logic.

Router
------

The :class:`~choice.router.Router` sets everything up.

Parser
------

The :class:`~choice.parser.Parser` is the meat and bones that reads
through the input.
