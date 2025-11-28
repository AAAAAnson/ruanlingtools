# -*- coding: utf-8 -*-
"""
Router package initialization
Exports all API routers for inclusion in main app
"""

from . import ai
from . import image
from . import pdf
from . import settings
from . import text
from . import youtube

__all__ = ['ai', 'image', 'pdf', 'settings', 'text', 'youtube']
