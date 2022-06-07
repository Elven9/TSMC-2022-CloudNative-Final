from flask import Flask
from flask_restful import Api, Resource, reqparse, request
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


import crawler

def test_google_search():
    crawler_loc = crawler.GoogleCrawler()
    query = "TSMC Ingas"
    results = crawler_loc.google_search(query)
    assert len(results) > 0

def test_get_source_try():
    crawler_loc = crawler.GoogleCrawler()
    target_url = 'https://www.reuters.com/technology/exclusive-ukraine-halts-half-worlds-neon-output-chips-clouding-outlook-2022-03-11/'
    response = crawler_loc.get_source(target_url)
    assert response.status_code == 200

def test_html_parser():
    crawler_loc = crawler.GoogleCrawler()
    target_url = 'https://www.reuters.com/technology/exclusive-ukraine-halts-half-worlds-neon-output-chips-clouding-outlook-2022-03-11/'
    response = crawler_loc.get_source(target_url)
    soup = crawler_loc.html_parser(response.text)
    results = soup.findAll("div")
    assert len(results) > 0

def test_scrape_google():
    query = 'https://www.google.com/search?q='+"TSMC Ingas"
    crawler_loc = crawler.GoogleCrawler()
    results = crawler_loc.scrape_google(query)
    assert len(results) > 0


def test_html_getText():
    crawler_loc = crawler.GoogleCrawler()
    target_url = 'https://www.reuters.com/technology/exclusive-ukraine-halts-half-worlds-neon-output-chips-clouding-outlook-2022-03-11/'
    response = crawler_loc.get_source(target_url)
    soup = crawler_loc.html_parser(response.text)
    orignal_text = crawler_loc.html_getText(soup)
    assert len(orignal_text) > 0

def test_word_count():
    crawler_loc = crawler.GoogleCrawler()
    target_url = 'https://www.reuters.com/technology/exclusive-ukraine-halts-half-worlds-neon-output-chips-clouding-outlook-2022-03-11/'
    response = crawler_loc.get_source(target_url)
    soup = crawler_loc.html_parser(response.text)
    orignal_text = crawler_loc.html_getText(soup)
    result_wordcount = crawler_loc.word_count(orignal_text)
    assert len(result_wordcount) > 0

def test_get_wordcount_json():
    crawler_loc = crawler.GoogleCrawler()
    target_url = 'https://www.reuters.com/technology/exclusive-ukraine-halts-half-worlds-neon-output-chips-clouding-outlook-2022-03-11/'
    response = crawler_loc.get_source(target_url)
    soup = crawler_loc.html_parser(response.text)
    orignal_text = crawler_loc.html_getText(soup)
    result_wordcount = crawler_loc.word_count(orignal_text)
    whitelist = ['Ukraine' , 'Russia', 'Japan']
    date = ['2/20']
    end_result = crawler_loc.get_wordcount_json(whitelist , result_wordcount, date)
    assert len(end_result) > 0

def test_jsonarray_toexcel():
    crawler_loc = crawler.GoogleCrawler()
    target_url = 'https://www.reuters.com/technology/exclusive-ukraine-halts-half-worlds-neon-output-chips-clouding-outlook-2022-03-11/'
    response = crawler_loc.get_source(target_url)
    soup = crawler_loc.html_parser(response.text)
    orignal_text = crawler_loc.html_getText(soup)
    result_wordcount = crawler_loc.word_count(orignal_text)
    whitelist = ['Ukraine' , 'Russia']
    date = ['2/20']
    end_result = crawler_loc.get_wordcount_json(whitelist , result_wordcount, date)
    path = '/var/log/history/'
    c_flag = crawler_loc.jsonarray_toexcel(end_result, path)
    assert c_flag != 0

def test_get_original_text():
    crawler_loc = crawler.crawler()
    target_url = 'https://www.reuters.com/technology/exclusive-ukraine-halts-half-worlds-neon-output-chips-clouding-outlook-2022-03-11/'
    original_text = crawler_loc.get_original_text(target_url)
    assert len(original_text) > 0

def test_get_resource_count():
    crawler_loc = crawler.crawler()
    data = {"type":"TSMC", "url":["https://taipeitimes.com/News/biz/archives/2022/01/20/2003771688", "https://udn.com/news/story/7240/6367275"], "date":"2/20"}
    result = crawler_loc.get_resource_count(data)
    assert len(result) > 0
'''
def test_post():
    crawler_loc = crawler.crawler()
    results = crawler_loc.post()
    assert len(results) > 0
'''