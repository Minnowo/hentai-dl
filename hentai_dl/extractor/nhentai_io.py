# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nhentai.net/"""

from bs4 import BeautifulSoup
from re import search

from .common import GalleryExtractor, Extractor, Message
from .. import text, util
import collections
import json


class NhentaiBase():
    """Base class for nhentai extractors"""
    category = "nhentai"
    root = "https://nhentai.io"
    media_url = "https://himg.nl/images/nhentai/"


class NhentaiGalleryExtractor(NhentaiBase, GalleryExtractor):
    """Extractor for image galleries from nhentai.net"""

    pattern = r"(?:https?://)?nhentai\.io/([^\/]*)"


    def __init__(self, match, use_api = False):

        url = self.root + "/" + match.group(1)
        
        self.use_api = use_api
        GalleryExtractor.__init__(self, match, url)

        self.iter_names = True


    def items(self):
        self.login()
        page = self.request(self.gallery_url, notfound=self.subcategory).text
        data = self.metadata(page)
        page = self.request(self.gallery_url + "/read/", notfound=self.subcategory).text
        imgs = self.images(page)

        if "count" in data:
            if self.config("page-reverse"):
                images = util.enumerate_reversed(imgs, 1, data["count"])

            else:
                images = zip(range(1, data["count"] + 1), imgs)

        else:
            try:
                data["count"] = len(imgs)
            except TypeError:
                pass
            
            if self.config("page-reverse"):
                images = util.enumerate_reversed(imgs, 1)

            else:
                images = enumerate(imgs, 1)


        yield Message.Directory, data

        # compute the z_fill once even if its not used
        z_fill = len(str(data["count"]))

        for i, (url, imgdata) in images:
            util.add_nameext_from_url(url, imgdata)
            
            if self.iter_names:
                imgdata["filename"] = "{}".format(i).zfill(z_fill)

            yield Message.Url, url, imgdata


    def metadata(self, page):
        html = BeautifulSoup(page, 'html.parser')
        data = {}

        info_div = html.find('div', attrs={'id': 'info'})

        data["title"] = info_div.find('h1').text

        p_title = info_div.find('h1').find('span', attrs={'class': 'pretty'})
        data["title_pretty"] = p_title.text if p_title else ""
        
        subtitle = info_div.find('h2')
        data["subtitle"] = subtitle.text if subtitle else ""

        data["gallery_id"] = -1

        needed_fields = [
            'Characters', 'Artists', 'Languages', 'Pages',
            'Tags', 'Parodies', 'Groups', 'Categories'
            ]
        
        for field in info_div.find_all('div', attrs={'class': 'field-name'}):

            field_name = field.contents[0].strip().strip(':')

            if field_name in needed_fields:
                dat = [s.find('span', attrs={'class': 'name'}).contents[0].strip() for s in field.find_all('a', attrs={'class': 'tag'})]
                data[field_name.lower()] = ', '.join(dat)

        time_field = info_div.find('time')
        if time_field.has_attr('datetime'):
            data['uploaded'] = time_field['datetime']

        self.data = data 
        return data


    def images(self, page):
        """Gets the gallery images"""
        
        images = []
 
        html = BeautifulSoup(page, 'html.parser')

        doujinshi_cover = html.find('div', attrs={'class': 'readimg'})

        index = 0
        for i in doujinshi_cover.find_all('img'):
            index += 1
            image_url = i.attrs['src']
            ext = image_url.rsplit(".", 1)[-1]

            # width and height meta are missing from the gallery page,
            # would require a bunch of requests to get the info without using the api
            images.append((image_url, {"w" : -1, "h" : -1, "extension" : ext}))

        return images


# class NhentaiSearchExtractor(NhentaiBase, Extractor):
#     """Extractor for nhentai search results"""

#     subcategory = "search"
#     pattern = r"(?:https?://)?nhentai\.net/search/?\?([^#]+)"
#     test = ("https://nhentai.net/search/?q=touhou", {
#         "pattern": NhentaiGalleryExtractor.pattern,
#         "count": 30,
#         "range": "1-30",
#     })


#     def __init__(self, match):
#         Extractor.__init__(self, match)
#         self.params = text.parse_query(match.group(1))


#     def items(self):
#         data = {"_extractor": NhentaiGalleryExtractor}
#         for gallery_id in self._pagination(self.params):
#             url = "{}/g/{}/".format(self.root, gallery_id)
#             yield Message.Queue, url, data


#     def _pagination(self, params):
#         url = "{}/search/".format(self.root)
#         params["page"] = text.parse_int(params.get("page"), 1)

#         while True:
#             page = self.request(url, params=params).text
#             yield from text.extract_iter(page, 'href="/g/', '/')
#             if 'class="next"' not in page:
#                 return
#             params["page"] += 1


# class NhentaiFavoriteExtractor(NhentaiBase, Extractor):
#     """Extractor for nhentai favorites"""

#     subcategory = "favorite"
#     pattern = r"(?:https?://)?nhentai\.net/favorites/?(?:\?([^#]+))?"
#     test = ("https://nhentai.net/favorites/",)


#     def __init__(self, match):
#         Extractor.__init__(self, match)
#         self.params = text.parse_query(match.group(1))


#     def items(self):
#         data = {"_extractor": NhentaiGalleryExtractor}
#         for gallery_id in self._pagination(self.params):
#             url = "{}/g/{}/".format(self.root, gallery_id)
#             yield Message.Queue, url, data


#     def _pagination(self, params):
#         url = "{}/favorites/".format(self.root)
#         params["page"] = text.parse_int(params.get("page"), 1)

#         while True:
#             page = self.request(url, params=params).text
#             yield from text.extract_iter(page, 'href="/g/', '/')
#             if 'class="next"' not in page:
#                 return
#             params["page"] += 1
