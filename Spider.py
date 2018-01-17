from urllib.parse import urlencode
import pymongo
from pyquery import PyQuery as pq
import requests
from lxml.etree import XMLSyntaxError
from cleanout import clean_strip
from config import PROXY_POOL_URL, MAX_COUNT, MONGO_DB, MONGO_URI, KEYWORD


class Weixin(object):

    def __init__(self):
        self.base_url = "http://weixin.sogou.com/weixin?"
        self.headers = {
        'Cookie': 'CXID=5FBDFD41919AAFFCE1AC0D2584BE8A8A; SUID=5146E2743865860A5A5D8E1D0007D81E; ad=7$RX5Zllll2zgYcNlllllVIN0P1lllllNnJpUyllllGlllll9j7ll5@@@@@@@@@@; ABTEST=0|1516109022|v1; SNUID=F8EC4BDEAAAFCB4D091F96CEAABB5CBC; IPLOC=CN3100; weixinIndexVisited=1; SUV=0048178A74E246515A5DFCE0D516C166; sct=2; JSESSIONID=aaaH-O6VEdZr07J8pHKdw; ppinf=5|1516160413|1517370013|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo0ODolRTQlQjglOTQlRTglQTElOEMlNDAlRTUlODglODclRTclOEYlOEQlRTYlODMlOUN8Y3J0OjEwOjE1MTYxNjA0MTN8cmVmbmljazo0ODolRTQlQjglOTQlRTglQTElOEMlNDAlRTUlODglODclRTclOEYlOEQlRTYlODMlOUN8dXNlcmlkOjQ0Om85dDJsdU9iQTNkLUlneEFjVG1LMzE4MDZ0WXNAd2VpeGluLnNvaHUuY29tfA; pprdig=v0sgkiWI0zn1HNSSnvsNt9VWy-sHLzfWHxJuz68T2N8e1UcpCrYC719cgiITwOYw8J_3fJJ5M-JexpjniXTGbVgG4QupxkrvB0wwi0-qBWH_al9zAqpULXwDMaw9YlRHB4hsCnlsef1IjeOuSGwGr7L_O_VAoZDfeFJ5VTB_wu8; sgid=05-30935577-AVpexZ0uNPG3fzqAsJDTJAE; ppmdig=151616041300000061c1e76a8c829cba8bf8b385e07cd965',
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        self.client = pymongo.MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.proxy = None

    def get_proxy(self):

        try:
            resposne = requests.get(PROXY_POOL_URL)
            if resposne.status_code == 200:
                return resposne.text
            return None
        except ConnectionError:
            return None

    def get_html(self, url, count=1):

        if count >= MAX_COUNT:
            print("尝试了太多次数")
            return None
        try:
            if self.proxy:
                proxies = {
                    'http': 'http://'+ self.proxy
                }
                response = requests.get(url, allow_redirects=False, headers=self.headers, proxies=proxies)
            else:
                response = requests.get(url, allow_redirects=False, headers=self.headers)

            if response.status_code == 200:
                return response.text
            if response.status_code == 302:
                print('302')
                self.proxy = self.get_proxy()
            if self.proxy:
                print('Using Proxy', self.proxy)
                return self.get_html(url)
            else:
                print('Get Proxy Failed')
                return None

        except ConnectionError as e:
            print('Error Occurred', e.args)
            self.proxy = self.get_proxy()
            count += 1
            return self.get_html(url, count)

    def get_index(self, keyword, page):
        data = {
            'query': keyword,
            'type': 2,
            'page': page
        }
        queries = urlencode(data)
        url = self.base_url + queries
        html = self.get_html(url)
        return html

    def parse_index(self, html):
        doc = pq(html)
        items = doc('.news-box .news-list li .txt-box h3 a').items()
        for item in items:
            yield item.attr('href')

    def get_detail(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            return None
        except ConnectionError:
            return None

    def parse_detail(self, html):
        try:
            doc = pq(html)
            title = doc('.rich_media_title').text()
            content = clean_strip(clean_strip(doc('.rich_media_content').text(),'\n',''),'\xa0','').replace('\ufeff','')
            date = doc('#post-date').text()
            nickname = doc('#js_profile_qrcode > div > strong').text()
            wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
            return {
                'title': title,
                'content': content,
                'date': date,
                'nickname': nickname,
                'wechat': wechat
            }
        except XMLSyntaxError:
            return None

    def save_to_mongo(self, data):
        if self.db['articles'].update({'title': data['title']}, {'$set': data}, True):
            print('Saved to Mongo', data['title'])
        else:
            print('Saved to Mongo Failed', data['title'])


    def main(self):
        for page in range(1, 101):
            html = self.get_index(KEYWORD, page)
            if html:
                article_urls = self.parse_index(html)
                for article_url in article_urls:
                    article_html = self.get_detail(article_url)
                    if article_html:
                        article_data = self.parse_detail(article_html)
                        print(article_data)
                        if article_data:
                            self.save_to_mongo(article_data)



if __name__ == '__main__':
    weixin = Weixin()
    weixin.main()
