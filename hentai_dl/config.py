# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Global config module"""

import sys
import json
import os.path
import logging
from . import util

log = logging.getLogger("config")


_config = {}

if util.WINDOWS:
    _default_configs = [
        r"%APPDATA%\gallery-dl\config.json",
        r"%USERPROFILE%\gallery-dl\config.json",
        r"%USERPROFILE%\gallery-dl.conf",
    ]
else:
    _default_configs = [
        "/etc/gallery-dl.conf",
        "${XDG_CONFIG_HOME}/gallery-dl/config.json" if os.environ.get("XDG_CONFIG_HOME") else "${HOME}/.config/gallery-dl/config.json",
        "${HOME}/.gallery-dl.conf",
    ]


if getattr(sys, "frozen", False):
    # look for config file in PyInstaller executable directory (#682)
    _default_configs.append(os.path.join(os.path.dirname(sys.executable), "gallery-dl.conf",))



def clear():
    """Reset configuration to an empty state"""
    _config.clear()


def get(path : tuple, key : str, default = None, *, conf = _config):
    """Get the value of property 'key' or a default value"""
    
    for p in path:
        conf = conf[p]
    return conf.get(key, default)
    
