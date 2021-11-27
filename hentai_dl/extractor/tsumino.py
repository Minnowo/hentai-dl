# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tsumino.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, exceptions, util
from bs4 import BeautifulSoup
from html import unescape
# from ..cache import cache


class TsuminoBase():
    """Base class for tsumino extractors"""
    category = "tsumino"
    cookiedomain = "www.tsumino.com"
    root = "https://www.tsumino.com"

    def login(self):
        # username, password = self._get_auth_info()
        # if username:
        #     self._update_cookies(self._login_impl(username, password))
        # else:
            self.session.cookies.setdefault(
                "ASP.NET_SessionId", "x1drgggilez4cpkttneukrc5")

    # @cache(maxage=14*24*3600, keyarg=1)
    # def _login_impl(self, username, password):
    #     self.log.info("Logging in as %s", username)
    #     url = "{}/Account/Login".format(self.root)
    #     headers = {"Referer": url}
    #     data = {"Username": username, "Password": password}

    #     response = self.request(url, method="POST", headers=headers, data=data)
    #     if not response.history:
            # raise exceptions.AuthenticationError()
    #     return self.session.cookies


class TsuminoGalleryExtractor(TsuminoBase, GalleryExtractor):
    """Extractor for image galleries on tsumino.com"""
    pattern = (r"(?i)(?:https?://)?(?:www\.)?tsumino\.com"
               r"/(?:entry|Book/Info|Read/(?:Index|View))/(\d+)")

    def __init__(self, match, use_api = False):
        self.gallery_id = match.group(1)
        
        url = "{}/entry/{}".format(self.root, self.gallery_id)

        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):

        soup = BeautifulSoup(page, "html.parser")

        title = soup.find("meta", property="og:title")['content']

        title_en, _, title_jp = unescape(title).partition("/")
        title_en = title_en.strip()
        title_jp = title_jp.strip()

        return {
            "gallery_id": util.parse_int(self.gallery_id),
            "title"     : title_en or title_jp,
            "title_en"  : title_en,
            "title_jp"  : title_jp,
            "thumbnail" : soup.find("meta", attrs={"property" : "og:image"})["content"],
            "uploader"  : soup.find("div", attrs={"id" : "Uploader"}).a.text.strip(),
            "date"      : text.parse_datetime(soup.find("div", attrs={"id" : "Uploaded"}).text.strip(), "%Y %B %d"),
            "group"     : [x.text.strip() for x in soup.find("div", attrs={"id" : "Group"}).find_all("a", attrs={"class" : "book-tag"})],
            "artist"    : [x.text.strip() for x in soup.find("div", attrs={"id" : "Artist"}).find_all("a", attrs={"class" : "book-tag"})],
            "parody"    : [x.text.strip() for x in soup.find("div", attrs={"id" : "Parody"}).find_all("a", attrs={"class" : "book-tag"})],
            "characters": [x.text.strip() for x in soup.find("div", attrs={"id" : "Character"}).find_all("a", attrs={"class" : "book-tag"})],
            "tags"      : [x.text.strip() for x in soup.find("div", attrs={"id" : "Tag"}).find_all("a", attrs={"class" : "book-tag"})],
            "language"  : "English",
            "lang"      : "en",
        }


    def images(self, page):
        url = "{}/Read/Index/{}?page=1".format(self.root, self.gallery_id)
        headers = {"Referer": self.gallery_url}
        response = self.request(url, headers=headers, fatal=False)

        if "/Auth/" in response.url:
            raise exceptions.StopExtraction(
                "Failed to get gallery JSON data. Visit '%s' in a browser "
                "and solve the CAPTCHA to continue.", response.url)

        soup = BeautifulSoup(response.content, "html.parser")

        img = soup.find("div", attrs={"id" : "image-container"})["data-cdn"]
        
        page_count = util.parse_int(soup.find("h1").text.rsplit(" ", 1)[1])
        base, _, params = unescape(img).partition("[PAGE]")

        return [(base + str(i) + params, {}) for i in range(1, page_count + 1)]

