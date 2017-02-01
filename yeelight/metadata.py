# -*- coding: utf-8 -*-
"""Project metadata.

Information describing the project.
"""

from .version import __version__

# The package name, which is also the "UNIX name" for the project.
package = 'yeelight'
project = "python-yeelight"
project_no_spaces = project.replace(' ', '')
version = __version__
description = ("yeelight is a Python library for controlling YeeLight WiFi RGB"
               " LED bulbs.")
authors = ['Stavros Korokithakis']
authors_string = ', '.join(authors)
emails = ['hi@stavros.io']
license = 'BSD'
copyright = '2016 ' + authors_string
url = 'https://gitlab.com/stavros/python-yeelight'
