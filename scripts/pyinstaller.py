# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.


"""Build a standalone executable using PyInstaller"""

import PyInstaller.__main__
import util
import os

VIEWER_BASE = util.path("hentai_dl\\viewer\\")

PyInstaller.__main__.run([
    "--onefile",
    "--console",
    "--name", "hentai-dl." + ("exe" if os.name == "nt" else "bin"),
    "--add-data", VIEWER_BASE+"*;viewer\\",
    "--add-data", VIEWER_BASE+"default\\*;viewer\\default\\",
    "--add-data", VIEWER_BASE+"minimal\\*;viewer\\minimal\\",
    "--additional-hooks-dir", util.path("scripts"),
    "--distpath", util.path("dist"),
    "--workpath", util.path("build"),
    "--specpath", util.path("build"),
    util.path("hentai_dl", "__main__.py"),
])