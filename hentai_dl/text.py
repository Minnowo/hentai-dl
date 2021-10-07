# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.



def parse_bytes(value, default = 0, suffixes = "bkmgtp"):
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