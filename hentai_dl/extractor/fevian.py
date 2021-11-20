# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nhentai.io/"""

from bs4 import BeautifulSoup

from .common import GalleryExtractor, Message
from .. import util


class FevianBase():
    """Base class for fevian extractors"""
    category = "fevian"

class Sexuad_Blog_FC2_Extractor(GalleryExtractor, FevianBase):
    # https://sexuad.blog.fc2.com/e/nijigen-ero-kimetu-kanroji
    
    pattern = r"(?:https?://)?sexuad\.blog\.fc2\.com/e/([^\/]*)"
    root = "https://sexuad.blog.fc2.com/e"

    def __init__(self, match, use_api = False):

        url = self.root + "/" + match.group(1)
        
        self.use_api = False
        GalleryExtractor.__init__(self, match, url)

        self.iter_names = True

    
    def metadata(self, page):
        html = BeautifulSoup(page, 'html.parser')
        data = {}

        data["title"] = html.find('h1', attrs={"id" : "entry_header-title"}).text.strip()

        data["gallery_id"] = -1

        self.data = data 
        return data


    def images(self, page):
        """Gets the gallery images"""
        
        images = []
 
        html = BeautifulSoup(page, 'html.parser')

        main = html.find("div", attrs={"class" : "inner-contents"}).div

        for div in main.find_all("a"):
            if div.img:
                ext = util.get_url_ext(div.img["src"])
                images.append((div.img["src"], {"w" : -1, "h" : -1, "extension" : ext}))

        return images

# all these pages have the same html layout 
class Erodoujin_Honpo_Work_Extractor(GalleryExtractor, FevianBase):
    # http://erodoujin-honpo.work/2021/11/20/post-25567/
    
    pattern = r"(?:https?://)?erodoujin\-honpo\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://erodoujin-honpo.work"

    def __init__(self, match, use_api = False):

        url = self.root + "/" + match.group(1)
        
        self.use_api = False
        GalleryExtractor.__init__(self, match, url)

        self.iter_names = True

    
    def metadata(self, page):
        html = BeautifulSoup(page, 'html.parser')
        data = {}

        data["title"] = html.find('h1', attrs={"class" : "entry-title"}).text.strip()

        data["gallery_id"] = util.parse_int(self.url.rsplit("-", 1)[-1], -1)

        self.data = data 
        return data


    def images(self, page):
        """Gets the gallery images"""
        
        images = []
 
        html = BeautifulSoup(page, 'html.parser')

        main = html.find("div", attrs={"id" : "the-content"})

        for div in main.find_all("div", attrs={"class" : "t_b"}):
            if div.img:
                ext = util.get_url_ext(div.img["src"])
                images.append((div.img["src"], {"w" : -1, "h" : -1, "extension" : ext}))
        

        return images

class Erodoujin_Zanmai_XYZ_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://erodoujin-zanmai.xyz/2021/11/20/post-131/
    
    pattern = r"(?:https?://)?erodoujin\-zanmai\.xyz/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "http://erodoujin-zanmai.xyz"

class Erodoujin_Mecca_XYZ_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://erodoujin-mecca.xyz/2021/11/20/post-0-523/

    pattern = r"(?:https?://)?erodoujin\-mecca\.xyz/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "http://erodoujin-mecca.xyz"

class Erodoujin_Biyori_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://erodoujin-biyori.work/2021/11/19/post-0-904/

    pattern = r"(?:https?://)?erodoujin\-biyori\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "http://erodoujin-biyori.work"

class Eromachi_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://eromachi.work/2021/11/20/post-0-876/

    pattern = r"(?:https?://)?eromachi\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "http://eromachi.work"

class Erogazou_March_Extractor(Erodoujin_Honpo_Work_Extractor):
    # https://erogazou-march.com/2021/11/20/post-28104/

    pattern = r"(?:https?://)?erogazou\-march\.com/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "http://erogazou-march.com"

