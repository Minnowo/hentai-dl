# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import datetime
import json 
from . import util 

def write_json(path, data, indent = 3):
    
    if not util.create_directory_from_file_name(path):
        return

    try:
        with open(path, "w") as writer:
            json.dump(data, writer, indent=indent)

    except:
        pass 

def parse_range(input):
    pass 


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



def parse_datetime(date_string, format="%Y-%m-%dT%H:%M:%S%z", utcoffset=0):
    """Create a datetime object by parsing 'date_string'"""
    try:
        if format.endswith("%z") and date_string[-3] == ":":
            # workaround for Python < 3.7: +00:00 -> +0000
            ds = date_string[:-3] + date_string[-2:]
        else:
            ds = date_string
        d = datetime.datetime.strptime(ds, format)
        o = d.utcoffset()
        if o is not None:
            # convert to naive UTC
            d = d.replace(tzinfo=None, microsecond=0) - o
        else:
            if d.microsecond:
                d = d.replace(microsecond=0)
            if utcoffset:
                # apply manual UTC offset
                d += datetime.timedelta(0, utcoffset * -3600)
        return d
    except (TypeError, IndexError, KeyError):
        return None
    except (ValueError, OverflowError):
        return date_string