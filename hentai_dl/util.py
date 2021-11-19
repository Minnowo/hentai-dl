# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

try:
    from urllib.parse import unquote
except ImportError:
    from urlparse import unquote

from genericpath import exists
from functools import partial
from random import uniform
import sys
import os.path
import unicodedata

WINDOWS = (os.name == "nt")
SENTINEL = object()

LANGUAGEG_CODE_MAP = {
    "ar": "Arabic",
    "bg": "Bulgarian",
    "ca": "Catalan",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "fi": "Finnish",
    "fr": "French",
    "he": "Hebrew",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ms": "Malay",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sv": "Swedish",
    "th": "Thai",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "zh": "Chinese",
}

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

def clamp(value, min, max):
    if value > max:
        return max 
    if value < min:
        return min 
    return value


def build_duration_func(duration, min=0.0):
    if not duration:
        return None

    try:
        lower, upper = duration
    except TypeError:
        pass
    else:
        return partial(
            uniform,
            lower if lower > min else min,
            upper if upper > min else min,
        )

    return partial(
        identity, 
        duration if duration > min else min
        )



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

def enumerate_reversed(iterable, start=0, length=None):
    """Enumerate 'iterable' and return its elements in reverse order"""
    start -= 1
    if length is None:
        length = len(iterable)
    return zip(
        range(length - start, start, -1),
        reversed(iterable),
    )

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # No resource path found, returns path relative to current file
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

def add_nameext_from_url(url, data = None):
    """Adds 'filename' : filename, 'extension' : extension to the given dict"""
    if data is None:
        data = {}

    filename = unquote(get_url_filename(url))

    name, _, ext = filename.rpartition(".")

    if name and len(ext) <= 16:
        if "filename" not in data:
            data["filename"] = name

        if "extension" not in data:
            data["extension"] = ext.lower()

    else:
        if "filename" not in data:
            data["filename"] = filename
            
        if "extension" not in data:
            data["extension"] = ""

    return data

def get_url_filename(url : str):
    """Gets a file name from the given url"""
    try:
        return url.split("?")[0].rsplit("/", 1)[-1]
    except (TypeError, AttributeError):
        return ""


def get_url_ext(url, includeDot = False):
    """Gets a file extension from the given url"""
    ext = get_url_filename(url).rsplit(".", 1)

    if len(ext) < 2:
        return ""

    ext = ext[-1]

    if includeDot:
        return "." + ext.lower().strip()
    return ext.lower().strip()


def code_to_language(code, default=None):
    """Map an ISO 639-1 language code to its actual name"""
    return LANGUAGEG_CODE_MAP.get((code or "").lower(), default)


def language_to_code(lang, default=None):
    """Map a language name to its ISO 639-1 code"""
    if lang is None:
        return default
    lang = lang.capitalize()
    for code, language in LANGUAGEG_CODE_MAP.items():
        if language == lang:
            return code
    return default
