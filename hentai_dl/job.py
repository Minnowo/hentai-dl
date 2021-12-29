# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import logging
import os.path

from time import sleep
from concurrent.futures import ThreadPoolExecutor

from hentai_dl.extractor.message import Message

from . import extractor
from . import downloader
from . import exceptions
from . import output
from .path import PathFormat
from . import config
from . import text
from . import util

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
        self.output_directory = config.get((), "output-directory", False) 
        self.download_directory = self.output_directory
        self.out = output.select("terminal")
        self.cancled = False
        self.format_directory = False
        self.handling_queue = False 

        if not isinstance(self.output_directory, str):
            self.format_directory = True 
            self.output_directory = "hentai-dl"

        self.no_dl = not config.get((),"download", True) 
        self.skip = config.get((), "skip", True)
        self.part_files = config.get((), "part", True)

    def run(self):

        status = 0
        log = self.extractor.log

        try:
            with ThreadPoolExecutor(max_workers=config.get((), "thread-count", 1)) as exec:
                
                results = []
                for message in self.extractor:
                    
                    # to correct the output directory if anything is specified
                    self.handling_queue = message[0] == Message.Queue

                    if message[0] == Message.Url:
                        results.append(exec.submit(self.handle_url, message[1], message[2]))

                    elif message[0] == Message.Directory:
                        self.handle_directory(message[1])

                    # this if statement is kinda dumb but it works so whatever
                    elif message[0] == Message.Queue:

                        for _message in message[1]:
                            if _message[0] == Message.Url:
                                results.append(exec.submit(self.handle_url, _message[1], _message[2]))

                            elif _message[0] == Message.Directory:
                                self.handle_directory(_message[1])

                            else:
                                # cause this is using iteration instead of recursion to handle queue
                                # not gonna make it support a queue of a queue unless i change this to a recursive function
                                # this shouldn't ever trigger unless i add an extractor that does this tho
                                raise Exception("Does not support recursive downloading of galleries, someone has added a Queue extractor class which returns Queues")

                        try:
                            
                            # need to block all threads here to prevent a Message.Directory
                            # from changing the download path to a different place while files are still downloading
                            # for the specific gallery 
                            while(any([i.running() for i in results])):
                                sleep(1)

                            while(any([not i.done() for i in results])):
                                sleep(1)

                        except KeyboardInterrupt:
                            print("keyboard interrupt")

                            self.cancled = True
                            # cancel all downloaders that might be running
                            # this quickly ends the threads allowing them to properly join
                            for scheme, dl in self.downloaders.items():
                                dl.cancel()

                            raise  
                try:
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
                       "Please run hentai-dl again with the --verbose flag, "
                       "copy its output and report this issue on "
                       "https://github.com/mikf/gallery-dl/issues ."), exc.__class__.__name__, exc)
            log.debug("", exc_info=True)
            status |= 1

        except BaseException:
            status |= 1
            raise
        
        return status


    def handle_url(self, url, file_meta_dict):
        """Formats and downloads the given url"""

        if self.cancled:
            return

        if not file_meta_dict:
            print("no metadict will not download")
            return

        name = file_meta_dict.get("filename")
        ext  = file_meta_dict.get("extension")

        out_path = PathFormat(use_temp_path = self.part_files)
        out_path.set_directory(self.download_directory, build_path=False)
        out_path.set_filename(name, build_path=False)
        out_path.set_extension(ext)

        if self.skip and os.path.isfile(out_path.path):
            self.logger.info(f"file already exists for {url}. skipping")
            return

        return self.download(url, out_path)


    def handle_directory(self, directory):
        """Formats and creates the given directory"""

        output_name_format = config.get((), "output-name-format", None)

        # if not name format is specified, default to the gallery title
        if output_name_format is None:
            output_name_format = directory.get("title", None)

            # if there is somehow no 'title' key in the given dict, 
            # generate a random number and just use hex cause why not
            if output_name_format is None:
                import random 
                output_name_format = hex(str(random.randint(1000, 10000))).upper()

        else:
            output_name_format = text.NameFormatter(output_name_format, directory).get_formatted_name()

        if self.format_directory:
            self.download_directory = os.path.join(self.output_directory,  self.extractor.category, output_name_format)

        # cuase i haven't added the format command or whatever that makes a directory in the output directory formated per gallery
        # so use the gallery title to prevent duplicates even tho it might cause them anyway 
        elif self.handling_queue:
            self.download_directory = os.path.join(self.output_directory, output_name_format)
        
        else:
            # if the user specified a name format apply it, otherwise don't add the directory['title'] to the output
            if isinstance(config.get((), "output-name-format", False), str):
                self.download_directory = os.path.join(self.output_directory, output_name_format)
                
            else:
                self.download_directory = self.output_directory

        self.logger.info(f"output directory: {self.download_directory}")

        if "metadata" in config.get((), "postprocessors", []):
            meta = os.path.join(self.download_directory, config.get(("internal",), "metadata_filename"))
            
            self.logger.info(f"writing metadata: {meta}")

            text.write_json(meta, directory)


    def download(self, url : str, path):
        """Download the given url, save to the given path"""

        if self.no_dl:
            self.logger.info(f"downloading: {url}")
            return True 

        downloader = self.get_downloader_from_url(url)
        
        if not downloader:
            self.write_unsupported_url(url)
            return False

        if isinstance(path, str):
            path = PathFormat.from_path(path, self.part_files)

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

