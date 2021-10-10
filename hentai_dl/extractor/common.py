# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re
import ssl
import time
import netrc
import queue
import logging
import datetime
import requests
import threading
from requests.adapters import HTTPAdapter
from .message import Message
from .. import config, text, util, exceptions
from ..util import WINDOWS

class Extractor():

    category = ""
    subcategory = ""
    basecategory = ""
    categorytransfer = False
    directory_fmt = ("{category}",)
    filename_fmt = "{filename}.{extension}"
    archive_fmt = ""
    cookiedomain = ""
    browser = None
    root = ""
    test = None
    request_interval = 0.0
    request_interval_min = 0.0
    request_timestamp = 0.0

    PLATFORM_MAP = {
        "auto" : ("Windows NT 10.0; Win64; x64" if WINDOWS else "X11; Linux x86_64"),
        "windows" : "Windows NT 10.0; Win64; x64",
        "linux" : "X11; Linux x86_64",
        "macos" : "Macintosh; Intel Mac OS X 11.5"
    }

    def __init__(self, match):
        self.log = logging.getLogger(self.category)
        self.url = match.string
        self.finalize = None

        if self.basecategory:
            self.config = self._config_shared
            self.config_accumulate = self._config_shared_accumulate

        self._cfgpath = ("extractor", self.category, self.subcategory)
        self._parentdir = ""

        self._write_pages = False # self.config("write-pages", False)
        self._retries = 4 # self.config("retries", 4)
        self._timeout = 30 # self.config("timeout", 30)
        self._verify = True # self.config("verify", True)
        # self._interval = util.build_duration_func(
        #     self.config("sleep-request", self.request_interval),
        #     self.request_interval_min,
        # )

        if self._retries < 0:
            self._retries = float("inf")

        self._init_session()
        self._init_cookies()
        self._init_proxies()

    @classmethod
    def from_url(cls, url):
        if isinstance(cls.pattern, str):
            cls.pattern = re.compile(cls.pattern)

        match = cls.pattern.match(url)
        return cls(match) if match else None

    def __iter__(self):
        return self.items()

    def items(self):
        yield Message.Version, 1

    def skip(self, num):
        return 0

    def config(self, key, default=None):
        return config.interpolate(self._cfgpath, key, default)

    def config_accumulate(self, key):
        return config.accumulate(self._cfgpath, key)

    def _config_shared(self, key, default=None):
        return config.interpolate_common(("extractor",), (
            (self.category, self.subcategory),
            (self.basecategory, self.subcategory),
        ), key, default)

    def _config_shared_accumulate(self, key):
        values = config.accumulate(self._cfgpath, key)
        conf = config.get(("extractor",), self.basecategory)
        if conf:
            values[:0] = config.accumulate((self.subcategory,), key, conf=conf)
        return values

    def request(self, url, *, method="GET", session=None, retries=None,
                encoding=None, fatal=True, notfound=None, **kwargs):
        if retries is None:
            retries = self._retries

        if session is None:
            session = self.session

        if "timeout" not in kwargs:
            kwargs["timeout"] = self._timeout

        if "verify" not in kwargs:
            kwargs["verify"] = self._verify

        response = None
        tries = 1

        if self._interval:
            seconds = (self._interval() - (time.time() - Extractor.request_timestamp))

            if seconds > 0.0:
                self.log.debug("Sleeping for %.5s seconds", seconds)
                time.sleep(seconds)

        while True:
            try:
                response = session.request(method, url, **kwargs)

            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.ChunkedEncodingError,
                    requests.exceptions.ContentDecodingError) as exc:
                msg = exc

            except (requests.exceptions.RequestException) as exc:
                raise exceptions.HttpError(exc)

            else:
                code = response.status_code

                if self._write_pages:
                    self._dump_response(response)

                if 200 <= code < 400 or fatal is None and \
                        (400 <= code < 500) or not fatal and \
                        (400 <= code < 429 or 431 <= code < 500):
                    if encoding:
                        response.encoding = encoding
                    return response

                if notfound and code == 404:
                    raise exceptions.NotFoundError(notfound)

                msg = "'{} {}' for '{}'".format(code, response.reason, url)
                server = response.headers.get("Server")

                if server and server.startswith("cloudflare"):
                    if code == 503 and b"jschl-answer" in response.content:
                        self.log.warning("Cloudflare IUAM challenge")
                        break

                    if code == 403 and b'name="captcha-bypass"' in response.content:
                        self.log.warning("Cloudflare CAPTCHA")
                        break

                if code < 500 and code != 429 and code != 430:
                    break

            finally:
                Extractor.request_timestamp = time.time()

            self.log.debug("%s (%s/%s)", msg, tries, retries+1)

            if tries > retries:
                break

            time.sleep(max(tries, self.request_interval))
            tries += 1

        raise exceptions.HttpError(msg, response)


    def wait(self, *, seconds=None, until=None, adjust=1.0, reason="rate limit reset"):
        now = time.time()

        if seconds:
            seconds = float(seconds)
            until = now + seconds

        elif until:
            if isinstance(until, datetime.datetime):
                # convert to UTC timestamp
                until = (until - util.EPOCH) / util.SECOND
            else:
                until = float(until)
            seconds = until - now

        else:
            raise ValueError("Either 'seconds' or 'until' is required")

        seconds += adjust
        if seconds <= 0.0:
            return

        if reason:
            t = datetime.datetime.fromtimestamp(until).time()
            isotime = "{:02}:{:02}:{:02}".format(t.hour, t.minute, t.second)
            self.log.info("Waiting until %s for %s.", isotime, reason)

        time.sleep(seconds)


    def _get_auth_info(self):
        """Return authentication information as (username, password) tuple"""

        username = self.config("username")
        password = None

        if username:
            password = self.config("password")

        elif self.config("netrc", False):
            try:
                info = netrc.netrc().authenticators(self.category)
                username, _, password = info

            except (OSError, netrc.NetrcParseError) as exc:
                self.log.error("netrc: %s", exc)

            except TypeError:
                self.log.warning("netrc: No authentication info")

        return username, password


    def _init_session(self):
        self.session = session = requests.Session()
        headers = session.headers
        headers.clear()

        browser = self.config("browser", self.browser)

        if browser and isinstance(browser, str):
            browser, _, platform = browser.lower().partition(":")

            platform = self.PLATFORM_MAP.get(platform, self.PLATFORM_MAP["linux"])
            
            if browser == "chrome":
                _emulate_browser_chrome(session, platform)
            else:
                _emulate_browser_firefox(session, platform)
                
        else:
            headers["User-Agent"] = self.config("user-agent", (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; "
                "rv:91.0) Gecko/20100101 Firefox/91.0"))
            headers["Accept"] = "*/*"
            headers["Accept-Language"] = "en-US,en;q=0.5"
            headers["Accept-Encoding"] = "gzip, deflate"

        custom_headers = self.config("headers")
        if custom_headers:
            headers.update(custom_headers)

        ciphers = self.config("ciphers")
        if ciphers:
            if isinstance(ciphers, list):
                ciphers = ":".join(ciphers)
            session.mount("https://", HTTPSAdapter(ciphers))


    def _init_proxies(self):
        """Update the session's proxy map"""

        proxies = self.config("proxy")
        
        if not proxies:
            return 
        
        if isinstance(proxies, str):
            proxies = {"http": proxies, "https": proxies}

        if isinstance(proxies, dict):
            for scheme, proxy in proxies.items():
                if "://" not in proxy:
                    proxies[scheme] = "http://" + proxy.lstrip("/")

            self.session.proxies = proxies

        else:
            self.log.warning("invalid proxy specifier: %s", proxies)


    def _init_cookies(self):
        """Populate the session's cookiejar"""

        self._cookiefile = None
        self._cookiejar = self.session.cookies

        if self.cookiedomain is None:
            return

        cookies = self.config("cookies")
        if not cookies:
            return 

        if isinstance(cookies, dict):
            self._update_cookies_dict(cookies, self.cookiedomain)

        elif isinstance(cookies, str):
            cookiefile = util.expand_path(cookies)

            try:
                with open(cookiefile) as fp:
                    cookies = util.load_cookiestxt(fp)

            except Exception as exc:
                self.log.warning("cookies: %s", exc)

            else:
                self._update_cookies(cookies)
                self._cookiefile = cookiefile

        else:
            self.log.warning(
                "expected 'dict' or 'str' value for 'cookies' option, "
                "got '%s' (%s)", cookies.__class__.__name__, cookies)


    def _store_cookies(self):
        """Store the session's cookiejar in a cookies.txt file"""

        if self._cookiefile and self.config("cookies-update", True):
            try:
                with open(self._cookiefile, "w") as fp:
                    util.save_cookiestxt(fp, self._cookiejar)

            except OSError as exc:
                self.log.warning("cookies: %s", exc)


    def _update_cookies(self, cookies, *, domain=""):
        """Update the session's cookiejar with 'cookies'"""

        if isinstance(cookies, dict):
            self._update_cookies_dict(cookies, domain or self.cookiedomain)

        else:
            setcookie = self._cookiejar.set_cookie
            try:
                cookies = iter(cookies)

            except TypeError:
                setcookie(cookies)

            else:
                for cookie in cookies:
                    setcookie(cookie)


    def _update_cookies_dict(self, cookiedict, domain):
        """Update cookiejar with name-value pairs from a dict"""

        setcookie = self._cookiejar.set
        for name, value in cookiedict.items():
            setcookie(name, value, domain=domain)


    def _check_cookies(self, cookienames, *, domain=None):
        """Check if all 'cookienames' are in the session's cookiejar"""

        if not self._cookiejar:
            return False

        if domain is None:
            domain = self.cookiedomain

        names = set(cookienames)
        now = time.time()

        for cookie in self._cookiejar:
            if cookie.name in names and cookie.domain == domain:
                if cookie.expires and cookie.expires < now:
                    self.log.warning("Cookie '%s' has expired", cookie.name)

                else:
                    names.discard(cookie.name)
                    if not names:
                        return True
        return False


    def _prepare_ddosguard_cookies(self):
        if not self._cookiejar.get("__ddg2", domain=self.cookiedomain):
            self._cookiejar.set("__ddg2", util.generate_token(), domain=self.cookiedomain)


    def _get_date_min_max(self, dmin=None, dmax=None):
        """Retrieve and parse 'date-min' and 'date-max' config values"""

        def get(key, default):
            ts = self.config(key, default)
        
            if isinstance(ts, str):
                try:
                    ts = int(datetime.datetime.strptime(ts, fmt).timestamp())

                except ValueError as exc:
                    self.log.warning("Unable to parse '%s': %s", key, exc)
                    ts = default

            return ts

        fmt = self.config("date-format", "%Y-%m-%dT%H:%M:%S")
        return get("date-min", dmin), get("date-max", dmax)


    def _dispatch_extractors(self, extractor_data, default=()):
        
        extractors = {
            data[0].subcategory : data
            for data in extractor_data
        }

        include = self.config("include", default) or ()
        if include == "all":
            include = extractors

        elif isinstance(include, str):
            include = include.split(",")

        result = [(Message.Version, 1)]
        for category in include:
            if category in extractors:
                extr, url = extractors[category]
                result.append((Message.Queue, url, {"_extractor": extr}))

        return iter(result)

    @classmethod
    def _get_tests(cls):
        """Yield an extractor's test cases as (URL, RESULTS) tuples"""

        tests = cls.test
        if not tests:
            return

        if len(tests) == 2 and (not tests[1] or isinstance(tests[1], dict)):
            tests = (tests,)

        for test in tests:
            if isinstance(test, str):
                test = (test, None)
            yield test


    def _dump_response(self, response, history=True):
        """Write the response content to a .dump file in the current directory.

        The file name is derived from the response url,
        replacing special characters with "_"
        """

        if history:
            for resp in response.history:
                self._dump_response(resp, False)

        if hasattr(Extractor, "_dump_index"):
            Extractor._dump_index += 1

        else:
            Extractor._dump_index = 1
            Extractor._dump_sanitize = re.compile(r"[\\\\|/<>:\"?*&=#]+").sub

        fname = "{:>02}_{}".format(
            Extractor._dump_index,
            Extractor._dump_sanitize('_', response.url)
        )[:250]

        try:
            with open(fname + ".dump", 'wb') as fp:
                util.dump_response(
                    response, fp, headers=(self._write_pages == "all"))

        except Exception as e:
            self.log.warning("Failed to dump HTTP request (%s: %s)",
                             e.__class__.__name__, e)


