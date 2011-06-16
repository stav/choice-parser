"""Choice Parser"""
# :copyright: (c) 2011 Steven Almeroth.
# :license:   MIT, see LICENSE for more details.

import sys

VERSION = (0, 1, 0, "alpha1")

__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Steven Almeroth"
__contact__ = "sroth77@gmail.com"
__homepage__ = "http://warriorship.org/projects/choice"
__docformat__ = "restructuredtext"

if sys.version_info < (2, 7):

    version = '.'.join((str(v) for v in sys.version_info))

    raise SystemExit(
        "You will need at least Python version 2.7 to use this applicaton.\n"
        "Please try a newer version of Python than %s." %
            version
        )