class Nijierohomotuko_Extractor(Erodoujin_Honpo_Work_Extractor):
    # https://nijierohomotuko.xyz/2021/11/20/post-24432/
    
    pattern = r"(?:https?://)?nijierohomotuko\.xyz/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://nijierohomotuko.xyz"

class Erogakuen_Site_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://erogakuen.site/2021/11/19/post-26734/
    
    pattern = r"(?:https?://)?erogakuen\.site/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://erogakuen.site"
    
class Eronijinomori_XYX_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://eronijinomori.xyz/2021/11/19/post-21609/
    
    pattern = r"(?:https?://)?eronijinomori\.xyz/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://eronijinomori.xyz"
    
class Ero_Sogu_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://ero-sogu.work/2021/11/19/post-0-95/
    
    pattern = r"(?:https?://)?ero\-sogu\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://ero-sogu.work"
    
class Erodoujinch_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://erodoujinch.work/2021/11/20/post-18150/
    
    pattern = r"(?:https?://)?erodoujinch\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://erodoujinch.work"
    
class Kindan_Kjt_Com_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://kindan-kjt.com/2021/11/20/post-27774/
    
    pattern = r"(?:https?://)?kindan\-kjt\.com/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://kindan-kjt.com"

class Dochaero_Com_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://dochaero.com/2021/11/19/post-28432/
    
    pattern = r"(?:https?://)?dochaero\.com/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://dochaero.com"

class Nijierosuana_Site_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://nijierosuana.site/2021/11/20/post-10629/
    
    pattern = r"(?:https?://)?nijierosuana\.site/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://nijierosuana.site"

class Echiechikissa_Site_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://echiechikissa.site/2021/11/19/post-27545/
    
    pattern = r"(?:https?://)?echiechikissa\.site/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://echiechikissa.site"

class Erosoku_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://erosoku.work/2021/11/19/post-25067/
    
    pattern = r"(?:https?://)?erosoku\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://erosoku.work"

class Echiechi_Navi_XYZ_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://echiechi-navi.xyz/2021/11/20/post-0-814/
    
    pattern = r"(?:https?://)?echiechi\-navi\.xyz/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://echiechi-navi.xyz"

class Doujin_Susume_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://doujin-susume.work/2021/11/20/post-0-605/
    
    pattern = r"(?:https?://)?doujin\-susume\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://doujin-susume.work"

class Doujin_Darake_XYZ_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://doujin-darake.xyz/2021/11/19/post-0-397/
    
    pattern = r"(?:https?://)?doujin\-darake\.xyz/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://doujin-darake.xyz"

class Nijierosyukai_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://nijierosyukai.work/2021/11/20/post-0-639/
    
    pattern = r"(?:https?://)?nijierosyukai\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://nijierosyukai.work"

class Njanight_Site_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://hjanight.site/2021/11/19/post-0-428/
    
    pattern = r"(?:https?://)?hjanight\.site/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://hjanight.site"

class Nijiero_Watch_Com_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://nijiero-watch.com/2021/11/19/post-0-354/
    
    pattern = r"(?:https?://)?nijiero\-watch\.com/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://nijiero-watch.com"

class Ero_Road_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://ero-road.work/2021/11/19/post-0-229/
    
    pattern = r"(?:https?://)?ero\-road\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://ero-road.work"

class Choechiechimura_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://choechiechimura.work/2021/11/20/post-0-639/
    
    pattern = r"(?:https?://)?choechiechimura\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://choechiechimura.work"

class Eroseiiki_XYZ_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://eroseiiki.xyz/2021/11/20/post-0-184/
    
    pattern = r"(?:https?://)?eroseiiki\.xyz/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://eroseiiki.xyz"

class Nijiero_Jiumu_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://nijiero-jimu.work/2021/11/19/post-0-49/
    
    pattern = r"(?:https?://)?nijiero\-jimu\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://nijiero-jimu.work"

