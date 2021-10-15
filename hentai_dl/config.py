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
from . import util

log = logging.getLogger("config")


_config = {}

if WINDOWS:
    _default_configs = [
        r"%APPDATA%\hentai-dl\config.json",
        r"%USERPROFILE%\hentai-dl\config.json",
        r"%USERPROFILE%\hentai-dl.conf",
    ]
else:
    _default_configs = [
        "/etc/hentai-dl.conf",
        "${XDG_CONFIG_HOME}/hentai-dl/config.json" if os.environ.get("XDG_CONFIG_HOME") else "${HOME}/.config/hentai-dl/config.json",
        "${HOME}/.hentai-dl.conf",
    ]


if getattr(sys, "frozen", False):
    # look for config file in PyInstaller executable directory (#682)
    _default_configs.append(os.path.join(os.path.dirname(sys.executable), "hentai-dl.conf",))

def load(files=None, strict=False, fmt="json"):
    """Load JSON configuration files"""
    if fmt == "yaml":
        try:
            import yaml
            parsefunc = yaml.safe_load

        except ImportError:
            log.error("Could not import 'yaml' module")
            return

    else:
        parsefunc = json.load

    for path in files or _default_configs:
        path = util.expand_path(path)

        try:
            with open(path, encoding="utf-8") as file:
                confdict = parsefunc(file)

        except OSError as exc:
            if strict:
                log.error(exc)
                sys.exit(1)

        except Exception as exc:
            log.warning("Could not parse '%s': %s", path, exc)
            if strict:
                sys.exit(2)
                
        else:
            if not _config:
                _config.update(confdict)
            else:
                util.combine_dict(_config, confdict)

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



def set(path, key, value, *, conf=_config):
    """Set the value of property 'key' for this session"""
    for p in path:
        try:
            conf = conf[p]
        except KeyError:
            conf[p] = conf = {}
    conf[key] = value


def setdefault(path, key, value, *, conf=_config):
    """Set the value of property 'key' if it doesn't exist"""
    for p in path:
        try:
            conf = conf[p]
        except KeyError:
            conf[p] = conf = {}
    return conf.setdefault(key, value)


def unset(path, key, *, conf=_config):
    """Unset the value of property 'key'"""
    try:
        for p in path:
            conf = conf[p]
        del conf[key]
    except Exception:
        pass
