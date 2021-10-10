# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from . import option
from .downloader import http
from .job import DownloaderJob


def main():

    parser = option.build_parser()
    args = parser.parse_args()

    dl = http.__downloader__(DownloaderJob("https://nhentai.net/g/375952/1/"))


    print(args.options)
    print("all done")