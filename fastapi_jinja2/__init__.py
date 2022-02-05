"""fastapi-jinja2 - Adds integration of the Jinja2 template language to FastAPI. Credits: Micheal Kennedy of TalkPython.fm"""

__version__ = '0.1'
__author__ = 'Shuaib Mohammad <smartexpert@users.noreply.github.com>'
__all__ = ['template', 'global_init', 'not_found', 'response','fragment']

from .engine import global_init
from .engine import template
from .engine import fragment
from .engine import response
from .engine import not_found