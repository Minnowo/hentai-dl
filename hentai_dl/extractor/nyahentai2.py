# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nhentai.net/"""

from bs4 import BeautifulSoup
from re import search, match

from .common import Extractor, GalleryExtractor, Message
from .. import util
import collections
import json

class NyaHentai2Base():

    category = "nyahentai2"
    root = "https://nyahentai2.net"

class NyaHentai2Extractor(NyaHentai2Base, GalleryExtractor):

    pattern = r"(?:https?://)?nyahentai2\.net/(?:read/)?(\d+)"

    def __init__(self, match, use_api = False):

        # like 90% sure this site has an api available but its like 3am and i already did web scraping which is plenty
        use_api = False 

        url = self.root + "/read/" + match.group(1) + ".html"

        GalleryExtractor.__init__(self, match, url)

        self.gallery_id = match.group(1)
        self.gallery_url = url 
        self.iter_names = True
    
    def items(self):
        self.login()
        page = self.request(self.url, notfound=self.subcategory).text
        data = self.metadata(page)
        page = self.request(self.gallery_url, notfound=self.subcategory).text
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

        info_div = html.find('div', attrs={'id': 'info-block'})

        title_en = info_div.find('h1')

        if title_en:
            if title_en.a:
                data["title_en"] = title_en.a["title"]

        title_jp = info_div.find('h4', attrs={"class" : "gray"})

        if title_jp:
            data["title_jp"] = title_jp.text

        data["title"] = data["title_en"] or data["title_jp"]

        tag_container = info_div.find("section", attrs={"id" : "tags"})

        for tag in tag_container.find_all("div", attrs={"class" : "tag-container field-name"}):
            
            # god this is so ugly 
            # since .text takes all sub html text aswell its kinda like
            # -> characters:\n\n\n 'some character' \n\n\n 'another character'
            # so just split and filter it 
            t = list(filter(None, [i.strip() for i in tag.text.split("\n")]))
            
            # prevent errors 
            if len(t) < 1:
                continue

            # the category only has 1 item and its grouped as 1 string
            if len(t) == 1:
                _ = t[0].split(":") # split them
                key  = _[0].strip() # set the key
                t[0] = _[1]         # item stays the same
                
            else:
                key = t[0].replace(":", "") # removve the : after the category
                del t[0] # remove the category from the list

            data[key] = []

            for i in t:

                if i.find("(") != -1:
                    data[key].append(i[:i.find("(") - 1].strip())
                else:
                    data[key].append(i.strip())
            

        data["gallery_id"] = util.parse_int(self.gallery_id)
        


        self.data = data 
        return data


    def images(self, page):
        """Gets the gallery images"""
        
        images = []
 
        html = BeautifulSoup(page, 'html.parser')

        content = html.find('div', attrs={'id': 'content'})
        page_content = content.find("div", attrs={"id" : "page-container"})
        imgs = page_content.find("textarea", attrs={"id" : "listImgH"}).text.strip()

        # the 'textarea' element above just has a list of all the image urls as a string -> ["","",""...]
        # so just split that and pull from between the "
        for i in imgs.split(","):
            
            m = search(r"\"([^\"\']+)\"", i)

            if not m:
                continue
            
            image_url = m.group(1).replace("\\", "") # they escape / with \ so the urls look like https:\\/\\/ after this gets them
            ext = image_url.rsplit(".", 1)[-1]

            # width and height meta are missing from the gallery page,
            # would require a bunch of requests to get the info without using the api
            images.append((image_url, {"w" : -1, "h" : -1, "extension" : ext}))

        return images
