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

class Echiechikissa_Site_Extractor(Erodoujin_Honpo_Work_Extractor):
    # http://echiechikissa.site/2021/11/19/post-0-157/

    pattern = r"(?:https?://)?echiechikissa\.site/(\d+/\d+/\d+/post-\d+(?:-\d+)?)"
    root = "http://echiechikissa.site"

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
    


# http://hadasirori.blog.jp/archives/%E3%80%90%E6%BF%80%E9%81%B8127%E6%9E%9A%E3%80%91%E3%82%A8%E3%83%83%E3%83%81%E3%81%A7%E5%8F%AF%E6%84%9B%E3%81%84%E3%83%AD%E3%83%AA%E7%BE%8E%E5%B0%91%E5%A5%B3%E3%81%AE%E3%81%9F%E3%81%BE%E3%82%89%E3%81%AA%E3%81%84%E8%B2%A7%E4%B9%B3%E3%81%A0%E3%81%91%E3%81%A9%E7%BE%8E%E4%B9%B3%E3%81%AE%E4%BA%8C%E6%AC%A1%E7%94%BB%E5%83%8F211119.html
# https://nijisenmon.work/archives/hentai_animated_gif-122.html
# http://hadasirori.blog.jp/archives/%E3%80%90%E6%BF%80%E9%81%B8135%E6%9E%9A%E3%80%91%E9%A8%8E%E4%B9%97%E4%BD%8D%E3%82%BB%E3%83%83%E3%82%AF%E3%82%B9%E3%81%A7%E3%82%A8%E3%83%83%E3%83%81%E3%81%AA%E7%B9%8B%E3%81%8C%E3%81%A3%E3%81%A6%E3%82%8B%E3%81%A8%E3%81%93%E4%B8%B8%E8%A6%8B%E3%81%88%E3%81%AA%E3%83%AD%E3%83%AA%E8%B2%A7%E4%B9%B3%E7%BE%8E%E5%B0%91%E5%A5%B3%E3%81%AE%E4%BA%8C%E6%AC%A1%E3%82%A8%E3%83%AD%E7%94%BB%E5%83%8F211119.html
# https://mogiero.blog.fc2.com/blog-entry-62642.html
# http://nijierosuana.site/2021/11/20/post-10629/
# http://kindan-kjt.com/2021/11/20/post-27774/
# http://dochaero.com/2021/11/19/post-28432/
# http://erosoku.work/2021/11/19/post-25067/
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_212919%2F&af_id=dadada123-990&ch=api
# https://mogiero.blog.fc2.com/blog-entry-62645.html
# http://echiechikissa.site/2021/11/19/post-27545/
# https://mogiero.blog.fc2.com/blog-entry-62643.html
# https://nijisenmon.work/archives/hentai_animated_gif-119.html
# http://doujin-susume.work/2021/11/20/post-0-605/
# http://echiechi-navi.xyz/2021/11/20/post-0-814/
# http://doujin-darake.xyz/2021/11/19/post-0-397/
# http://comichara.com/azururen/zara/zara-7
# http://erogakuen.site/2021/11/19/post-149/
# http://nijierosyukai.work/2021/11/20/post-0-639/
# http://nijierosuana.site/2021/11/19/post-0-73/
# http://ero-sogu.work/2021/11/20/post-0-236/
# https://nijifeti.com/physical_reaction/hatsujou/hatsujou-038_1119.html
# http://nijierohomotuko.xyz/2021/11/20/post-0-796/
# http://comichara.com/kantaikorekushon/akagi/akagi-2
# http://ero-sogu.work/2021/11/19/post-24764/
# http://hjanight.site/2021/11/19/post-0-428/
# http://eronijinomori.xyz/2021/11/20/post-2964/
# https://nijisenmon.work/archives/hentai_animated_gif-26.html
# http://ero-road.work/2021/11/19/post-0-229/
# http://nijiero-watch.com/2021/11/19/post-0-354/
# http://situero.com/serifutsuki/serifutsuki-395
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_214299%2F&af_id=dadada123-990&ch=api
# http://choechiechimura.work/2021/11/20/post-0-639/
# http://eronijinomori.xyz/2021/11/20/post-0-80/
# https://www.nijioma.blog/hentai-ananotoriko-j?utm_source=rss&utm_medium=rss&utm_campaign=hentai-ananotoriko-j
# https://gennji.com/post-332491/
# http://eromachi.work/2021/11/19/post-10606/
# http://hjanight.site/2021/11/19/post-0-156/
# https://mogiero.blog.fc2.com/blog-entry-62648.html
# http://doujin-susume.work/2021/11/20/post-0-668/
# http://nijierosyukai.work/2021/11/19/post-27767/
# http://nijierohomotuko.xyz/2021/11/19/post-24544/
# http://ero-sogu.work/2021/11/20/post-18723/
# http://eromachi.work/2021/11/19/post-28333/
# http://comichara.com/onihoronoha/nemameko/nemameko-6
# http://ero-sogu.work/2021/11/20/post-17409/
# https://nijisenmon.work/archives/hentai_animated_gif-25.html
# https://erogazou-march.com/2021/11/19/post-0-315/
# http://echiechi-navi.xyz/2021/11/19/post-0-554/
# http://choechiechimura.work/2021/11/19/post-0-332/
# https://mogiero.blog.fc2.com/blog-entry-62646.html
# http://eroseiiki.xyz/2021/11/20/post-0-184/
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_215930%2F&af_id=dadada123-990&ch=api
# http://echiechikissa.site/2021/11/20/post-0-68/

