# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


MIME_TYPES = {
    "image/jpeg"    : "jpg",
    "image/jpg"     : "jpg",
    "image/png"     : "png",
    "image/gif"     : "gif",
    "image/bmp"     : "bmp",
    "image/x-bmp"   : "bmp",
    "image/x-ms-bmp": "bmp",
    "image/webp"    : "webp",
    "image/svg+xml" : "svg",
    "image/ico"     : "ico",
    "image/icon"    : "ico",
    "image/x-icon"  : "ico",
    "image/vnd.microsoft.icon" : "ico",
    "image/x-photoshop"        : "psd",
    "application/x-photoshop"  : "psd",
    "image/vnd.adobe.photoshop": "psd",

    "video/webm": "webm",
    "video/ogg" : "ogg",
    "video/mp4" : "mp4",

    "audio/wav"  : "wav",
    "audio/x-wav": "wav",
    "audio/webm" : "webm",
    "audio/ogg"  : "ogg",
    "audio/mpeg" : "mp3",

    "application/zip"  : "zip",
    "application/x-zip": "zip",
    "application/x-zip-compressed": "zip",
    "application/rar"  : "rar",
    "application/x-rar": "rar",
    "application/x-rar-compressed": "rar",
    "application/x-7z-compressed" : "7z",

    "application/pdf"  : "pdf",
    "application/x-pdf": "pdf",
    "application/x-shockwave-flash": "swf",

    "application/ogg": "ogg",
    "application/octet-stream": "bin",
}


# https://en.wikipedia.org/wiki/List_of_file_signatures
FILE_SIGNATURES = {
    "jpg" : b"\xFF\xD8\xFF",
    "png" : b"\x89PNG\r\n\x1A\n",
    "gif" : (b"GIF87a", b"GIF89a"),
    "bmp" : b"BM",
    "webp": b"RIFF",
    "svg" : b"<?xml",
    "ico" : b"\x00\x00\x01\x00",
    "cur" : b"\x00\x00\x02\x00",
    "psd" : b"8BPS",
    "webm": b"\x1A\x45\xDF\xA3",
    "ogg" : b"OggS",
    "wav" : b"RIFF",
    "mp3" : (b"\xFF\xFB", b"\xFF\xF3", b"\xFF\xF2", b"ID3"),
    "zip" : (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    "rar" : b"\x52\x61\x72\x21\x1A\x07",
    "7z"  : b"\x37\x7A\xBC\xAF\x27\x1C",
    "pdf" : b"%PDF-",
    "swf" : (b"CWS", b"FWS"),
    # check 'bin' files against all other file signatures
    "bin" : b"\x00\x00\x00\x00\x00\x00\x00\x00",
}
