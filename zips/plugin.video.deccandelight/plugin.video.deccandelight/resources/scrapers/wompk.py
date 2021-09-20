'''
DeccanDelight scraper plugin
Copyright (C) 2019 gujal

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
from six.moves import urllib_parse, html_parser
import requests
import re


class wompk(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.moviesmanha.com/category/'
        self.icon = self.ipath + 'wompk.png'
        self.list = {'01Hindi Movies': 'indian movies',
                     '02Hindi Dubbed Movies': 'hindi dubbed movies',
                     '03English Movies': 'english',
                     '04Movies By Actor': 'movies by actors',
                     '05Movies By Actress': 'movies by actress',
                     '06Movies By Type': 'by type',
                     '07Punjabi': self.bu + 'watch-punjabi-movies-online/MMMM7',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s=MMMM7'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of categories.
        """
        cats = []
        page = requests.get(self.bu[:-9], headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': re.compile('^menu-shahbaz')})
        mdiv = BeautifulSoup(page, "html.parser", parse_only=mlink)

        submenus = mdiv.find_all('li', {'class': re.compile('^menu-item')})
        for submenu in submenus:
            if iurl in submenu.find('a').text.lower():
                break

        items = submenu.find_all('li')
        for item in items:
            title = item.text
            url = item.find('a')['href']
            # url = url if url.startswith('http') else self.bu[:-9] + url
            cats.append((title, self.icon, url))

        return (cats, 7)

    def get_items(self, url):
        h = html_parser.HTMLParser()
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Movie Manha')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text
        if '?s=' in url:
            mlink = SoupStrainer('div', {'class': 'postcont'})
        else:
            mlink = SoupStrainer('div', {'class': 'contentbg'})
        html = requests.get(url, headers=self.hdr).text
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'wp-pagenavi'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': 'postbox'})

        for item in items:
            try:
                title = item.find('a')['title']
                title = self.clean_title(title)
            except:
                tdiv = item.find('div', {'class': 'title'})
                title = h.unescape(tdiv.a.text)
                title = title.encode('utf8') if self.PY2 else title
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['data-src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            purl = Paginator.find('a', {'class': 'nextpostslink'}).get('href')
            currpg = Paginator.find('span', {'class': 'current'}).text
            lastpg = Paginator.find('a', {'class': 'last'}).get('href').split('/')[-2] if Paginator.find('a', {'class': 'last'}) else Paginator.find_all('a', {'class': 'page larger'})[-1].text
            title = 'Next Page.. (Currently in Page {} of {})'.format(currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        """
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'id': 'singlecont'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        url = mdiv.find('table').nextSibling.find('a')['href']
        """
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'singcont'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        links = mdiv.find_all('iframe')

        for link in links:
            try:
                vidurl = link.get('src')
                vidurl = vidurl if vidurl.startswith('http') else 'https:' + vidurl
                self.resolve_media(vidurl, videos)
            except:
                pass

        return videos
