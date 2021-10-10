# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

__author__ = "Alice Nyaa"
__license__ = "GPLv3"
__maintainer__ = "Minnowo"

"""
Namespace(
    abort=None, 
    archive=None, 
    cfgfiles=None, 
    clear_cache=None, 
    cookies=None, 
    download=None, 
    inputfiles=None, 
    list_extractors=False, 
    list_modules=False, 
    list_urls=None, 
    load_config=True, 
    logfile=None, 
    loglevel=20, 
    mtime=None, 
    netrc=None, 
    options=[((), 'base-directory', 'D:/')], part=None, 
    password=None, postprocessors=None, proxy=None, rate=None, 
    retries=None, skip=None, sleep=None, terminate=None, timeout=None, 
    unsupportedfile=None, urls=[], username=None, verify=None, yamlfiles=None, 
    **{'base-directory': None, 'chapter-filter': None, 'chapter-range': None, 
    'filesize-max': None, 'filesize-min': None, 'image-filter': None, 'image-range': None, 'write-pages': None})
"""

def main():

    from .path import PathFormat

    name = PathFormat("D://Programming//python", "test///uwu", "py")
    print(name)
    name.set_directory("tmp//uwu//")
    print(name)