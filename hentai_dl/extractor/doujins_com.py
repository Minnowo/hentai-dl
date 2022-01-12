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


class DoujinsDotComGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from nhentai.net"""

    pattern = r"(?:https?://)?doujins.com/(.*?)/(.*?)-(\d+)"
    category = "doujins"
    root = "https://doujins.com"
    media_url = "https://static.doujins.com"

    def __init__(self, match, use_api = False):
        
        # no idea if they have an api, but based on how messy the site is probably not
        url = self.root + "/" + match.group(1) + "/" + match.group(2) + "-" + match.group(3)
        
        self.use_api = False
        GalleryExtractor.__init__(self, match, url)
        
        # doujin.com filenames are really messy and not in order when sorted
        self.iter_names = True 


    def metadata(self, page):
        return self.metadata_scrape(page)

    def metadata_api(self, page):
        self.data = {}
        return {}

    def metadata_scrape(self, page):

        html = BeautifulSoup(page, 'html.parser')
        data = {}

        title_div = html.find('div', attrs={'class': 'folder-title'})

        _ = [i.text for i in title_div.find_all('a')]
        data["title"] = " - ".join(_)
        data["title_pretty"] = _[-1] if _ else data["title"]
        
        tag_area = html.find('li', attrs={'class' : 'tag-area'})
        if tag_area:
            data['tags'] = [i.text.strip() for i in tag_area.find_all('a') if i]

        else:
            data['tags'] = []

        artists = html.find('div', attrs={'class' : 'gallery-artist'})
        if artists:
            data['artists'] = [i.text.strip() for i in artists.find_all('a') if i]

        else:
            data['artists'] = []

        message_area = html.find_all('div', attrs={'class':'folder-message'})
        if message_area:
            data['message'] = [i.text.strip() for i in message_area if i]

        else:
            data['message'] = []

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
        
        html = BeautifulSoup(page, 'html.parser')
        imgs = []
        images_area = html.find_all('div', attrs={'class' : 'swiper-slide'})

        for slider in images_area:

            img = search(r'src=\"(.*?)\"', str(slider.find('img')))
            if img:
                pg = img.group(1)
                
                # the urls look like this: https://static.doujins.com/n-ybqzb1dv.jpg?st=DIeNsEYQrnOyvHV1Y1D57g&e=1632413343
                # but when scraping from the page
                # they look like this    : https://static.doujins.com/n-ybqzb1dv.jpg?st=DIeNsEYQrnOyvHV1Y1D57g&amp;e=1632413343
                # and if they have the 'amp;' after the get request, the url doesn't work

                match = search(r'^(?:https?://)?static.doujins.com/(.*?)&(.*?);(.*?)$', pg)
                
                if match:
                    # reformat the deconstructed url so that it doesn't contain the 'amp;' 
                    # only reason i'm not directly searching for 'amp;' is because i'm not sure 
                    # if its a constant for everything on the site, but chances are if its not
                    # the url will still have random characters before a ; after the get request
                    pg = "{}/{}&{}".format(self.media_url, match.group(1), match.group(3))

                imgs.append((pg, {"w" : -1, "h" : -1}))

        return imgs