# https://mogiero.blog.fc2.com/blog-entry-62641.html
# http://nijiero-jimu.work/2021/11/19/post-0-49/
# http://mechasuko.work/2021/11/20/post-25695/
# http://nukigazo.com/kantaikorekushon/urakaze/urakaze-18
# https://erogazou-march.com/2021/11/19/post-0-802/
# http://nijiero-jimu.work/2021/11/20/post-28340/
# https://xn--r8jwklh769h2mc880dk1o431a.com/%e4%ba%8c%e6%ac%a1%e3%82%a8%e3%83%ad%e7%94%bb%e5%83%8f/post-33032
# http://dochaero.com/2021/11/20/post-28330/
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_215538%2F&af_id=dadada123-990&ch=api
# http://dochaero.com/2021/11/20/post-0-62/
# https://xn--r8jwklh769h2mc880dk1o431a.com/%e4%ba%8c%e6%ac%a1%e3%82%a8%e3%83%ad%e7%94%bb%e5%83%8f/post-33029
# http://mechasuko.work/2021/11/19/post-0-619/
# http://erosoku.work/2021/11/19/post-0-775/
# http://ero-sogu.work/2021/11/20/post-18566/
# http://echiechi-navi.xyz/2021/11/19/post-25673/
# http://mechasuko.work/2021/11/19/post-411/
# http://dochaero.com/2021/11/20/post-0-190/
# http://nijierohomotuko.xyz/2021/11/20/post-27543/
# http://mechasuko.work/2021/11/20/post-0-678/
# http://erosoku.work/2021/11/20/post-0-831/
# http://erohakubutukan.work/2021/11/20/post-28014/
# https://nijisenmon.work/archives/hentai_animated_gif-118.html
# http://kindan-kjt.com/2021/11/20/post-0-809/
# http://nijiero-watch.com/2021/11/20/post-25328/
# http://hjanight.site/2021/11/20/post-25517/
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_213203%2F&af_id=dadada123-990&ch=api
# http://eroseiiki.xyz/2021/11/19/post-198/
# http://moeimg.net/16856.html
# https://mogiero.blog.fc2.com/blog-entry-62644.html
# http://loveliveforever.com/paimoro/paimoro-15
# http://erodoujin-honpo.work/2021/11/20/post-0-878/
# http://echiechikissa.site/2021/11/20/post-26361/
# https://sexuad.blog.fc2.com/e/nijigen-ero-vtuber-siranui
# http://ero-road.work/2021/11/19/post-0-760/
# http://nijierosyukai.work/2021/11/20/post-27876/
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_215936%2F&af_id=dadada123-990&ch=api
# https://nijisenmon.work/archives/hentai_animated_gif-24.html
# http://choechiechimura.work/2021/11/19/post-25275/
# http://nukigazo.com/kantaikorekushon/musashi/musashi-19
# https://nijisenmon.work/archives/post-19922.html
# http://choechiechimura.work/2021/11/20/post-240-2/
# http://nikkan-doujin.work/2021/11/19/post-0-418/
# http://situero.com/kijoukurai/kijoukurai-20
# http://ero-road.work/2021/11/20/post-0-741/
# http://ero-sogu.work/2021/11/20/post-18688/
# http://pink-world.site/2021/11/19/post-0-533/
# http://nijierosyukai.work/2021/11/20/post-24449/
# http://ero-road.work/2021/11/20/post-27243/
# http://mechasuko.work/2021/11/19/post-0-781/
# http://eroseiiki.xyz/2021/11/19/post-0-12/
# http://erohakubutukan.work/2021/11/19/post-28013/
# http://mechasuko.work/2021/11/19/post-0-938/
# http://doujin-darake.xyz/2021/11/20/post-0-406/
# http://nukigazo.com/kantaikorekushon/kashima/kashima-17
# http://ero-sogu.work/2021/11/19/post-16893/
# https://kimootoko.net/archives/52258068.html
# http://kindan-kjt.com/2021/11/19/post-0-92/
# http://eronijinomori.xyz/2021/11/20/post-3022/
# http://nijierosuana.site/2021/11/19/post-0-463/
# http://ero-sogu.work/2021/11/20/post-26295/
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_214562%2F&af_id=dadada123-990&ch=api
# http://choechiechimura.work/2021/11/20/post-0-818/
# https://nijisenmon.work/archives/hentai_animated_gif-120.html
# http://edj-fan.xyz/2021/11/20/post-10831/
# http://nikkan-doujin.work/2021/11/20/post-0-763/
# https://erokan.net/archives/329732
# http://erodoujin-zanmai.xyz/2021/11/19/post-27315/
# http://nukigazo.com/kantaikorekushon/aiowa/aiowa-21
# http://pink-world.site/2021/11/20/post-27237/
# http://eronijinomori.xyz/2021/11/20/post-3040/
# http://hjanight.site/2021/11/20/post-0-619/
# http://erogakuen.site/2021/11/20/post-0-629/
# http://eronijinomori.xyz/2021/11/19/post-20103/
# http://nijiero-jimu.work/2021/11/19/post-0-523/
# http://moeimg.net/16857.html
# http://echiechikissa.site/2021/11/20/post-26760/
# http://erohakubutukan.work/2021/11/20/post-28016/
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_214501%2F&af_id=dadada123-990&ch=api
# http://nijierohomotuko.xyz/2021/11/19/post-26709/
# http://erocon.gger.jp/archives/25718564.html
# http://comichara.com/kantaikorekushon/yuudachi/yuudachi-4
# http://hadasirori.blog.jp/archives/%E3%80%90%E6%BF%80%E9%81%B8170%E6%9E%9A%E3%80%91%E3%83%AD%E3%83%AA%E7%BE%8E%E5%B0%91%E5%A5%B3%E3%81%8C%E3%82%A2%E3%83%8A%E3%83%AB%E3%81%AB%E3%81%8A%E3%81%A1%E3%82%93%E3%81%A1%E3%82%93%E6%8C%BF%E3%82%8C%E3%82%89%E3%82%8C%E3%81%A6%E3%82%BB%E3%83%83%E3%82%AF%E3%82%B9%E3%81%8C%E3%82%A8%E3%83%AD%E3%81%84%E4%BA%8C%E6%AC%A1%E7%94%BB%E5%83%8F211119.html
# http://erogakuen.site/2021/11/20/post-6/
# http://pink-world.site/2021/11/20/post-0-1027/
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_215419%2F&af_id=dadada123-990&ch=api
# http://nijierosuana.site/2021/11/20/post-0-105/
# http://nikkan-doujin.work/2021/11/20/post-0-237/
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_214935%2F&af_id=dadada123-990&ch=api
# http://doujin-darake.xyz/2021/11/19/post-0-590/
# http://comichara.com/kantaikorekushon/akitsumaru/akitsumaru-2
# http://erodoujin-biyori.work/2021/11/20/post-0-666/
# http://doujin-darake.xyz/2021/11/20/post-0-859/
# http://erodoujin-zanmai.xyz/2021/11/20/post-0-140/
# https://erogazou-march.com/2021/11/20/post-159/
# https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_215100%2F&af_id=dadada123-990&ch=api
# http://nijierosyukai.work/2021/11/19/post-0-502/
# http://nijiero-jimu.work/2021/11/20/post-28232/
# http://eromachi.work/2021/11/20/post-0-728/
# http://erodoujin-mecca.xyz/2021/11/19/post-0-229/
# http://erodoujin-biyori.work/2021/11/19/post-0-469/
# http://echiechi-navi.xyz/2021/11/20/post-0-161/
# http://nijiero-watch.com/2021/11/20/post-0-60/
# http://nijierohomotuko.xyz/2021/11/20/post-24432/
# http://eronijinomori.xyz/2021/11/20/post-18777/
# http://eroseiiki.xyz/2021/11/20/post-0-637/
# http://nijiero-watch.com/2021/11/19/post-122/
# http://nikkan-doujin.work/2021/11/19/post-25424/
# http://erodoujin-zanmai.xyz/2021/11/20/post-25500/
# http://edj-fan.xyz/2021/11/19/post-0-83/
# https://mogiero.blog.fc2.com/blog-entry-62640.html
# http://ero-okazu.work/2021/11/19/post-10739/
# https://nijisenmon.work/archives/hentai_animated_gif-121.html
# http://ero-okazu.work/2021/11/19/post-0-864/
# http://eronijinomori.xyz/2021/11/19/post-22894/
# http://pink-world.site/2021/11/20/post-0-679/
# http://edj-fan.xyz/2021/11/19/post-0-970/
# http://erohakubutukan.work/2021/11/20/post-28015/
# http://edj-fan.xyz/2021/11/20/post-0-919/
# http://pink-world.site/2021/11/19/post-162-3/
# http://kindan-kjt.com/2021/11/19/post-0-26/
# http://erogakuen.site/2021/11/20/post-24768/
# http://mechasuko.work/2021/11/20/post-386/
# http://nijiero-watch.com/2021/11/20/post-0-652/
# http://doujin-susume.work/2021/11/20/post-0-667/
# http://dochaero.com/2021/11/19/post-423/
# http://comichara.com/aidorumasuta/kazenotomoshibishoku/kazenotomoshibishoku-5
# http://erohakubutukan.work/2021/11/19/post-28012/
# https://erogazou-march.com/2021/11/20/post-0-222/
# http://hjanight.site/2021/11/20/post-0-265/
# http://eronijinomori.xyz/2021/11/19/post-20081/
# http://ero-okazu.work/2021/11/19/post-0-224/