class GalleryExtractor(Extractor):

    subcategory = "gallery"
    filename_fmt = "{category}_{gallery_id}_{num:>03}.{extension}"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    archive_fmt = "{gallery_id}_{num}"
    enum = "num"

    def __init__(self, match, url=None):
        Extractor.__init__(self, match)
        self.gallery_url = self.root + match.group(1) if url is None else url

    def items(self):
        self.login()
        page = self.request(self.gallery_url, notfound=self.subcategory).text
        data = self.metadata(page)
        imgs = self.images(page)

        if "count" in data:
            if self.config("page-reverse"):
                images = util.enumerate_reversed(imgs, 1, data["count"])
            else:
                images = zip(
                    range(1, data["count"]+1),
                    imgs,
                )
        else:
            enum = enumerate
            try:
                data["count"] = len(imgs)
            except TypeError:
                pass
            else:
                if self.config("page-reverse"):
                    enum = util.enumerate_reversed
            images = enum(imgs, 1)

        yield Message.Directory, data
        for data[self.enum], (url, imgdata) in images:
            if imgdata:
                data.update(imgdata)
                if "extension" not in imgdata:
                    text.nameext_from_url(url, data)
            else:
                text.nameext_from_url(url, data)
            yield Message.Url, url, data

    def login(self):
        """Login and set necessary cookies"""

    def metadata(self, page):
        """Return a dict with general metadata"""

    def images(self, page):
        """Return a list of all (image-url, metadata)-tuples"""



