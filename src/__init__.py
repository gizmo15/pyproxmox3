#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Proxmox api module."""

# /*
# * ----------------------------------------------------------------------------
# * "THE BEER-WARE LICENSE" (Revision 42):
# * <boris.tassou@securmail.fr> wrote this file. As long as you retain this notice you
# * can do whatever you want with this stuff. If we meet some day, and you think
# * this stuff is worth it, you can buy me a beer in return Boris Tassou
# * ----------------------------------------------------------------------------
# */

import sys

# Global name
__version__ = '0.0.1'
__author__ = 'Boris Tassou <boris.tassou@securmail.fr>'
__license__ = 'Beerware'

try:
    import requests
except ImportError:
    print('requests library not found')
    sys.exit(1)
