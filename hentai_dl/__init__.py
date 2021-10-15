# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys 
import platform
from . import output
from . import option
from . import config
from .downloader import http
from .job import DownloaderJob
from .meta import __version__


def main():

    if sys.stdout and sys.stdout.encoding.lower() != "utf-8":
        output.replace_std_streams()

    parser = option.build_parser()
    args = parser.parse_args()
    log = output.initialize_logging(args.loglevel)

    log.debug("Version %s%s", __version__)
    log.debug("Python %s - %s", platform.python_version(), platform.platform())
    log.warning("uwu")
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
        config.set(*opts)

    dl = DownloaderJob("https://nhentai.net/g/375952/1/")
    dl.run()
    # dl.download("https://i.nhentai.net/galleries/2034672/1.png", "D:\\Ωtmp\\test.png")

    print(args.options)
    print("all done")