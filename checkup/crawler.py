import bs4
import requests
import urllib
import json
import time
import re
import httplib2
import urlfetch
import html
import json

from bs4 import BeautifulSoup
from bs4 import Tag
from pytrends.request import TrendReq
from collections import Counter
from string import punctuation
from bs4.element import Comment
import reppy.robots
# from reppy.robots import Robots
from gglsbl import SafeBrowsingList
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from requests.exceptions import MissingSchema
from requests.exceptions import ConnectionError

# from google.appengine.api import urlfetch

class Crawler:

    def __init__(self, url, data):
        self.url = url
        self.source_code = requests.get(self.url)
        self.plain_text = self.source_code.text
        self.soup = BeautifulSoup(self.plain_text, "html.parser")
        self.data = data
        self.modal_data = {}
        self.modal_images = {}
        self.modal_keywords = {}
        self.pytrends = TrendReq(hl='en-US')

    def crawl(self, maxPages):
        page = 1
        seo_result = {}
        seo_result_2 = {}
        while page <= maxPages:
            page += 1

            page_speed_url = "https://www.googleapis.com/pagespeedonline/v2" \
                             "/runPagespeed?url=" + self.url + \
                             "&filter_third_party_resources=true&locale=en_US" \
                             "&screenshot=true&strategy=mobile&key" \
                             "=AIzaSyALJmgrWTmS3hvq3lxWzWnvo9FimxY-VAY"

            mobile_ready_url = 'https://www.googleapis.com/pagespeedonline' \
                               '/v3beta1' \
                               '/mobileReady?url=' + self.url + '&key=AIzaSyALJmgrWTmS3hvq3lxWzWnvo9FimxY-VAY'

            page_speed = requests.get(page_speed_url).json()

            page_speed['screenshot']['data'] = page_speed['screenshot']['data'].replace('_', '/')
            page_speed['screenshot']['data'] = page_speed['screenshot']['data'].replace('-', '+')

            seo_result['page_speed'] = page_speed

            mobile_ready = requests.get(mobile_ready_url).json()

            mobile_ready['screenshot']['data'] = mobile_ready['screenshot']['data'].replace('_', '/')
            mobile_ready['screenshot']['data'] = mobile_ready['screenshot']['data'].replace('-', '+')

            seo_result['mobile_ready'] = mobile_ready

            seo_result_2['Nested Tables'] = self.check_nested_tables()

            seo_result_2['Title'] = self.check_title()
            seo_result_2['Description'] = self.check_description()

            seo_result_2['<h1> Headings'] = self.check_headings_one()
            seo_result_2['<h2> Headings'] = self.check_headings_two()

            seo_result_2['Image Alt Tag'] = self.check_images_alt()

            Tag.do_not_call_in_templates = True

            seo_result_2['Broken Links'] = self.check_broken_links()

            seo_result_2['Bad Urls'] = self.check_urls()
            seo_result_2['Inline CSS'] = self.check_styles()
            seo_result_2['Google Analytics'] = self.check_google_analytics()

            seo_result_2['Favicon'] = self.check_favicon()
            seo_result_2['HTTPS'] = self.check_https()

            seo_result_2['Frameset'] = self.check_frames()
            seo_result_2['Canonical Tag'] = self.check_canonical()
            seo_result_2['No Index'] = self.check_noindex()

            seo_result_2['Robots'] = self.check_robots_txt()
            seo_result_2['robots_url'] = self.get_robots()
            seo_result_2['Sitemaps'] = self.check_site_map()
            seo_result_2['Doctype'] = self.check_doctype()

            seo_result_2['No Follow'] = self.check_nofollow()
            seo_result_2['Flash'] = self.check_flash()

            seo_result_2['Keywords'] = self.keyword_results_data(self.keyword_results())
            seo_result_2['Mobile Ready'] = self.check_mobile_ready(mobile_ready)

            scores = {'passed': 0, 'failed': 0, 'warning': 0}
            result = {}

            for key, value in seo_result_2.items():
                try:
                    if value['passed'] is True:
                        scores['passed'] += 1
                        result[key] = {'passed': True}
                    elif value['passed'] is False:
                        scores['failed'] += 1
                        result[key] = {'passed': False}
                    elif value['passed'] is None:
                        scores['warning'] += 1
                        result[key] = {'passed': None}
                except:
                    pass

            api_list = {'Speed': {}, 'Usability': {}}

            for key, value in page_speed['formattedResults']['ruleResults'].items():
                if key == 'MainResourceServerResponseTime':
                    continue
                try:
                    if value['urlBlocks']:
                        scores['failed'] += 1
                        result[value['localizedRuleName']] = {'passed': False}
                    else:
                        scores['passed'] += 1
                        result[value['localizedRuleName']] = {'passed': True}
                except:
                    scores['passed'] += 1
                    result[value['localizedRuleName']] = {'passed': True}
                if 'SPEED' in value['groups']:
                    api_list['Speed'][key] = value
                elif 'USABILITY' in value['groups']:
                    api_list['Usability'][key] = value
                result[value['localizedRuleName']]['priority'] = 'medium'

            seo_result['list'] = seo_result_2

            #self.format_keyword_data(self.keyword_results())

            seo_result['messages'] = json.dumps(self.modal_data)
            seo_result['images'] = json.dumps(self.modal_images)

            #seo_result['keywords'] = json.dumps(self.modal_keywords)

            seo_result['url'] = self.url
            seo_result['scores'] = json.dumps(scores)
            seo_result['result_set'] = json.dumps(result)

            priority_list = {'high': [], 'medium': [], 'low': []}
            for key, value in self.data.items():
                result[key]['priority'] = value['priority']

            for key, value in result.items():
                if value['passed'] is False:
                    priority_list[result[key]['priority']].append('<a href="#" onclick="navigate(\'' + key + '\', 100); return false;" class="orangelink">' + html.escape(key) + '</a>')

            priority_list = {key: value if len(value) > 0 else ['All checks have been passed for this priority'] for key, value in priority_list.items()}

            seo_result['result_set'] = json.dumps(result)
            seo_result['result_s'] = result
            priority_list = {'high': ', '.join(priority_list['high']), 'medium': ', '.join(priority_list['medium']), 'low': ', '.join(priority_list['low'])}
            seo_result['priority_list'] = priority_list

            omen = {'Common': {}, 'Advanced Seo': {}, 'Server': {}}
            for k, v in seo_result['list'].items():
                if type(v).__name__ == 'dict':
                    if v.get('category') == 'common':
                        omen['Common'][k] = v
                    elif v.get('category') == 'server':
                        omen['Server'][k] = v
                    elif v.get('category') == 'advanced_seo':
                        omen['Advanced Seo'][k] = v

            seo_result['omen'] = omen
            seo_result['api_list'] = api_list
            seo_result['nav_list'] = dict(omen, **api_list).keys()

            seo_result['total'] = json.dumps(self.calculate_result(result))

            return seo_result

    def calculate_result(self, data):
        scores = {'passed': 0, 'failed': 0}
        rates = {'high': 3, 'medium': 2, 'low': 1}
        for key, value in data.items():
            if type(value).__name__ == 'dict':
                if value.get('passed') is True:
                    scores['passed'] += rates[value['priority']]
                elif value.get('passed') is False:
                    scores['failed'] += rates[value['priority']]
        return scores


    def check_mobile_ready(self, mobile):
        return {
            'passed': mobile['ruleGroups']['USABILITY']['pass'],
            'content': mobile['ruleGroups']['USABILITY']['pass'],
            'length': 0,
            'name': 'Mobile Ready',
            'msg': self.format_message('Mobile Ready', mobile['ruleGroups']['USABILITY']['pass'], []),
            'category': self.get_from_queryset('Mobile Ready', 'category'),
            'priority': self.get_from_queryset('Mobile Ready', 'priority')
        }

    def check_title(self):
        title = '' if self.soup.find('title') is None else self.soup.find('title').string
        return {
            'passed': True if (len(title) <= 70 and len(title) > 0) else False,
            'content': title,
            'length': len(title),
            'name': 'title',
            'msg': self.format_message('Title', True if (len(title) <= 70 and len(title) > 0) else False, [len(title)]),
            'msg_data': '<p>' + title + '</p>' if len(title) > 0 else '',
            'category': self.get_from_queryset('Title', 'category'),
            'priority': self.get_from_queryset('Title', 'priority')
        }

    def check_description(self):
        description = '' if self.soup.find('meta', {'name': "description"}) is None else self.soup.find('meta', {'name': "description"}).get('content')
        return {
            'passed': True if (len(description) <= 160 and len(description) > 0) else False,
            'content': description,
            'length': len(description),
            'name': 'description',
            'msg': self.format_message('Description', True if (len(description) <= 160 and len(description) > 0) else False, [len(description)]),
            'msg_data': '<p>' + description + '</p>' if len(description) > 0 else '',
            'category': self.get_from_queryset('Description', 'category'),
            'priority': self.get_from_queryset('Description', 'priority')
        }

    def check_headings_one(self):
        headings_one = [] if self.soup.findAll('h1') is None else self.soup.findAll('h1')
        return {
            'passed': True if len(headings_one) == 1 else False,
            'content': headings_one,
            'length': len(headings_one),
            'name': 'headings_one',
            'msg': self.format_message('<h1> Headings', True if len(headings_one) == 1 else False, [len(headings_one)]),
            'category': self.get_from_queryset('<h1> Headings', 'category'),
            'priority': self.get_from_queryset('<h1> Headings', 'priority')
        }

    def check_headings_two(self):
        headings_two = [] if self.soup.findAll('h2') is None else self.soup.findAll('h2')
        return {
            'passed': True if len(headings_two) > 0 else False,
            'content': headings_two,
            'length': len(headings_two),
            'name': 'headings_two',
            'msg': self.format_message('<h2> Headings', True if len(headings_two) > 0 else False, [len(headings_two)]),
            'category': self.get_from_queryset('<h2> Headings', 'category'),
            'priority': self.get_from_queryset('<h2> Headings', 'priority')
        }

    def check_images_alt(self):
        images = self.soup.findAll('img')
        no_alt = []
        if (images is None):
            return {
                'passed': True,
                'content': None,
                'length': 0,
                'name': 'no_alt',
                'msg': self.format_message('Image Alt Tag', True, [len(images), len(no_alt)]),
                'category': self.get_from_queryset('Image Alt Tag', 'category'),
                'priority': self.get_from_queryset('Image Alt Tag', 'priority')
            }
        else:
            for image in images:
                alternative = image.get('alt')
                #image['height'] = '50%'
                #image['width'] = '50%'
                if (alternative is None):
                    #no_alt.append(str(self.check_url(image)))
                    no_alt.append(str(image))
                    #no_alt.append(image)
                elif (alternative == ""):
                    #no_alt.append(str(self.check_url(image)))
                    no_alt.append(str(image))
                    #no_alt.append(image)
                else:
                    pass
            self.modal_data['Image Alt Tag'] = json.dumps([html.escape(el) for el in no_alt])
            self.modal_images = no_alt
            return {
                'passed': False if len(no_alt) > 0 else True,
                'content': no_alt,
                'length': len(no_alt),
                'name': 'no_alt',
                'msg': self.format_message('Image Alt Tag', False if len(no_alt) > 0 else True, [len(images), len(no_alt)]),
                'category': self.get_from_queryset('Image Alt Tag', 'category'),
                'priority': self.get_from_queryset('Image Alt Tag', 'priority'),
                'json': json.dumps(no_alt),
                'html': json.dumps([html.escape(el) for el in no_alt])
            }

    def check_url(self, tag):
        url = tag.get('src')
        if not url.startswith(self.url):
            tag['src'] = self.url + url if (url.startswith('/') and not self.url.endswith('/')) or (not url.startswith('/') and self.url.endswith('/')) else self.url + '/' + url
            tag['src'].replace('///', '/')
        return tag

    def check_links(self):
        links = self.soup.findAll('a', href=True)
        linkz = []
        for link in links:
            if link.get('href') != '' and link.get('href') != '#':
                linkz.append(str(link))
        return linkz

    def check_broken_links(self, update = False):
        links = self.soup.findAll('a')
        broken_links = []
        all_links = []
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        if (links is None):
            return {
                'passed': True,
                'content': None,
                'length': 0,
                'name': 'broken_links',
                'msg': self.format_message('Broken Links', True, [len(broken_links)]),
                'category': self.get_from_queryset('Broken Links', 'category'),
                'priority': self.get_from_queryset('Broken Links', 'priority')
            }
        else:
            for link in links:
                href = link.get('href')
                if (href is None or link.get('onclick') is not None):
                    continue
                elif ('#' == href or 'javascript' in href or '@' in href):
                    continue
                elif ('https://' not in href and 'http://' not in href):
                    href = self.url + href
                try:
                    all_links.append(href)
                    request = requests.head(href, headers=headers)
                    if request.status_code >= 400:
                        request = requests.get(href, headers=headers)
                except:
                    broken_links.append(str(link))
                if request.status_code < 400:
                    pass
                else:
                    broken_links.append(str(link))
            #if update:
                #self.modal_data['Broken Links'] = json.dumps([html.escape(el) for el in broken_links])
            self.modal_data['Broken Links'] = json.dumps([html.escape(el) for el in broken_links])
            return {
                'passed': False if len(broken_links) > 0 else True,
                'content': broken_links,
                'length': len(broken_links),
                'name': 'broken_links',
                'msg': self.format_message('Broken Links', False if len(broken_links) > 0 else True, [len(all_links), len(broken_links)]),
                'html': json.dumps(broken_links),
                'category': self.get_from_queryset('Broken Links', 'category'),
                'priority': self.get_from_queryset('Broken Links', 'priority')
            }

    def url_exists(self, value):
        try:
            request = requests.head(value, allow_redirects=True)
        except ConnectionError:
            return False
        except MissingSchema:
            return False
        except:
            return False
        else:
            return True

    def check_script_async(self):
        scripts = self.soup.findAll('script')
        result = []
        if scripts is None:
            return {
                'passed': True,
                'content': None,
                'length': 0,
                'name': 'script_async',
                'msg': self.format_message('Script Async', True, [len(result)])
            }
        else:
            for script in scripts:
                if script.get('async') and script.get('src') is None or script.get('src') is '':
                    result.append(script)
            return {
                'passed': False if len(result) > 0 else True,
                'content': result,
                'length': len(result),
                'name': 'script_async',
                'msg': self.format_message('Script Async', False if len(result) > 0 else True, [len(result)])
            }

    def check_section(self):
        result = []
        for counter in range(1, 7):
            headings = self.soup.findAll('h' + str(counter))
            if headings is not None:
                for heading in headings:
                    if heading.contents:
                        if '<section' in str(heading.contents):
                            result.append(heading)
        return result

    def check_section_headings(self):
        sections = self.soup.findAll('section')
        result = []
        if sections is None:
            return result
        else:
            for section in sections:
                if section.contents:
                    if ('<h2' not in str(
                            section.contents) and '<h3' not in str(
                        section.contents) and
                            '<h3' not in str(
                                section.contents) and '<h4' not in str(
                                section.contents) and
                            '<h5' not in str(
                                section.contents) and '<h6' not in str(
                                section.contents)):
                        result.append(section)
        return result

    def check_urls(self):
        links = self.soup.findAll('a')
        bad_urls = []
        if (links is None):
            return {
                'passed': True,
                'content': bad_urls,
                'length': len(bad_urls),
                'name': 'bad_urls',
                'msg': self.format_message('Bad Urls', True, [len(bad_urls)]),
                'category': self.get_from_queryset('Bad Urls', 'category'),
                'priority': self.get_from_queryset('Bad Urls', 'priority')
            }
        else:
            for link in links:
                href = link.get('href')
                if (href is None or link.get('onclick') is not None):
                    continue
                elif ('#' == href or 'javascript' in href or '@' in href):
                    continue
                elif ('https://' not in href and 'http://' not in href):
                    href = self.url + href
                if ('?' in href):
                    if '_' in href.split('?')[0] or '=' in href.split('?')[0]:
                        bad_urls.append(str(link))
                else:
                    if '_' in href or '=' in href:
                        bad_urls.append(str(link))
            self.modal_data['Bad Urls'] = json.dumps([html.escape(el) for el in bad_urls])
            return {
                'passed': False if len(bad_urls) > 0 else True,
                'content': bad_urls,
                'length': len(bad_urls),
                'name': 'bad_urls',
                'msg': self.format_message('Bad Urls', False if len(bad_urls) > 0 else True, [len(bad_urls)]),
                'html': json.dumps(bad_urls),
                'category': self.get_from_queryset('Bad Urls', 'category'),
                'priority': self.get_from_queryset('Bad Urls', 'priority')
            }

    def check_styles(self):
        elements = [] if self.soup.findAll() is None else self.soup.findAll()
        result = []
        for element in elements:
            style = element.get('style')
            if (style is not None):
                result.append(str(element))
        self.modal_data['Inline CSS'] = json.dumps([html.escape(el) for el in result])
        return {
            'passed': False if len(result) > 0 else True,
            'content': result,
            'length': len(result),
            'name': 'inline_styles',
            'msg': self.format_message('Inline CSS', False if len(result) > 0 else True, [len(result)]),
            'html': json.dumps([html.escape(el) for el in result]),
            'json': json.dumps(result),
            'category': self.get_from_queryset('Inline CSS', 'category'),
            'priority': self.get_from_queryset('Inline CSS', 'priority')
        }

    def check_google_analytics(self):
        scripts = [] if self.soup.findAll('script') is None else self.soup.findAll('script')
        result = False
        for script in scripts:
            src = script.get('src')
            if (src is not None):
                if ('//www.google-analytics.com/analytics.js' in src):
                    result = True
                    break
            elif ('google-analytics.com' in script.string):
                result = True
                break
        return {
            'passed': result,
            'content': None,
            'length': 0,
            'name': 'google_analytics',
            'msg': self.format_message('Google Analytics', result, [0]),
            'category': self.get_from_queryset('Google Analytics', 'category'),
            'priority': self.get_from_queryset('Google Analytics', 'priority')
        }

    def check_favicon(self):
        links = self.soup.findAll('link')
        result = False
        if (links is not None):
            for link in links:
                rel = link.get('rel')
                if (rel is not None):
                    if ('icon' in rel):
                        result = link
                        break
        return {
            'passed': True if result is not False else False,
            'content': result,
            'length': 0,
            'name': 'favicon',
            'msg': self.format_message('Favicon', True if result is not False else False, [result]),
            'category': self.get_from_queryset('Favicon', 'category'),
            'priority': self.get_from_queryset('Favicon', 'priority')
        }

    def check_robots(self, robots_url):
        try:
            from urllib.request import urlopen
            with urlopen(robots_url) as stream:
                result = stream.read().decode("utf-8")
            if (result):
                return result
            else:
                return False
        except:
            return False

    def check_robots_txt(self):
        robots_url = self.get_robots()
        if robots_url:
            try:
                from urllib.request import urlopen
                with urlopen(robots_url) as stream:
                    # print(stream.read().decode("utf-8"))
                    result = stream.read().decode("utf-8")
            except:
                result = False
        else:
            result = False
        return {
            'passed': True if result else False,
            'content': result,
            'length': 1 if result else 0,
            'name': 'robots',
            'msg': self.format_message('Robots', True if result else False, []),
            'msg_data': '<p><a href="' + robots_url + '">' + robots_url + '</a></p>' if result else '',
            'category': self.get_from_queryset('Robots', 'category'),
            'priority': self.get_from_queryset('Robots', 'priority')
        }


    def get_robots(self):
        return reppy.Robots.robots_url(self.url)

    def check_sitemap(self):
        temp = reppy.Robots.fetch(self.url)
        return list(temp.sitemaps)

    def check_site_map(self):
        sitemaps = []
        str = self.check_robots(self.get_robots())
        if str is not False:
            lines = str.split('\n')
            for line in lines:
                if 'Sitemap:' in line:
                    temp = line.split(':', 1)
                    if temp[1] not in sitemaps:
                        sitemaps.append(temp[1])
            result = '<p>'
            for sitemap in sitemaps:
                result += '<a href="' + sitemap.lower().strip() + '">' + sitemap.lower().strip() + '</a><br>'
            result += '</p>'
        else:
            result = ''
        return {
            'passed': True if len(sitemaps) > 0 else False,
            'content': sitemaps,
            'length': len(sitemaps),
            'name': 'sitemaps',
            'msg': self.format_message('Sitemaps', True if len(sitemaps) > 0 else False, [len(sitemaps)]),
            'msg_data': result if len(sitemaps) > 0 else '',
            'category': self.get_from_queryset('Sitemaps', 'category'),
            'priority': self.get_from_queryset('Sitemaps', 'priority')
        }

    def check_https(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            requests.get(self.url, headers=headers)
            result = True
        except requests.exceptions.SSLError:
            result = False
        except:
            result = False
        return {
            'passed': result,
            'content': None,
            'length': 0,
            'name': 'Https',
            'msg': self.format_message('HTTPS', result, [0]),
            'category': self.get_from_queryset('HTTPS', 'category'),
            'priority': self.get_from_queryset('HTTPS', 'priority')
        }

    def check_deprecated_elements(self, type):
        elements = self.soup.findAll(type)
        result = []
        if (elements is None):
            return False
        else:
            for element in elements:
                result.append(element)
            return result

    def get_most_common_keyword_count(self):
        '''
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content)
        text = (''.join(s.findAll(text=True)) for s in soup)#.findAll(text=True))
        c = Counter((x.rstrip(punctuation).lower() for y in text for x in y.split()))

        print(c.most_common())
        print([x for x in c if c.get(x) > 5])
        '''
        html = urllib.request.urlopen(self.url).read()
        # print(self.text_from_html(html))

        liist = re.findall(r'\b\w+', self.text_from_html(html))
        lst = [x.lower() for x in liist]
        counter = Counter(lst)
        occs = [(word, count) for word, count in counter.items() if count >= 5 and self.is_valid_keyword(word)]
        occs.sort(key=lambda x: x[1])
        #print(occs)
        return occs

    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def text_from_html(self, body):
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(self.tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

    def check_flash(self):
        result = True
        if '/.swf/S' in self.source_code or 'flashplayer' in self.source_code or 'https://get.adobe.com/flashplayer/' in self.source_code:
            result = False
        return {
            'passed': result,
            'content': None,
            'length': 0,
            'name': 'flash',
            'msg': self.format_message('Flash', result, [0]),
            'category': self.get_from_queryset('Flash', 'category'),
            'priority': self.get_from_queryset('Flash', 'priority')
        }

    def check_nested_tables(self):
        tables = self.soup.findAll('table')
        nested_tables = []
        for table in tables:
            if '<table' in table.contents:
                nested_tables.append(table)
        return {
            'passed': False if len(nested_tables) > 0 else True,
            'content': nested_tables,
            'length': len(nested_tables),
            'name': 'nested_tables',
            'msg': self.format_message('Nested Tables', False if len(nested_tables) > 0 else True, [len(nested_tables)]),
            'category': self.get_from_queryset('Nested Tables', 'category'),
            'priority': self.get_from_queryset('Nested Tables', 'priority')
        }

    def check_frames(self):
        framesets = self.soup.findAll('frameset')
        frames = self.soup.findAll('frame')
        iframes = self.soup.findAll('iframe')
        return {
            'passed': False if len(framesets) > 0 or len(frames) > 0 or len(iframes) > 0 else True,
            'content': [framesets, frames],
            'length': [len(framesets), len(frames), len(iframes)],
            'name': 'Frameset',
            'msg': self.format_message('Frameset',  False if len(framesets) > 0 or len(frames) > 0 or len(iframes) > 0 else True, [len(framesets), len(frames), len(iframes)]),
            'category': self.get_from_queryset('Frameset', 'category'),
            'priority': self.get_from_queryset('Frameset', 'priority')
        }

    def check_canonical(self):
        canonical = self.soup.find('link', rel='canonical')
        return {
            'passed': True if canonical else False,
            'content': canonical,
            'length': 1 if canonical else 0,
            'name': 'canonical',
            'msg': self.format_message('Canonical Tag', True if canonical else False, ['uses' if canonical else 'does not use', self.url]),
            'category': self.get_from_queryset('Canonical Tag', 'category'),
            'priority': self.get_from_queryset('Canonical Tag', 'priority')
        }

    def check_safe_browsing(self):
        '''
        sbl = SafeBrowsingList('AIzaSyALJmgrWTmS3hvq3lxWzWnvo9FimxY-VAY')
        threat_list = sbl.lookup_url('http://github.com/')
        if threat_list == None:
            print("no threat")
        else:
            print('threats: ' + str(threat_list))
            print("Type: ", type(threat_list))
        return threat_list
        '''
        safe_browsing_url = 'https://sb-ssl.google.com/safebrowsing/api/lookup?client=demo-app&key=AIzaSyALJmgrWTmS3hvq3lxWzWnvo9FimxY-VAY&appver=1.5.2&pver=3.1&url=http%3A%2F%2Fianfette.org%2F'
        safe_url = requests.get(safe_browsing_url)  # .json()
        return safe_url

    def check_noindex(self):
        meta_tags = self.soup.findAll('meta')
        noindex_tags = []
        if meta_tags and meta_tags is not None:
            for meta_tag in meta_tags:
                name = meta_tag.get('name')
                if name is not None:
                    if 'robots' in name or 'googlebot' in name:
                        if meta_tag.get('content') == 'noindex':
                            noindex_tags.append(meta_tag)
        html_list = []
        for link in noindex_tags:
            html_list.append(str(link))
        self.modal_data['No Index'] = json.dumps([html.escape(el) for el in html_list])
        return {
            'passed': None,
            'content': noindex_tags,
            'length': len(noindex_tags),
            'name': 'no_index',
            'msg': self.format_message('No Index', None, ['uses' if len(noindex_tags) > 0 else 'does not use', len(noindex_tags)]),
            'html': json.dumps(noindex_tags),
            'category': self.get_from_queryset('No Index', 'category'),
            'priority': self.get_from_queryset('No Index', 'priority')
        }

    def check_nofollow(self):
        links = self.soup.findAll('a', rel="nofollow")
        html_list = []
        for link in links:
            html_list.append(str(link))
        self.modal_data['No Follow'] = json.dumps([html.escape(el) for el in html_list])
        return {
            'passed': None,
            'content': links,
            'length': len(links),
            'name': 'no_follow',
            'msg': self.format_message('No Follow', None, ['uses' if len(links) > 0 else 'does not use', len(links)]),
            'html': json.dumps(html_list),
            'category': self.get_from_queryset('No Follow', 'category'),
            'priority': self.get_from_queryset('No Follow', 'priority')
        }

    def check_doctype(self):
        items = [item for item in self.soup.contents if isinstance(item, bs4.Doctype)]
        return {
            'passed': True if items else False,
            'content': str(items[0]) if items else None,
            'length':  1 if items else 0,
            'name': 'doctype',
            'msg': self.format_message('Doctype', True if items else False, []),
            'category': self.get_from_queryset('Doctype', 'category'),
            'priority': self.get_from_queryset('Doctype', 'priority')
        }

    def check_media_queries(self):
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.content, 'lxml')
            css_links = [link["href"] for link in soup.findAll("link") if "stylesheet" in link.get("rel", [])]
        except Exception as e:
            pass

        pattern = re.compile(r'@media.+?\}')
        css_links = []
        media_only = []
        for url in css_links:
            try:
                response = requests.get(url).text
                media_only = pattern.findall(response)
            except Exception as e:
                media_only = []
            except:
                media_only = []
        return [css_links, media_only]

    def check_media(self):
        links = self.soup.findAll('link', rel="stylesheet")
        media_queries = []
        for link in links:
            try:
                css = requests.get(link.get('href')).text
            except:
                continue
            if '@media ' in css or link.get('media') is not None:
                media_queries.append(link)
        return media_queries

    def safe_browsing(self):
        params = urllib.parse.urlencode({
            'client': 'api',
            'apikey': 'AIzaSyALJmgrWTmS3hvq3lxWzWnvo9FimxY-VAY',
            'appver': '1.5.2',
            'pver': '3.1',
            'url': self.url})
        url = "https://sb-ssl.google.com/safebrowsing/api/lookup?%s" % params
        res = urlfetch.fetch(url, method=1)
        if res.status_code >= 400:
            raise Exception("Status: %s" % res.status_code)
        return res.status_code == 204

    def get_category(self, name):
        try:
            cat = self.data[name]['category']
        except:
            cat = None
        return cat

    def get_from_queryset(self, rule, name):
        try:
            data = self.data[rule][name]
        except:
            data = None
        return data

    def get_priority(self, name):
        try:
            priority = self.data[name]['priority']
        except:
            priority = None
        return priority

    def get_message(self, name, status):
        try:
            msg = self.data[name][status]['message']
        except:
            try:
                msg = self.data[name][None]['message']
            except:
                msg = ''
        return msg

    def format_message(self, name, status, args):
        message = self.get_message(name, status)
        if len(message) > 0 and len(args) > 0:
            for arg in args:
                message = message.replace('{{arg}}', arg if type(arg) is str else str(arg), 1)
        return message

    def keyword_results(self):
        results = self.get_most_common_keyword_count()
        keywords = {}
        for result in results:
            keywords[result[0]] = result[1]
        return keywords

    def keyword_results_data(self, keywords):
        if len(keywords) > 0:
            msg = '<ul class="list-group list-group-flush">'
            for key, value in keywords.items():
                msg += '<li onclick="prepare_modal(\'Keywords\', \'' + key + '\')" class="list-group-item list-group-item-light" name="hover-item"><small>' + key + ' - ' + str(value) + ' times </small></li>'
            msg += '</ul>'
        else:
            msg = ''
        #self.modal_data['Keywords'] = json.dumps(self.format_keyword_data(keywords))
        #self.modal_data['Keywords'] = json.dumps([html.escape(el) for el in no_alt])
        return {
            'passed': None,
            'content': None,
            'length': 0,
            'name': 'keywords',
            'msg': self.format_message('Keywords', None, []),
            #'html': json.dumps(self.format_keyword_data(keywords)),
            'msg_data': msg,
            'category': self.get_from_queryset('Keywords', 'category'),
            'priority': self.get_from_queryset('Keywords', 'priority')
        }

    def is_valid_keyword(self, text):
        try:
            float(text)
            return False
        except:
            return True if len(text) > 1 else False

    def format_keyword_data(self, keywords):
        keyword_data = {}
        keywords_data = {}
        for key, value in keywords.items():
            keyword_data[key] = {'data': self.keyword_data(key), 'freq': value}
            keywords_data[key] = self.keyword_data(key)
        self.modal_keywords = keywords_data
        return keyword_data

    def keyword_data(self, keyword, res='COUNTRY'):
        #pytrends = TrendReq(hl='en-US')
        self.pytrends.build_payload([keyword])
        data = {}
        dat = {}

        data['interest_over_time'] = self.pytrends.interest_over_time().to_dict()
        for key, value in data['interest_over_time'].items():
            dat[key] = {}

            for k, v in value.items():
                dat[key][str(k.to_pydatetime())] = v

        data['interest_over_time'] = dat
        data['interest_by_region'] = self.pytrends.interest_by_region(resolution=res).to_dict()
        data['related_topics'] = self.pytrends.related_topics()
        data['related_queries'] = self.pytrends.related_queries()
        data['suggestions'] = self.pytrends.suggestions(keyword)

        data['related_topics'][keyword] = data['related_topics'][keyword] if data['related_topics'][keyword] is None else data['related_topics'][keyword].to_dict()
        data['related_queries'][keyword] = data['related_queries'][keyword]
        data['related_queries'][keyword]['top'] = data['related_queries'][keyword]['top'].to_dict() if data['related_queries'][keyword]['top'] is not None else None
        data['related_queries'][keyword]['rising'] = data['related_queries'][keyword]['rising'].to_dict() if data['related_queries'][keyword]['rising'] is not None else None

        return data
