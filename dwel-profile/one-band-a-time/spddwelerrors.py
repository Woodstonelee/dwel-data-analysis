#!/usr/bin/env python
"""
All exceptions for processing DWEL data in SPD format. Inherit from
spdtlserrors.py
"""

from spdtlstools.spdtlserrors import *

class BandDisagreeError(SPDError):
    "Scan information from NIR and SWIR does not agree"