class Mechasuko_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://mechasuko.work/2021/11/19/post-0-619/
    
    pattern = r"(?:https?://)?mechasuko\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://mechasuko.work"

class Erohakubutukan_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://erohakubutukan.work/2021/11/20/post-28014/
    
    pattern = r"(?:https?://)?erohakubutukan\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://erohakubutukan.work"

class Erodoujin_Honpo_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://erodoujin-honpo.work/2021/11/20/post-0-878/
    
    pattern = r"(?:https?://)?erodoujin\-honpo\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://erodoujin-honpo.work"

class Nikkan_Doujin_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://nikkan-doujin.work/2021/11/19/post-0-418/
    
    pattern = r"(?:https?://)?nikkan\-doujin\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://nikkan-doujin.work"

class Pink_World_Site_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://pink-world.site/2021/11/19/post-0-533/
    
    pattern = r"(?:https?://)?pink\-world\.site/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://pink-world.site"

class Edj_Fan_XYZ_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://edj-fan.xyz/2021/11/20/post-10831/
    
    pattern = r"(?:https?://)?edj\-fan\.xyz/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://edj-fan.xyz"

class Ero_Okazu_Work_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://ero-okazu.work/2021/11/19/post-10739/
    
    pattern = r"(?:https?://)?ero\-okazu\.work/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "https://ero-okazu.work"

# http://ero-okazu.work/2021/11/19/post-0-864/
# http://kindan-kjt.com/2021/11/19/post-0-26/
# http://doujin-susume.work/2021/11/20/post-0-667/
# http://ero-okazu.work/2021/11/19/post-0-224/