# class NhentaiGalleryExtractor(NhentaiBase, GalleryExtractor):
#     """Extractor for image galleries from nhentai.net"""

#     pattern = r"(?:https?://)?nhentai\.io/([^\/]*)"


#     def __init__(self, match, use_api = False):

#         url = self.root + "/" + match.group(1)
        
#         self.use_api = use_api
#         GalleryExtractor.__init__(self, match, url)

#         self.iter_names = True


#     def items(self):
#         self.login()
#         page = self.request(self.gallery_url, notfound=self.subcategory).text
#         data = self.metadata(page)
#         page = self.request(self.gallery_url + "/read/", notfound=self.subcategory).text
#         imgs = self.images(page)

#         if "count" in data:
#             if self.config("page-reverse"):
#                 images = util.enumerate_reversed(imgs, 1, data["count"])

#             else:
#                 images = zip(range(1, data["count"] + 1), imgs)

#         else:
#             try:
#                 data["count"] = len(imgs)
#             except TypeError:
#                 pass
            
#             if self.config("page-reverse"):
#                 images = util.enumerate_reversed(imgs, 1)

#             else:
#                 images = enumerate(imgs, 1)


#         yield Message.Directory, data

#         # compute the z_fill once even if its not used
#         z_fill = len(str(data["count"]))