class HTTPSAdapter(HTTPAdapter):

    def __init__(self, ciphers):
        context = self.ssl_context = ssl.create_default_context()
        context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 |
                            ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
        context.set_ecdh_curve("prime256v1")
        context.set_ciphers(ciphers)
        HTTPAdapter.__init__(self)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        return HTTPAdapter.init_poolmanager(self, *args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        return HTTPAdapter.proxy_manager_for(self, *args, **kwargs)


def _emulate_browser_firefox(session, platform):
    headers = session.headers
    headers["User-Agent"] = ("Mozilla/5.0 (" + platform + "; rv:91.0) "
                             "Gecko/20100101 Firefox/91.0")
    headers["Accept"] = ("text/html,application/xhtml+xml,"
                         "application/xml;q=0.9,image/webp,*/*;q=0.8")
    headers["Accept-Language"] = "en-US,en;q=0.5"
    headers["Accept-Encoding"] = "gzip, deflate"
    headers["Referer"] = None
    headers["Upgrade-Insecure-Requests"] = "1"
    headers["Cookie"] = None

    session.mount("https://", HTTPSAdapter(
        "TLS_AES_128_GCM_SHA256:"
        "TLS_CHACHA20_POLY1305_SHA256:"
        "TLS_AES_256_GCM_SHA384:"
        "ECDHE-ECDSA-AES128-GCM-SHA256:"
        "ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-CHACHA20-POLY1305:"
        "ECDHE-RSA-CHACHA20-POLY1305:"
        "ECDHE-ECDSA-AES256-GCM-SHA384:"
        "ECDHE-RSA-AES256-GCM-SHA384:"
        "ECDHE-ECDSA-AES256-SHA:"
        "ECDHE-ECDSA-AES128-SHA:"
        "ECDHE-RSA-AES128-SHA:"
        "ECDHE-RSA-AES256-SHA:"
        "DHE-RSA-AES128-SHA:"
        "DHE-RSA-AES256-SHA:"
        "AES128-SHA:"
        "AES256-SHA:"
        "DES-CBC3-SHA"
    ))



def _emulate_browser_chrome(session, platform):
    if platform.startswith("Macintosh"):
        platform = platform.replace(".", "_") + "_2"

    headers = session.headers
    headers["Upgrade-Insecure-Requests"] = "1"
    headers["User-Agent"] = (
        "Mozilla/5.0 (" + platform + ") AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36")
    headers["Accept"] = ("text/html,application/xhtml+xml,application/xml;"
                         "q=0.9,image/webp,image/apng,*/*;q=0.8")
    headers["Referer"] = None
    headers["Accept-Encoding"] = "gzip, deflate"
    headers["Accept-Language"] = "en-US,en;q=0.9"
    headers["Cookie"] = None

    session.mount("https://", HTTPSAdapter(
        "TLS_AES_128_GCM_SHA256:"
        "TLS_AES_256_GCM_SHA384:"
        "TLS_CHACHA20_POLY1305_SHA256:"
        "ECDHE-ECDSA-AES128-GCM-SHA256:"
        "ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-AES256-GCM-SHA384:"
        "ECDHE-RSA-AES256-GCM-SHA384:"
        "ECDHE-ECDSA-CHACHA20-POLY1305:"
        "ECDHE-RSA-CHACHA20-POLY1305:"
        "ECDHE-RSA-AES128-SHA:"
        "ECDHE-RSA-AES256-SHA:"
        "AES128-GCM-SHA256:"
        "AES256-GCM-SHA384:"
        "AES128-SHA:"
        "AES256-SHA:"
        "DES-CBC3-SHA"
    ))