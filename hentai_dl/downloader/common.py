# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.

"""Common classes and constants used by downloader modules."""

from .. import config


class DownloaderBase():
    """Base class for downloaders"""
    scheme = ""

    def __init__(self, job):
        self.out = job.out
        self.session = job.extractor.session
        
        self.log = job.get_logger("downloader." + self.scheme)


    def config(self, key, default=None):
        """Interpolate downloader config value for 'key'"""
        return config.interpolate(("downloader", self.scheme), key, default)


    def download(self, url, pathfmt):
        """Write data from 'url' into the file specified by 'pathfmt'"""
