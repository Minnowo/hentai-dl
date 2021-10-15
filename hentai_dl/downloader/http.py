# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


"""Downloader module for http:// and https:// URLs"""

import time
import mimetypes
from requests.exceptions import RequestException, ConnectionError, Timeout
from ssl import SSLError

from .. import text, util, exceptions
from .common import DownloaderBase
from .const import MIME_TYPES, FILE_SIGNATURES

OpenSSLError = SSLError

class HttpDownloader(DownloaderBase):
    scheme = "http"


    def __init__(self, job):
        DownloaderBase.__init__(self, job)
        extractor = job.extractor

        self.chunk_size = 16384
        self.downloading = False

        self.cancled = False
        self.adjust_extension   = self.config("adjust-extensions", True)
        self.progress           = self.config("progress", 3.0)
        self.headers            = self.config("headers")
        self.min_file_size      = self.config("filesize-min")
        self.max_file_size      = self.config("filesize-max")
        self.retries            = self.config("retries", extractor._retries)
        self.timeout            = self.config("timeout", extractor._timeout)
        self.verify             = self.config("verify", extractor._verify)
        self.rate               = self.config("rate")

        if self.retries < 0:
            self.retries = float("inf")

        if self.min_file_size:
            self.min_file_size = util.parse_bytes(self.min_file_size)

            if not self.min_file_size:
                self.log.warning("Invalid minimum file size (%r)", self.min_file_size)

        if self.max_file_size:
            self.max_file_size = util.parse_bytes(self.max_file_size)
            
            if not self.max_file_size:
                self.log.warning("Invalid maximum file size (%r)", self.max_file_size)
            

        if self.rate:
            rate = util.parse_bytes(self.rate)

            if rate:
                if rate < self.chunk_size:
                    self.chunk_size = rate

                self.rate = rate
                self.receive = self._receive_rate

            else:
                self.log.warning("Invalid rate limit (%r)", self.rate)

        if self.progress is not None:
            self.receive = self._receive_rate

    def cancel(self):
        """Cancels downloads"""
        self.cancled = True

    def download(self, url, pathfmt):
        """Downloads the url and saves to the given path"""
        try:
            return self._download_impl(url, pathfmt)
        
        except Exception:
            print()
            raise

        finally:
            # remove file from incomplete downloads
            if self.downloading:
                util.remove_file(pathfmt.temp_path)



    def _download_impl(self, url, pathfmt):
        """Download mainloop"""

        response = None
        tries = 0
        msg = ""

        # kwdict = pathfmt.kwdict

        while True:
            if self.cancled:
                if response:
                    response.close()
                    response = None
                return False
            if tries:
                if response:
                    response.close()
                    response = None
                    
                self.log.warning("%s (%s/%s)", msg, tries, self.retries+1)

                if tries > self.retries:
                    return False
                time.sleep(tries)

            tries += 1
            file_header = None

            # collect HTTP headers
            headers = {"Accept": "*/*"}

            #   file-specific headers
            # extra = kwdict.get("_http_headers")
            
            # if extra:
            #     headers.update(extra)
            
            #   general headers
            if self.headers:
                headers.update(self.headers)
            
            #   partial content
            file_size = pathfmt.part_size()
            if file_size:
                headers["Range"] = "bytes={}-".format(file_size)

            # connect to (remote) source
            try:
                response = self.session.request("GET", url, stream=True, headers=headers, timeout=self.timeout, verify=self.verify)
            except (ConnectionError, Timeout) as exc:
                msg = str(exc)
                continue
            except Exception as exc:
                self.log.warning(exc)
                return False

            # check response
            code = response.status_code
            if code == 200:  # OK
                offset = 0
                size = response.headers.get("Content-Length")

            elif code == 206:  # Partial Content
                offset = file_size
                size = response.headers["Content-Range"].rpartition("/")[2]

            elif code == 416 and file_size:  # Requested Range Not Satisfiable
                break

            else:
                msg = "'{} {}' for '{}'".format(code, response.reason, url)

                if code == 429 or 500 <= code < 600:  # Server Error
                    continue
                
                self.log.warning(msg)
                return False

            # check for invalid responses
            # validate = kwdict.get("_http_validate")
            # if validate and not validate(response):
            #     self.log.warning("Invalid response")
            #     return False

            # set missing filename extension from MIME type
            if not pathfmt.extension:
                pathfmt.set_extension(self._find_extension(response))

                if pathfmt.exists():
                    return True

            # check file size
            size = util.parse_int(size, None)

            if size is not None:
                if self.min_file_size and size < self.min_file_size:
                    self.log.warning("File size smaller than allowed minimum (%s < %s)", size, self.min_file_size)
                    return False

                if self.max_file_size and size > self.max_file_size:
                    self.log.warning("File size larger than allowed maximum (%s > %s)", size, self.max_file_size)
                    return False

            content = response.iter_content(self.chunk_size)

            # check filename extension against file header
            if not offset and self.adjust_extension and pathfmt.extension in FILE_SIGNATURES:
                try:
                    file_header = next(content if response.raw.chunked else response.iter_content(16), b"")

                except (RequestException, SSLError, OpenSSLError) as exc:
                    msg = str(exc)
                    print()
                    continue

                if self._adjust_extension(pathfmt, file_header) and pathfmt.exists():
                    return True

            # set open mode
            if not offset:
                mode = "w+b"
                if file_size:
                    self.log.debug("Unable to resume partial download")
            else:
                mode = "r+b"
                self.log.debug("Resuming download at byte %d", offset)

            # download content
            self.downloading = True
            with pathfmt.open(mode) as fp:
                
                if file_header:
                    fp.write(file_header)
                    offset += len(file_header)

                elif offset:
                    if self.adjust_extension and pathfmt.extension in FILE_SIGNATURES:
                        self._adjust_extension(pathfmt, fp.read(16))
                    fp.seek(offset)

                # self.out.start(pathfmt.path)
                print("starting download of: {}".format(url))

                try:
                    self.receive(fp, content, size, offset)
                    
                except (RequestException, SSLError, OpenSSLError, exceptions.DownloadCanceledError) as exc:
                    msg = str(exc)
                    print()
                    continue

                # check file size
                if size and fp.tell() < size:
                    msg = "file size mismatch ({} < {})".format(fp.tell(), size)
                    print()
                    continue

            break

        self.downloading = False

        return True


    # @staticmethod
    def _receive(self, fp, content, bytes_total, bytes_downloaded):

        for data in content:
            if self.cancled:
                raise exceptions.DownloadCanceledError()
            fp.write(data)


    def _receive_rate(self, fp, content, bytes_total, bytes_downloaded):
        rate = self.rate
        progress = self.progress
        bytes_start = bytes_downloaded
        write = fp.write
        t1 = tstart = time.time()

        for data in content:

            if self.cancled:
                raise exceptions.DownloadCanceledError()

            write(data)

            t2 = time.time()           # current time
            elapsed = t2 - t1          # elapsed time
            num_bytes = len(data)

            if progress is not None:
                bytes_downloaded += num_bytes
                tdiff = t2 - tstart
                if tdiff >= progress:
                    self.out.progress(
                        bytes_total, bytes_downloaded,
                        int((bytes_downloaded - bytes_start) / tdiff),
                    )

            if rate:
                expected = num_bytes / rate  # expected elapsed time
                if elapsed < expected:
                    # sleep if less time elapsed than expected
                    time.sleep(expected - elapsed)
                    t2 = time.time()

            t1 = t2


    def _find_extension(self, response):
        """Get filename extension from MIME type"""
        mtype = response.headers.get("Content-Type", "image/jpeg")
        mtype = mtype.partition(";")[0]

        if "/" not in mtype:
            mtype = "image/" + mtype

        if mtype in MIME_TYPES:
            return MIME_TYPES[mtype]

        ext = mimetypes.guess_extension(mtype, strict=False)
        if ext:
            return ext[1:]

        self.log.warning("Unknown MIME type '%s'", mtype)
        return "bin"


    @staticmethod
    def _adjust_extension(pathfmt, file_header):
        """Check filename extension against file header"""
        sig = FILE_SIGNATURES[pathfmt.extension]

        if not file_header.startswith(sig):
            for ext, sig in FILE_SIGNATURES.items():
                if file_header.startswith(sig):
                    pathfmt.set_extension(ext)
                    return True
        return False


__downloader__ = HttpDownloader