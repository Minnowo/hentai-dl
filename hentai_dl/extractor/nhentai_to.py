# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nhentai.to/"""

from bs4 import BeautifulSoup
from re import search

from .common import GalleryExtractor
from .. import util


class NhentaiBase():
    """Base class for nhentai extractors"""
    category = "nhentai"
    root = "https://nhentai.to"
    media_url = "https://t.dogehls.xyz"


class NhentaiGalleryExtractor(NhentaiBase, GalleryExtractor):
    """Extractor for image galleries from nhentai.io"""

    pattern = r"(?:https?://)?nhentai\.to/g/(\d+)"


    def __init__(self, match, use_api = False):

        url = self.root + "/g/" + match.group(1)
        
        self.gallery_id = util.parse_int(match.group(1))
        self.use_api = False
        GalleryExtractor.__init__(self, match, url)

        self.iter_names = True


    def metadata(self, page):
        return self.metadata_scrape(page)

    def metadata_api(self, page):
        return {}

    def metadata_scrape(self, page):
        
        html = BeautifulSoup(page, 'html.parser')
        data = {}

        info_div = html.find('div', attrs={'id': 'info'})

        data["title"] = info_div.find('h1').text

        p_title = info_div.find('h1').find('span', attrs={'class': 'pretty'})
        data["title_pretty"] = p_title.text if p_title else ""
        
        subtitle = info_div.find('h2')
        data["subtitle"] = subtitle.text if subtitle else ""

        data["gallery_id"] = self.gallery_id

        doujinshi_cover = html.find('div', attrs={'id': 'cover'})
        data["media_id"] = util.parse_int(search('/galleries/([0-9]+)/cover.(jpg|png|gif)$', doujinshi_cover.a.img.attrs['src']).group(1))        

        needed_fields = [
            'Characters', 'Artists', 'Languages', 'Pages',
            'Tags', 'Parodies', 'Groups', 'Categories'
            ]
        
        for field in info_div.find_all('div', attrs={'class': 'field-name'}):

            field_name = field.contents[0].strip().strip(':')

            if field_name in needed_fields:
                dat = [s.contents[0].strip() for s in field.find_all('a', attrs={'class': 'tag'})]
                data[field_name.lower()] = ', '.join(dat)

        time_field = info_div.find('time')
        if time_field.has_attr('datetime'):
            data['uploaded'] = time_field['datetime']

        self.data = data 
        return data



    def images(self, page):
        """Gets the gallery images"""
        return self.image_scrape(page)

    def image_api(self):
        """Gets all the gallery images from the api"""
        return []

    def image_scrape(self, page):
        """Gets all gallery images from the web source"""

        images = []
 
        html = BeautifulSoup(page, 'html.parser')

        doujinshi_cover = html.find('div', attrs={'id': 'cover'})
        img_id = search('/galleries/([0-9]+)/cover.(jpg|png|gif)$', doujinshi_cover.a.img.attrs['src']).group(1)

        index = 0
        for i in html.find_all('div', attrs={'class': 'thumb-container'}):
            index += 1
            thumb_url = i.img.attrs['data-src']
            ext = thumb_url.rsplit(".", 1)[-1]
            # "https://t.dogehls.xyz" + / + galleries + / + xxxxx + / xxx.ext
            image_url = "%s/galleries/%s/%d.%s" % (self.media_url, img_id, index, ext)

            # width and height meta are missing from the gallery page,
            # would require a bunch of requests to get the info without using the api
            images.append((image_url, {"w" : -1, "h" : -1, "extension" : ext}))

        return images

