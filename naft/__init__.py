"""
This is a terrible idea.
"""
import sys
from naft.backports import dis as bp_dis

__title__ = 'NAFT'
__author__ = 'Isaac Dickinson'
__license__ = 'MIT'
__copyright__ = 'Copyright 2016 Isaac Dickinson'
__version__ = '0.0.1'

if sys.version_info[0:2] <= (3, 3):
    # Update sys.modules with our backported dis.
    sys.modules['dis'] = bp_dis
