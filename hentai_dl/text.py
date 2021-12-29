# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import datetime
import json 
import re
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



class NameFormatter():
    """Formats the given string with the given dict key values"""

    EASE_OF_LIFE_MAP = {
        "i" : "gallery_id",
        "mi" : "media_id",
        "t" : "title",
        "te" : "title_en",
        "tj" : "title_ja",
        "a" : "artist",
        "d" : "date",
        "l" : "language"
    }

    MATCH_SUB = re.compile(r"\$\[([a-zA-Z]+)\]")

    def __init__(self, string, dict) -> None:
        
        self.og_string = string 
        self.dict = dict 

    
    def get_formatted_name(self):

        # find all matches of $['some text']
        keys = [i.strip() for i in self.MATCH_SUB.findall(self.og_string) if i]

        new_string = self.og_string

        for i in keys:
            
            # check if any of the matches are in the EASE_OF_LIFE_MAP dict and then index the given dict
            value = self.dict.get(self.EASE_OF_LIFE_MAP.get(i, i), None)

            # combine lists using -
            if hasattr(value, '__iter__'):
                value = "-".join(list(value))

            # just remove the match if nothing is found 
            if value is None:
                new_string = self.MATCH_SUB.sub("", new_string, 1)
                continue 
            
            # else just sub it with the value found in the dict 
            new_string = self.MATCH_SUB.sub(str(value), new_string, 1)

        return new_string

