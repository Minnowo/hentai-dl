# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import logging

from . import extractor
from . import downloader
from . import exceptions
from . import output

class Job():

    def __init__(self, extr, parent=None) -> None:
        
        if isinstance(extr, str):
            extr = extractor.find(extr)

        if not extr:
            raise exceptions.NoExtractorError()

        self.extractor = extr
        self.pathfmt = None
        self.kwdict = {}
        self.status = 0
        self.url_key = extr.config("url-metadata")

        self._logger_extra = {
            "job"      : self,
            "extractor": extr,
            "path"     : output.PathfmtProxy(self),
            "keywords" : output.KwdictProxy(self),
        }
        extr.log = self._wrap_logger(extr.log)
        extr.log.debug("Using %s for '%s'", extr.__class__.__name__, extr.url)

        # data from parent job
        if parent:
            pextr = parent.extractor

            # transfer (sub)category
            if pextr.config("category-transfer", pextr.categorytransfer):
                extr._cfgpath = pextr._cfgpath
                extr.category = pextr.category
                extr.subcategory = pextr.subcategory

            # reuse connection adapters
            extr.session.adapters = pextr.session.adapters

        # user-supplied metadata
        kwdict = extr.config("keywords")
        if kwdict:
            self.kwdict.update(kwdict)

    
    def get_logger(self, name):
        """Gets a logger with the given name"""
        return self._wrap_logger(logging.getLogger(name))


    def _wrap_logger(self, logger):
        return output.LoggerAdapter(logger, self._logger_extra)


    def write_unsupported_url(self, url):
        """Let the user know the url is unsupported"""
        if self.logger:
            self.logger.info("Unsupported url: %s", url)



class DownloaderJob(Job):
    
    def __init__(self, url, parent = None) -> None:
        Job.__init__(self, url, parent)

        self.logger = self.get_logger("download")
        self.downloaders = {}
        self.outpur_directory = ""
        self.out = output.select("terminal")



    def get_file_name(self):
        pass


    def handle_url(self, url):
        pass

    def handle_directory(self, directory):
        pass 


    def download(self, url : str, path : str):
        """Download the given url, save to the given path"""

        downloader = self.get_downloader_from_url(url)

        if not downloader:
            self.write_unsupported_url(url)
            return False

        try:
            return downloader.download(url, path)
        except OSError as ex:
            self.logger.warning("%s: %s", ex.__class__.__name__, ex)
            return False


    def get_downloader_from_scheme(self, scheme : str):
        """Get a downloader for the given scheme"""

        # check for existing downloaders of the same scheme
        cls = self.downloaders.get(scheme, None)

        if cls:
            return cls 

        # couldn't find any existing downloader
        # get a new downloader for the given scheme
        cls = downloader.find(scheme)

        if cls:
            # downloader found, create instance and add to cache
            instance = cls(self)
            
            if scheme in ("http", "https"):
                self.downloaders["http"] = instance
                self.downloaders["https"] = instance
            else:
                self.downloaders[scheme] = instance

            return instance

        return None
        

    def get_downloader_from_url(self, url : str):
        """Get a downloader for the given url"""

        scheme = urlparse(url)
        return self.get_downloader_from_scheme(scheme)

