# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys 
import logging

from . import output
from . import option
from . import config
from . import exceptions
from .downloader import http
from .job import DownloaderJob
from .meta import __version__
from .util import clamp

"""
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
netrc=None, 
options=[], 
output_directory=None, 
part=None, 
password=None, 
postprocessors=None, 
proxy=None, 
rate=None, 
retries=None, 
skip=None, 
sleep=None, 
thread_count=5, 
timeout=None, 
unsupportedfile=None, 
urls=['https://nhentai.net/g/177013'], 
use_api=False, 
username=None, 
yamlfiles=None, 
**{
    'filesize-max': None, 
    'filesize-min': None, 
    'image-range': None, 
    'write-pages': None
    }
"""

def progress(urls, pformat):
    """Wrapper around urls to output a simple progress indicator"""
    if pformat is True:
        pformat = "[{current}/{total}] {url}"

    pinfo = {"total": len(urls)}

    for pinfo["current"], pinfo["url"] in enumerate(urls, 1):
        print(pformat.format_map(pinfo), file=sys.stderr)
        yield pinfo["url"]


def parse_inputfile(file, log):
    """Filter and process strings from an input file.

    Lines starting with '#' and empty lines will be ignored.
    """

    for line in file:
        line = line.strip()

        if not line or line[0] == "#":
            # empty line or comment
            continue

        yield line

def main():

    if sys.stdout and sys.stdout.encoding.lower() != "utf-8":
        output.replace_std_streams()

    parser = option.build_parser()
    args = parser.parse_args()
    log = output.initialize_logging(args.loglevel)
    # output.configure_logging(args.loglevel)
    # print(**args)
    # return
    # log.warning("uwu")
    # configuration
    if args.load_config:
        config.load()
        
    if args.cfgfiles:
        config.load(args.cfgfiles, strict=True)

    if args.yamlfiles:
        config.load(args.yamlfiles, strict=True, fmt="yaml")

    # if args.postprocessors:
    #     config.set((), "postprocessors", args.postprocessors)

    # if args.abort:
    #     config.set((), "skip", "abort:" + str(args.abort))

    # if args.terminate:
    #     config.set((), "skip", "terminate:" + str(args.terminate))
    

    for opts in args.options:
        print(opts)
        config.set(*opts)
    # return
    # config.set(("runtime",), "threads", clamp(args.thread_count, 0, 32))
    # config.set(("runtime",), "use_api", args.use_api)

    output.configure_logging(args.loglevel)

    if args.loglevel <= logging.DEBUG:
        from platform import python_version, platform

        log.debug("Version %s%s", __version__)
        log.debug("Python %s - %s", python_version(), platform())


    if not args.urls and not args.inputfiles:
        parser.error(
            "The following arguments are required: URL\n"
            "Use 'hentai-dl --help' to get a list of all options.")


    urls = args.urls
    if args.inputfiles:
        for inputfile in args.inputfiles:
            try:
                if inputfile == "-":
                    if sys.stdin:
                        urls += parse_inputfile(sys.stdin, log)

                    else:
                        log.warning("input file: stdin is not readable")

                else:
                    with open(inputfile, encoding="utf-8") as file:
                        urls += parse_inputfile(file, log)

            except OSError as exc:
                log.warning("input file: %s", exc)

    pformat = config.get(("output",), "progress", True)
    if pformat and len(urls) > 1 and args.loglevel < logging.ERROR:
        urls = progress(urls, pformat)

    jobtype = DownloaderJob
    status = 0
    for url in urls:
        try:
            log.debug("Starting %s for '%s'", jobtype.__name__, url)

            status |= jobtype(url).run()

        except KeyboardInterrupt:
            sys.exit("\nKeyboardInterrupt")

        except exceptions.TerminateExtraction:
            pass

        except exceptions.NoExtractorError:
            log.error("No suitable extractor found for '%s'", url)

    return status
    # with open("/mnt/d/Ωtmp/test.txt", "w+b") as f:
    #     f.write("test")
    # return
    dl = DownloaderJob("https://nhentai.net/g/375952/1/")
    # dl = DownloaderJob("https://doujins.com/hentai-magazine-chapters/haguruma-55114")
    dl.run()
    # dl.download("https://i.nhentai.net/galleries/2034672/1.png", "D:\\Ωtmp\\test.png") 

    print(args.options)
    print("all done")