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
from six.moves import urllib_parse, html_parser
import re
import requests
import json


class tgun(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://tamilgun.tw/'
        self.icon = self.ipath + 'tgun.png'

    def get_menu(self):
        h = html_parser.HTMLParser()
        r = requests.get(self.bu, headers=self.hdr)
        if r.url != self.bu:
            self.bu = r.url
        items = {}
        cats = re.findall('id="menu-item-(?!4|5404|6147|13047).*?href="((?=.*categories).*?)">((?!User).*?)<', r.text)
        sno = 1
        for url, title in cats:
            title = h.unescape(title)
            title = title.encode('utf8') if self.PY2 else title
            items['{:02d}'.format(sno) + title] = url
            sno += 1
        items['99[COLOR yellow]** Search **[/COLOR]'] = self.bu + '/?s='
        return (items, 7, self.icon)

    def get_items(self, url):
        h = html_parser.HTMLParser()
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Tamil Gun')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('article', {'class': re.compile('video')})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)

        plink = SoupStrainer('ul', {'class': 'page-numbers'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)

        for item in mdiv:
            title = h.unescape(item.h3.text)
            title = title.encode('utf8') if self.PY2 else title
            title = title.replace(' HDTV', '').replace(' HD', '')
            url = item.h3.find('a')['href']
            try:
                thumb = item.find('img')['src'].strip()
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            nextli = Paginator.find('a', {'class': 'next'})
            purl = nextli.get('href')
            if 'http' not in purl:
                purl = self.bu[:-12] + purl
            currpg = Paginator.find('span', {'class': 'current'}).text
            pages = Paginator.find_all('a', {'class': 'page-numbers'})
            lastpg = pages[-2].text
            title = 'Next Page.. (Currently in Page %s of %s)' % (currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        if 'cinebix.com' in url:
            self.resolve_media(url, videos)
            return videos

        elif 'tamildbox.' in url or 'tamilhdbox' in url:
            self.resolve_media(url, videos)
            return videos

        html = requests.get(url, headers=self.hdr).text

        try:
            linkcode = urllib_parse.unquote(re.findall(r"unescape\('([^']+)", html)[0])
            sources = re.findall('<iframe.+?src="([^"]+)', linkcode, re.IGNORECASE)
            for source in sources:
                self.resolve_media(source, videos)
        except:
            pass

        mlink = SoupStrainer('div', {'id': 'videoframe'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                url = link.get('src')
                if url.startswith('//'):
                    url = 'https:' + url
                self.resolve_media(url, videos)
        except:
            pass

        try:
            links = videoclass.find_all('a')
            for link in links:
                if 'href' in str(link):
                    url = link.get('href')
                else:
                    url = link.get('onclick').split("'")[1]
                if url.startswith('//'):
                    url = 'https:' + url
                self.resolve_media(url, videos)
        except:
            pass

        mlink = SoupStrainer('div', {'class': 'entry-excerpt'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            pdivs = videoclass.find_all('p')
            for pdiv in pdivs:
                links = pdiv.find_all('a')
                for link in links:
                    if 'href' in str(link):
                        url = link.get('href')
                    else:
                        url = link.get('onclick').split("'")[1]
                    if url.startswith('//'):
                        url = 'https:' + url
                    self.resolve_media(url, videos)
        except:
            pass

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                url = link.get('src')
                if 'latest.htm' not in url:
                    self.resolve_media(url, videos)
        except:
            pass

        try:
            sources = json.loads(re.findall('vdf-data-json">(.*?)<', html)[0])
            url = 'https://www.youtube.com/watch?v={}'.format(sources['videos'][0]['youtubeID'])
            self.resolve_media(url, videos)
        except:
            pass

        return videos

    def get_video(self, url):
        headers = self.hdr
        headers['Referer'] = 'http://{}/'.format(self.get_vidhost(url))
        url += '&stream=1'
        html = requests.get(url, headers=self.hdr, allow_redirects=False)
        strurl = html.headers.get('location')
        return strurl
