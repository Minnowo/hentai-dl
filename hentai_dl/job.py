# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import logging
import multiprocessing
import signal
from time import sleep
from concurrent.futures import ThreadPoolExecutor

from hentai_dl.extractor.message import Message

from . import extractor
from . import downloader
from . import exceptions
from . import output
from .path import PathFormat
from . import config

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
            # "path"     : output.PathfmtProxy(self),
            # "keywords" : output.KwdictProxy(self),
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
        self.outpur_directory = "/mnt/d/Ωtmp/"
        self.out = output.select("terminal")
        self.cancled = False


    def run(self):

        status = 0
        log = self.extractor.log

        try:
            with ThreadPoolExecutor(max_workers=config.get((), "thread-count", 5)) as exec:
                
                results = []
                for message in self.extractor:
                    
                    if message[0] == Message.Url:
                        results.append(exec.submit(self.handle_url, message[1], message[2]))

                    elif message[0] == Message.Directory:
                        self.handle_directory(message[1])

                    # something to block the main thread to avoid thread.join
                    # this allows for the KeyboardInterrupt to takeplace
                    while(any([i.running() for i in results])):
                        sleep(1)

        except KeyboardInterrupt:
            print("keyboard interrupt")

            self.cancled = True
            # cancel all downloaders that might be running
            # this quickly ends the threads allowing them to properly join
            for scheme, dl in self.downloaders.items():
                dl.cancel()

            raise 

        except exceptions.StopExtraction as exc:
            if exc.message:
                log.error(exc.message)
            status |= exc.code

        except exceptions.TerminateExtraction:
            raise

        except exceptions.GalleryDLException as exc:
            log.error("%s: %s", exc.__class__.__name__, exc)
            status |= exc.code

        except OSError as exc:
            log.error("Unable to download data:  %s: %s", exc.__class__.__name__, exc)
            log.debug("", exc_info=True)
            status |= 128

        except Exception as exc:
            log.error(("An unexpected error occurred: %s - %s. "
                       "Please run gallery-dl again with the --verbose flag, "
                       "copy its output and report this issue on "
                       "https://github.com/mikf/gallery-dl/issues ."),
                      exc.__class__.__name__, exc)
            log.debug("", exc_info=True)
            status |= 1

        except BaseException:
            status |= 1
            raise
        
        return status
                

    def get_file_name(self):
        pass


    def handle_url(self, url, file_meta_dict):
        """Formats and downloads the given url"""

        if self.cancled:
            return

        if not file_meta_dict:
            print("not metadict will not download")
            return

        name = file_meta_dict.get("filename")
        ext  = file_meta_dict.get("extension")

        out_path = PathFormat()
        out_path.set_directory(self.outpur_directory, build_path=False)
        out_path.set_filename(name, build_path=False)
        out_path.set_extension(ext)

        # print(out_path)
        return self.download(url, out_path)


    def handle_directory(self, directory):
        """Formats and creates the given directory"""


    def download(self, url : str, path):
        """Download the given url, save to the given path"""

        downloader = self.get_downloader_from_url(url)
        
        if not downloader:
            self.write_unsupported_url(url)
            return False

        if isinstance(path, str):
            path = PathFormat.from_path(path)

        try:
            if downloader.download(url, path):
                path.finalize()
                return True 
            return False
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
        return self.get_downloader_from_scheme(scheme.scheme)

