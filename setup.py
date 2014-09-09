# -*- coding: utf-8 -*-
"""
Created on Fri Nov 04 14:06:35 2011

@author: X220
"""

from distutils.core import setup
import py2exe
setup(
    windows=[{"script":"edsstat.py"}],
    options={"py2exe":
                     {"includes":["sip"], "bundle_files" : 1}},
    zipfile = None )
                