#         for i, (url, imgdata) in images:
#             util.add_nameext_from_url(url, imgdata)
            
#             if self.iter_names:
#                 imgdata["filename"] = "{}".format(i).zfill(z_fill)

#             yield Message.Url, url, imgdata


#     def metadata(self, page):
#         html = BeautifulSoup(page, 'html.parser')
#         data = {}

#         info_div = html.find('div', attrs={'id': 'info'})

#         data["title"] = info_div.find('h1').text

#         p_title = info_div.find('h1').find('span', attrs={'class': 'pretty'})
#         data["title_pretty"] = p_title.text if p_title else ""
        
#         subtitle = info_div.find('h2')
#         data["subtitle"] = subtitle.text if subtitle else ""

#         data["gallery_id"] = -1

#         needed_fields = [
#             'Characters', 'Artists', 'Languages', 'Pages',
#             'Tags', 'Parodies', 'Groups', 'Categories'
#             ]
        
#         for field in info_div.find_all('div', attrs={'class': 'field-name'}):

#             field_name = field.contents[0].strip().strip(':')

#             if field_name in needed_fields:
#                 dat = [s.find('span', attrs={'class': 'name'}).contents[0].strip() for s in field.find_all('a', attrs={'class': 'tag'})]
#                 data[field_name.lower()] = ', '.join(dat)

#         time_field = info_div.find('time')
#         if time_field.has_attr('datetime'):
#             data['uploaded'] = time_field['datetime']

#         self.data = data 
#         return data


#     def images(self, page):
#         """Gets the gallery images"""
        
#         images = []
 
#         html = BeautifulSoup(page, 'html.parser')

#         doujinshi_cover = html.find('div', attrs={'class': 'readimg'})

#         index = 0
#         for i in doujinshi_cover.find_all('img'):
#             index += 1
#             image_url = i.attrs['src']
#             ext = image_url.rsplit(".", 1)[-1]

#             # width and height meta are missing from the gallery page,
#             # would require a bunch of requests to get the info without using the api
#             images.append((image_url, {"w" : -1, "h" : -1, "extension" : ext}))

#         return images
