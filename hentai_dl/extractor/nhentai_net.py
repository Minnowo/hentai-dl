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


class NhentaiBase():
    """Base class for nhentai extractors"""
    category = "nhentai"
    root = "https://nhentai.net"
    media_url = "https://i.nhentai.net"


class NhentaiGalleryExtractor(NhentaiBase, GalleryExtractor):
    """Extractor for image galleries from nhentai.net"""

    pattern = r"(?:https?://)?nhentai\.net/g/(\d+)"


    def __init__(self, match, use_api = False):

        if use_api:
            url = self.root + "/api/gallery/" + match.group(1)

        else:
            url = self.root + "/g/" + match.group(1)
        
        self.use_api = use_api
        GalleryExtractor.__init__(self, match, url)

        self.iter_names = True


    def metadata(self, page):
        
        if self.use_api:
            return self.metadata_api(page)

        return self.metadata_scrape(page)

    def metadata_api(self, page):
        self.data = data = json.loads(page)

        title_en = data["title"].get("english", "")
        title_ja = data["title"].get("japanese", "")

        info = collections.defaultdict(list)
        for tag in data["tags"]:
            info[tag["type"]].append(tag["name"])

        language = ""
        for language in info["language"]:
            if language != "translated":
                language = language.capitalize()
                break

        return {
            "title"     : title_en or title_ja,
            "title_en"  : title_en,
            "title_ja"  : title_ja,
            "gallery_id": data["id"],
            "media_id"  : util.parse_int(data["media_id"]),
            "date"      : data["upload_date"],
            "scanlator" : data["scanlator"],
            "artist"    : info["artist"],
            "group"     : info["group"],
            "parody"    : info["parody"],
            "characters": info["character"],
            "tags"      : info["tag"],
            "type"      : info["category"][0] if info["category"] else "",
            "lang"      : util.language_to_code(language),
            "language"  : language,
        } 

    def metadata_scrape(self, page):
        
        html = BeautifulSoup(page, 'html.parser')
        data = {}

        info_div = html.find('div', attrs={'id': 'info'})

        data["title"] = info_div.find('h1').text
        data["title_pretty"] = info_div.find('h1').find('span', attrs={'class': 'pretty'}).text
        
        subtitle = info_div.find('h2')
        data["subtitle"] = subtitle.text if subtitle else ""

        data["gallery_id"] = util.parse_int(info_div.find("h3", attrs={"id" : "gallery_id"}).text)

        doujinshi_cover = html.find('div', attrs={'id': 'cover'})
        data["media_id"] = util.parse_int(search('/galleries/([0-9]+)/cover.(jpg|png|gif)$',doujinshi_cover.a.img.attrs['data-src']).group(1))        

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

        if self.use_api:
            return self.image_api()

        return self.image_scrape(page)

    def image_api(self):
        """Gets all the gallery images from the api"""

        ufmt = "{}/galleries/{}/{{}}.{{}}".format(self.media_url, self.data["media_id"])
        extdict = {"j": "jpg", "p": "png", "g": "gif"}

        return [
            (ufmt.format(
                num, 
                extdict.get(img["t"], "jpg")), 
                {"width": img["w"], "height": img["h"], "extension" : extdict.get(img["t"], "jpg")}
                ) for num, img in enumerate(self.data["images"]["pages"], 1)] 

    def image_scrape(self, page):
        """Gets all gallery images from the web source"""

        images = []
 
        html = BeautifulSoup(page, 'html.parser')

        doujinshi_cover = html.find('div', attrs={'id': 'cover'})
        img_id = search('/galleries/([0-9]+)/cover.(jpg|png|gif)', str(doujinshi_cover.a.img)).group(1)

        index = 0
        for i in html.find_all('div', attrs={'class': 'thumb-container'}):
            index += 1
            thumb_url = i.img.attrs['data-src']
            ext = thumb_url.rsplit(".", 1)[-1]
            # "https://i.nhentai.net" + / + galleries + / + xxxxx + / xxx.ext
            image_url = "%s/galleries/%s/%d.%s" % (self.media_url, img_id, index, ext)

            # width and height meta are missing from the gallery page,
            # would require a bunch of requests to get the info without using the api
            images.append((image_url, {"w" : -1, "h" : -1, "extension" : ext}))

        return images


class NhentaiGalleryGalleryExtractorBase(NhentaiBase, GalleryExtractor):

    sub = ""

    def __init__(self, match, use_api = False):

        url = self.root + self.sub + match.group(1) + "?page={PAGE}"
        
        self.use_api = use_api
        GalleryExtractor.__init__(self, match, url)

        self.url = url 

        self.iter_names = True

    def items(self):
        
        page = 1
        gallery_urls = set()

        while True:
            url = self.url.format(PAGE=str(page))

            response = self.request(url, fatal=False)

            soup = BeautifulSoup(response.content, "html.parser")

            content = soup.find("div", attrs={"id" : "content"})
            container = content.find("div", attrs={"class" : "container index-container"})

            h3 = container.find("h3")

            if h3:
                if h3.text == "No results, sorry.":
                    self.log.info(f"no more pages found. {page} total pages found.")
                    break 

            self.log.info("extracting page: " + url)

            for div in container.find_all("div", attrs={"class" : "gallery"}):

                if div.a:
                    g_url = self.root + div.a["href"]
                    gallery_urls.add(match(NhentaiGalleryExtractor.pattern, g_url))
            
            page += 1

        for i in gallery_urls:

            if i:

                yield Message.Queue, NhentaiGalleryExtractor(i, self.use_api)


class NhentaiGroupExtractor(NhentaiGalleryGalleryExtractorBase):
    """Extractor for groups (downloads EVERY gallery under the group)"""

    pattern = r"(?:https?://)?nhentai\.net/group/([^\/]+/)"
    sub = "/group/"

class NhentaiArtistExtractor(NhentaiGalleryGalleryExtractorBase):
    """Extractor for artists (downloads EVERY gallery under the artist)"""

    pattern = r"(?:https?://)?nhentai\.net/artist/([^\/]+/)"
    sub = "/artist/"

class NhentaiTagExtractor(NhentaiGalleryGalleryExtractorBase):
    """Extractor for tags (downloads EVERY gallery under the tag)"""
    
    pattern = r"(?:https?://)?nhentai\.net/tag/([^\/]+/)"
    sub = "/tag/"

class NhentaiCharacterExtractor(NhentaiGalleryGalleryExtractorBase):
    """Extractor for characters (downloads EVERY gallery under the character)"""
    
    pattern = r"(?:https?://)?nhentai\.net/character/([^\/]+/)"
    sub = "/character/"

class NhentaiCharacterExtractor(NhentaiGalleryGalleryExtractorBase):
    """Extractor for parody (downloads EVERY gallery under the parody)"""
    
    pattern = r"(?:https?://)?nhentai\.net/parody/([^\/]+/)"
    sub = "/parody/"

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
