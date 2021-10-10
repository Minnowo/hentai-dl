# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


"""Filesystem path handling"""

import os.path
import shutil

from re import compile

from . import util
from .util import WINDOWS

class PathFormat:
    EXTENSION_MAP = {
        "jpeg": "jpg",
        "jpe" : "jpg",
        "jfif": "jpg",
        "jif" : "jpg",
        "jfi" : "jpg",
    }

    RESTRICT_MAP = {
        "auto" : "\\\\|/<>:\"?*" if WINDOWS else "/",
        "unix" : "/",
        "windows" : "\\\\|/<>:\"?*",
        "ascii" : "^0-9A-Za-z_."
    }

    STRIP_MAP = {
        "auto" : ". " if WINDOWS else "",
        "unix" : "",
        "windows" : ". "
    }

    def __init__(self, directory = "", filename = "", extension = "", replace = "_") -> None:
        
        self.directory = ""
        self.filename = ""
        self.extension = ""
        self.path = ""
        self.temp_path = ""
        self.replace = replace

        # the regex function that will replace characters
        self._replace = compile(f"[{self.RESTRICT_MAP['auto']}]").sub

        self.set_directory(directory)
        self.set_filename(filename)
        self.set_extension(extension)

    def clean(self, path : str):
        """Removes illegal characters and strips the string"""

        if not path:
            return path

        strip = self.STRIP_MAP["auto"]

        if os.altsep and os.altsep in path:
            path = path.replace(os.altsep, os.sep)

        # remove empty strings from the split
        spl = list(filter(None, path.split(os.sep)))
        tmp = []

        if WINDOWS:
            # C: D: E: F:
            # don't want to replace the : in drive letters 
            # so if the start of the path is a drive remove it
            if spl[0].find(":") == 1:
                tmp.append(spl[0] + os.sep)
                del spl[0]

        for i in spl:
            # replace illegal characters
            i = self._replace(self.replace, i)
            tmp.append(i.rstrip(strip))
        
        return util.expand_path(os.path.join(*tmp))

    def _build_directory(self):
        """Build directory path and create it if necessary"""

        if not WINDOWS:
            return

        # Enable longer-than-260-character paths on Windows
        if not self.directory.startswith("\\\\?\\"):
            directory = "\\\\?\\" + os.path.abspath(self.directory)

            # abspath() in Python 3.7+ removes trailing path separators (#402)
            if directory[-1] != os.sep:
                directory += os.sep

            self.directory = directory
            util.create_directory(directory)


    def _build_path(self):
        """Builds the path""" 

        self._build_directory()
        self.path = os.path.join(self.directory, f"{self.filename}.{self.extension}")
        self.temp_path = self.path + ".part"


    def set_filename(self, name : str, update_extension = False, *, build_path = True):
        """Updates the filename"""

        tmp = self.clean(name).rsplit(os.sep)

        if len(tmp) > 1:
            self.append_directory(tmp[0], build_path = False)
            name = tmp[1]
        else:
            name = tmp[0]

        if update_extension:
            ext = name.rsplit(".")

            if len(ext) > 1:
                self.set_extension(ext[1], build_path=False)

        self.filename = name

        if build_path:
            self._build_path()


    def set_extension(self, ext, *, build_path = True):
        """Updates the extension"""

        self.extension = self.EXTENSION_MAP.get(ext, self.clean(ext))

        if build_path:
            self._build_path()


    def append_directory(self, directory, *, build_path = True):
        """Append the given directory onto the current directory"""

        if isinstance(directory, str):
            dir = self.clean(directory)

        else:
            dir = self.clean(os.path.join(*directory))
        
        self.directory += dir 

        if build_path:
            self._build_path()


    def set_directory(self, directory, *, build_path = True):
        """Sets the directory"""

        if isinstance(directory, str):
            dir = self.clean(directory)

        else:
            dir = self.clean(os.path.join(*directory))
        
        self.directory = dir

        if build_path:
            self._build_path()
        else:
            self._build_directory()
    

    def finalize(self, *, delete = False):
        """Move tempfile to its target location"""

        if delete and self.temp_path and os.path.exists(self.temp_path):
            util.remove_file(self.temp_path)
            return

        if self.temp_path != self.path:
            # Move temp file to its actual location
            try:
                os.replace(self.temp_path, self.path)
            except OSError:
                shutil.copyfile(self.temp_path, self.path)
                os.unlink(self.temp_path)

    def __repr__(self) -> str:
        return self.path
