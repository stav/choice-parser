"""Choice Parser"""
# :copyright: (c) 2100 Steven Almeroth.
# :license:   MIT, see LICENSE for more details.

import sys

VERSION = (0, 1, 0, "alpha1")

__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Steven Almeroth"
__contact__ = "sroth77@gmail.com"
__homepage__ = "http://warriorship.org/projects/choice"
__docformat__ = "restructuredtext"

if sys.version_info < (2, 5):
    raise Exception(
        "Python 2.4 is not supported by this version. "
        "Please use a newer version of Python.")
