"""Here you can import/implement macros.

This module will get reloaded per request to be up to date.

Use `superdesk.macro_register.macros.register` for registration.
"""

import os.path
from superdesk.macros import load_macros


macros_folder = os.path.realpath(os.path.dirname(__file__))
load_macros(macros_folder, package_prefix="ntb.macros")
