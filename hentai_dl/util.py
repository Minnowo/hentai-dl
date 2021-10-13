# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from genericpath import exists
import sys
import os.path
import unicodedata

WINDOWS = (os.name == "nt")
SENTINEL = object()


class EAWCache(dict):

    def __missing__(self, key):
        width = self[key] = 2 if unicodedata.east_asian_width(key) in "WF" else 1
        return width


def shorten_string(txt : str, limit : int, sep = "…") -> str:
    """Limit width of 'txt'; assume all characters have a width of 1"""

    if len(txt) <= limit:
        return txt

    limit -= len(sep)
    return txt[:limit // 2] + sep + txt[-((limit+1) // 2):]



def shorten_string_eaw(txt, limit, sep="…", cache=EAWCache()):
    """Limit width of 'txt'; check for east-asian characters with width > 1"""
    char_widths = [cache[c] for c in txt]
    text_width = sum(char_widths)

    if text_width <= limit:
        # no shortening required
        return txt

    limit -= len(sep)
    if text_width == len(txt):
        # all characters have a width of 1
        return txt[:limit // 2] + sep + txt[-((limit+1) // 2):]

    # wide characters
    left = 0
    lwidth = limit // 2
    while True:
        lwidth -= char_widths[left]
        if lwidth < 0:
            break
        left += 1

    right = -1
    rwidth = (limit+1) // 2 + (lwidth + char_widths[left])
    while True:
        rwidth -= char_widths[right]
        if rwidth < 0:
            break
        right -= 1

    return txt[:left] + sep + txt[right+1:]

def combine_dict(a, b):
    """Recursively combine the contents of 'b' into 'a'"""
    for key, value in b.items():
        if key in a and isinstance(value, dict) and isinstance(a[key], dict):
            combine_dict(a[key], value)
            
        else:
            a[key] = value
    return a

def parse_bytes(value, default=0, suffixes="bkmgtp"):
    """Convert a bytes-amount ("500k", "2.5M", ...) to int"""
    try:
        last = value[-1].lower()
    except (TypeError, KeyError, IndexError):
        return default

    if last in suffixes:
        mul = 1024 ** suffixes.index(last)
        value = value[:-1]
    else:
        mul = 1

    try:
        return round(float(value) * mul)
    except ValueError:
        return default


def parse_int(value, default=0):
    """Convert 'value' to int"""
    if not value:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def identity(x):
    """Returns its argument"""
    return x


def expand_path(path):
    """Expand environment variables and tildes (~)"""
    if not path:
        return path

    if not isinstance(path, str):
        path = os.path.join(*path)

    return os.path.expandvars(os.path.expanduser(path))


def list_dirs(path : str) -> list:
    """List directories in the given directory"""
    current_directory = os.getcwd()
    try:
        os.chdir(path)
        return next(os.walk('.'))[1]
    finally:
        os.chdir(current_directory)


def create_directory_from_file_name(path : str) -> bool:
    """
    Creates a directory from the file path.

    Returns: 
        True if the path was created
        
        False if path was not created
    """
    return create_directory(os.path.dirname(path))


def create_directory(path : str) -> bool:
    """
    Creates the given directory.

    Returns: 
        True if the path was created
        
        False if path was not created
    """
    try:
        os.makedirs(expand_path(path), exist_ok=True)
    except OSError:
        pass
    return os.path.isdir(path)


def remove_file(path : str) -> bool:
    """
    Deletes the given file.

    Returns: 
        True if the file was removed
        
        False if file was not removed
    """
    try:
        os.unlink(path)
    except OSError:
        pass
    return not os.path.exists(path)


def remove_directory(path : str) -> bool:
    """
    Deletes the given directory.

    Returns: 
        True if the path was removed

        False if path was not removed
    """
    try:
        os.rmdir(path)
    except OSError:
        pass
    return not os.path.isdir(path)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # No resource path found, returns path relative to current file
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)