# http://comichara.com/aidorumasuta/kazenotomoshibishoku/kazenotomoshibishoku-5
# https://nijisenmon.work/archives/hentai_animated_gif-121.html
# https://nijisenmon.work/archives/hentai_animated_gif-120.html
# https://mogiero.blog.fc2.com/blog-entry-62640.html
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_215100%2F&af_id=dadada123-990&ch=api
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_214935%2F&af_id=dadada123-990&ch=api
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_214562%2F&af_id=dadada123-990&ch=api
# http://nukigazo.com/kantaikorekushon/musashi/musashi-19
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_215419%2F&af_id=dadada123-990&ch=api
# http://hadasirori.blog.jp/archives/%E3%80%90%E6%BF%80%E9%81%B8170%E6%9E%9A%E3%80%91%E3%83%AD%E3%83%AA%E7%BE%8E%E5%B0%91%E5%A5%B3%E3%81%8C%E3%82%A2%E3%83%8A%E3%83%AB%E3%81%AB%E3%81%8A%E3%81%A1%E3%82%93%E3%81%A1%E3%82%93%E6%8C%BF%E3%82%8C%E3%82%89%E3%82%8C%E3%81%A6%E3%82%BB%E3%83%83%E3%82%AF%E3%82%B9%E3%81%8C%E3%82%A8%E3%83%AD%E3%81%84%E4%BA%8C%E6%AC%A1%E7%94%BB%E5%83%8F211119.html
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_214501%2F&af_id=dadada123-990&ch=api
# http://comichara.com/kantaikorekushon/akitsumaru/akitsumaru-2
# http://comichara.com/kantaikorekushon/yuudachi/yuudachi-4
# http://moeimg.net/16857.html
# https://kimootoko.net/archives/52258068.html
# https://erokan.net/archives/329732
# http://erocon.gger.jp/archives/25718564.html
# http://nukigazo.com/kantaikorekushon/aiowa/aiowa-21
# https://nijisenmon.work/archives/hentai_animated_gif-118.html
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_213203%2F&af_id=dadada123-990&ch=api
# http://moeimg.net/16856.html
# https://mogiero.blog.fc2.com/blog-entry-62644.html
# http://loveliveforever.com/paimoro/paimoro-15
# https://sexuad.blog.fc2.com/e/nijigen-ero-vtuber-siranui
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_215936%2F&af_id=dadada123-990&ch=api
# https://nijisenmon.work/archives/hentai_animated_gif-24.html
# http://hadasirori.blog.jp/archives/%E3%80%90%E6%BF%80%E9%81%B8127%E6%9E%9A%E3%80%91%E3%82%A8%E3%83%83%E3%83%81%E3%81%A7%E5%8F%AF%E6%84%9B%E3%81%84%E3%83%AD%E3%83%AA%E7%BE%8E%E5%B0%91%E5%A5%B3%E3%81%AE%E3%81%9F%E3%81%BE%E3%82%89%E3%81%AA%E3%81%84%E8%B2%A7%E4%B9%B3%E3%81%A0%E3%81%91%E3%81%A9%E7%BE%8E%E4%B9%B3%E3%81%AE%E4%BA%8C%E6%AC%A1%E7%94%BB%E5%83%8F211119.html
# https://nijisenmon.work/archives/hentai_animated_gif-122.html
# http://hadasirori.blog.jp/archives/%E3%80%90%E6%BF%80%E9%81%B8135%E6%9E%9A%E3%80%91%E9%A8%8E%E4%B9%97%E4%BD%8D%E3%82%BB%E3%83%83%E3%82%AF%E3%82%B9%E3%81%A7%E3%82%A8%E3%83%83%E3%83%81%E3%81%AA%E7%B9%8B%E3%81%8C%E3%81%A3%E3%81%A6%E3%82%8B%E3%81%A8%E3%81%93%E4%B8%B8%E8%A6%8B%E3%81%88%E3%81%AA%E3%83%AD%E3%83%AA%E8%B2%A7%E4%B9%B3%E7%BE%8E%E5%B0%91%E5%A5%B3%E3%81%AE%E4%BA%8C%E6%AC%A1%E3%82%A8%E3%83%AD%E7%94%BB%E5%83%8F211119.html
# https://mogiero.blog.fc2.com/blog-entry-62642.html
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_212919%2F&af_id=dadada123-990&ch=api
# https://mogiero.blog.fc2.com/blog-entry-62645.html
# https://mogiero.blog.fc2.com/blog-entry-62643.html
# https://nijisenmon.work/archives/hentai_animated_gif-119.html
# http://comichara.com/azururen/zara/zara-7
# https://nijifeti.com/physical_reaction/hatsujou/hatsujou-038_1119.html
# http://comichara.com/kantaikorekushon/akagi/akagi-2
# https://nijisenmon.work/archives/hentai_animated_gif-26.html
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_214299%2F&af_id=dadada123-990&ch=api
# https://www.nijioma.blog/hentai-ananotoriko-j?utm_source=rss&utm_medium=rss&utm_campaign=hentai-ananotoriko-j
# https://mogiero.blog.fc2.com/blog-entry-62648.html
# http://comichara.com/onihoronoha/nemameko/nemameko-6
# https://nijisenmon.work/archives/hentai_animated_gif-25.html
# https://mogiero.blog.fc2.com/blog-entry-62646.html
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_215930%2F&af_id=dadada123-990&ch=api

# https://mogiero.blog.fc2.com/blog-entry-62641.html
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_215538%2F&af_id=dadada123-990&ch=api
# http://nukigazo.com/kantaikorekushon/urakaze/urakaze-18

# http://nukigazo.com/kantaikorekushon/kashima/kashima-17

# http://situero.com/serifutsuki/serifutsuki-395
# https://gennji.com/post-332491/

# https://xn--r8jwklh769h2mc880dk1o431a.com/%e4%ba%8c%e6%ac%a1%e3%82%a8%e3%83%ad%e7%94%bb%e5%83%8f/post-33032
# https://xn--r8jwklh769h2mc880dk1o431a.com/%e4%ba%8c%e6%ac%a1%e3%82%a8%e3%83%ad%e7%94%bb%e5%83%8f/post-33029
# https://nijisenmon.work/archives/post-19922.html
# http://situero.com/kijoukurai/kijoukurai-20
