'''
DeccanDelight scraper plugin
Copyright (C) 2016 gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
from resources.lib.base import Scraper
from bs4 import BeautifulSoup, SoupStrainer
from six.moves import html_parser
import re
import requests


class torm(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://tormalayalam.xyz'
        self.icon = self.ipath + 'torm.png'
        self.list = {'01Movies': self.bu + '/movies'}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        h = html_parser.HTMLParser()
        movies = []

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'itemList'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'k2Pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('span', {'class': 'catItemImage'})

        for item in items:
            title = h.unescape(item.find('a')['title'])
            title = title.encode('utf8') if self.PY2 else title
            url = self.bu + item.find('a')['href']
            thumb = self.bu + item.find('img')['src']
            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            pdiv = Paginator.find('a', {'class': 'next'})
            purl = self.bu + pdiv.get('href')
            pgtxt = re.findall(r'(Page\s[^<]+)', Paginator.text)[0].strip()
            title = 'Next Page.. (Currently in %s)' % pgtxt
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'itemFullText'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            vidurl = re.findall('Watch Online:.+?href="([^"]+)', html, re.DOTALL)[0]
            self.resolve_media(vidurl, videos)
        except:
            pass

        try:
            links = videoclass.find_all('div', {'class': 'avPlayerContainer'})
            for link in links:
                vidurl = link.find('iframe')['src']
                if 'http' not in vidurl:
                    vidurl = 'http:' + vidurl
                self.resolve_media(vidurl, videos)
        except:
            pass

        try:
            table = videoclass.find('div', {'class': 'divTable'})
            links = table.find_all('a')
            for link in links:
                vidurl = link.get('href')
                self.resolve_media(vidurl, videos)
        except:
            pass

        try:
            table = videoclass.find('table')
            links = table.find_all('a')
            for link in links:
                vidurl = link.get('href')
                self.resolve_media(vidurl, videos)
        except:
            pass

        return videos
