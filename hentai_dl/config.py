# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Global config module"""

import sys
import json
import os.path
import logging
from .util import WINDOWS, SENTINEL

log = logging.getLogger("config")


_config = {}

if WINDOWS:
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
    _default_configs.append(os.path.join(os.path.dirname(sys.executable), "hentai-dl.conf",))



def clear():
    """Reset configuration to an empty state"""
    _config.clear()


def get(path : tuple, key : str, default = None, *, conf = _config):
    """Get the value of property 'key' or a default value"""
    
    try:
        for p in path:
            conf = conf[p]
        return conf[key]
    except Exception:
        return default
    

def accumulate(path : tuple, key : str, *, conf=_config):
    """Accumulate the values of 'key' along 'path'"""

    result = []

    try:
        if key in conf:
            value = conf[key]
            if value:
                result.extend(value)

        for p in path:
            conf = conf[p]
            if key in conf:
                value = conf[key]
                if value:
                    result[:0] = value
    except Exception:
        pass
    return result


def interpolate(path, key, default=None, *, conf=_config):
    """Interpolate the value of 'key'"""
    if key in conf:
        return conf[key]
    try:
        for p in path:
            conf = conf[p]
            if key in conf:
                default = conf[key]
    except Exception:
        pass
    return default


def interpolate_common(common, paths, key, default=None, *, conf=_config):
    """Interpolate the value of 'key'
    using multiple 'paths' along a 'common' ancestor
    """
    if key in conf:
        return conf[key]

    # follow the common path
    try:
        for p in common:
            conf = conf[p]
            if key in conf:
                default = conf[key]
    except Exception:
        return default

    # try all paths until a value is found
    value = SENTINEL
    for path in paths:
        c = conf

        try:
            for p in path:
                c = c[p]
                if key in c:
                    value = c[key]
        except Exception:
            pass

        if value is not SENTINEL:
            return value
    return default