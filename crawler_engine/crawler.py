from flask import Flask
from flask_restful import Api, Resource, reqparse, request
import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
#import sqlite3
from influxdb import InfluxDBClient
nltk.download('stopwords')
nltk.download('punkt')
import json
app = Flask(__name__)
api = Api(app)

DB_path = "http://tsmc-project-influxdb.default:8086/project"

parser = reqparse.RequestParser()
#parser.add_argument('type')
#parser.add_argument('url')
parser.add_argument("payload", type=json)
#args = parser.parse_args()


'''
input data type 
"payload" : [{"type":"TSMC", "url":["abc.com","ddd.com"]}]

api usage
use post and url:localhost:8088/crawler
e.g curl -d '{"payload":[{"type":"TSMC", "url":["https://taipeitimes.com/News/biz/archives/2022/01/20/2003771688", "https://udn.com/news/story/7240/6367275"]},{"type":"ASML", "url":["https://taipeitimes.com/News/biz/archives/2022/01/20/2003771688", "https://udn.com/news/story/7240/6367275"]}]}' -H "Content-Type: application/json" -X POST localhost:8088/crawler
'''
class crawler(Resource):
    def __init__(self):
        self.crawler = GoogleCrawler()
    '''
    def get(self, company):
        results = self.get_resource_count(company)
        #print(results[0]["link"])
        return results
    '''
    def post(self):
        json_data = request.get_json(force=True)
        path = '/var/log/history/'
        #print(json_data['payload'])
        results = []
        for data in json_data['payload']:
            print(data)
            #print(type(x))
            results += self.get_resource_count(data)
        print(type(results))
        #self.crawler.jsonarray_toexcel(results, path) 
        self.store_data(results)
        return results

    def get_resource_count(self, data):
        #query = "台積電"
        query = data['type']
        urls = data['url']
        date = data['date']
        #query = company
        print(query)
        #result_wordcount = 0
        all_text = ""
        for url in urls:
            #source_data = self.crawler.google_search(query , 'qdr:w' , page);
            original_text = self.get_original_text(url)
            all_text += original_text
        word_count = self.crawler.word_count(all_text)
        #whitelist = ['ASML', 'Intel', 'TSMC']
        whitelist = [query]
        result = self.crawler.get_wordcount_json(whitelist, word_count, date) 
              
        return result


    def get_original_text(self, link):
        Target_URL = link
        response = self.crawler.get_source(Target_URL)
        soup = self.crawler.html_parser(response.text)
        original_text = self.crawler.html_getText(soup)
        return original_text 
    def store_data(self, results):
        conn = InfluxDBClient('tsmc-project-influxdb.default', '8086', '', '', 'project')
        #conn = InfluxDBClient('localhost', '8086', 'admin', 'admin')

        #conn.execute('''
        #    CREATE TABLE IF NOT EXISTS TrendTable (
        #        Date TEXT NOT NULL,
        #        Company TEXT NOT NULL,
        #        Count INT NOT NULL,
        #        PRIMARY KEY (Date, Company)
        #    );
        #'''
        #)
        #conn.create_database('project')
        for data in results:
            info = [{
                "measurement": "Trend",
                "tags": {
                    "Date" : data['Date'],
                    "Company" : data['Company']
                },
                "fields": {
                    "Count" : data['Count']
                }                
            }]
            conn.write_points(info)


class GoogleCrawler():
    def __init__(self):
        self.url = 'https://www.google.com/search?q='    
    #  URL 萃取 From Google Search上 , using 第三方套件
    #  https://python-googlesearch.readthedocs.io/en/latest/
    def google_url_search_byOpenSource(query,tbs='qdr:m',num=10):
        array_url = [url for url in search('tsmc', tbs='qdr:m' , num=10)]
        return array_url
    # 網路擷取器
    def get_source(self,url):
        try:
            session = HTMLSession()
            response = session.get(url)
            return response
        except requests.exceptions.RequestException as e:
            print(e)
    # URL 萃取 From Google Search上
    def scrape_google(self,query):

        response = self.get_source(self.url + query)
        links = list(response.html.absolute_links)
        google_domains = ('https://www.google.', 
                          'https://google.', 
                          'https://webcache.googleusercontent.', 
                          'http://webcache.googleusercontent.', 
                          'https://policies.google.',
                          'https://support.google.',
                          'https://maps.google.')

        for url in links[:]:
            if url.startswith(google_domains):
                links.remove(url)
        return links
# URL萃取器，有link之外，也有標題
#     qdr:h (past hour)
#     qdr:d (past day)
#     qdr:w (past week)
#     qdr:m (past month)
#     qdr:y (past year)
    def google_search(self,query,timeline='',page='0'):
        url = self.url + query + '&tbs={timeline}&start={page}'.format(timeline=timeline,page=page)
        print('[Check][URL] URL : {url}'.format(url=url))
        response = self.get_source(self.url + query)
        return self.parse_googleResults(response)
    # Google Search Result Parsing
    def parse_googleResults(self,response):

        css_identifier_result = "tF2Cxc"
        css_identifier_title = "h3"
        css_identifier_link = "yuRUbf"
        css_identifier_text = "VwiC3b"
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.findAll("div", {"class": css_identifier_result})
        output = []
        for result in results:
            item = {
                'title': result.find(css_identifier_title).get_text(),
                'link': result.find("div", {"class": css_identifier_link}).find(href=True)['href'],
                'text': result.find("div", {"class": css_identifier_text}).get_text()
            }
            output.append(item)
        return output
    # 網頁解析器
    def html_parser(self,htmlText):
        soup = BeautifulSoup(htmlText, 'html.parser')
        return soup
    # 解析後，取<p>文字
    def html_getText(self,soup):
        orignal_text = ''
        for el in soup.find_all('p'):
            orignal_text += ''.join(el.find_all(text=True))
        return orignal_text
    
    def word_count(self, text):
        counts = dict()
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)
        #words = text.replace(',','').split()
        for word in words:
            if word not in stop_words:
                if word in counts:
                    counts[word] += 1
                else:
                    counts[word] = 1
        return counts
    def get_wordcount_json(self,whitelist , dict_data, date):
        data_array = []
        for i in whitelist:
            if i in dict_data:
                json_data = {
                    'Date' : date,
                    'Company' : i , 
                    'Count' : dict_data[i]
                }
                data_array.append(json_data)
            else:
                json_data = {
                    'Date' : date,
                    'Company' : i , 
                    'Count' : 0
                }
                data_array.append(json_data)
        return data_array
    def jsonarray_toexcel(self,data_array, path):
        df = pd.DataFrame(data=data_array)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        filename = path + current_time + ".xlsx"
        print("save result as "+filename)
        try:
            print("Save to pvc")
            df.to_excel(filename , index=False)
        except:
            print("Save Error, Change")
            print("Save to Root")
            df.to_excel('result.xlsx' , index=False)
        return

#api.add_resource(crawler, '/crawler/<string:company>')
api.add_resource(crawler, '/crawler')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8088, debug=True)

