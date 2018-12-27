# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy_splash import SplashRequest
from ..items import JdPythonItem
import json
import re
import math
import random
import requests
from jd_Python.settings import User_Agent_List
lua_script1 = '''
function main(splash)
   splash:go(splash.args.url)
   splash:wait(2)
   splash:runjs("document.getElementsByClassName('page')[0].scrollIntoView(true)")
   splash:wait(2)
   return splash:html()
end
'''

class JdPythonSpider(scrapy.Spider):
    name = 'jd_python'
    allowed_domains = ['jd.com']
    #start_urls = ['https://search.jd.com/Search?keyword=scrapy']
    base_url='https://search.jd.com/Search?keyword=scrapy'

    def start_requests(self):
        yield Request(self.base_url,callback=self.parse_page_url)

    def parse_page_url(self,response):
        totle_page=response.xpath("//span[@class='fp-text']/i/text()").extract_first()
        for i in range(int(totle_page)):
            url='https://search.jd.com/Search?keyword=scrapy&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=scrapy&page=%s&s=%s&click=0'%(i*2+1,i*60+1)
            yield SplashRequest(url,endpoint='execute',args={'lua_source':lua_script1},cache_args=lua_script1)
    def parse(self, response):
        item=JdPythonItem()
        papers = response.xpath("//li[@class='gl-item']")
        for paper in papers:
            #name= paper.xpath(".//div[@class='p-name']/a/@title").extract_first()
            #href = paper.xpath(".//div[@class='p-name']/a/@href").extract_first()
            sku_id=paper.xpath("./@data-sku").extract_first()
            if sku_id:
                book_url = 'https://item.jd.com/%s.html'%(int(sku_id))
            #item['name']=name

            yield SplashRequest(book_url,meta={'sku':sku_id},callback=self.parse_book_info)

    def parse_book_info(self,response):
        item=JdPythonItem()
        url=response.url
        book_name=response.xpath("//div[@class='sku-name']/text()").extract_first()
        #book_prie=response.xpath("//div[@class='summary-price']//strong[@id='jd-price']/text()").extract_first()
        book_price=response.xpath("//div[@id='summary-price']/div[@class='dd']/strong/text()").extract_first()
        info={'sku':response.meta['sku'],'name':book_name,'price':book_price,'url':response.url}
        comment_summary_url = 'https://sclub.jd.com/comment/productCommentSummaries.action?referenceIds=%s' % (int(response.meta['sku']))
        yield Request(comment_summary_url, meta=info, callback=self.parse_poorcomment_url)
    def parse_poorcomment_url(self,response):
        item=JdPythonItem()
        #获取产品差评的数量
        comment_summary = json.loads(response.body.decode(response.encoding))

        poorcount = comment_summary['CommentsCount'][0]['PoorCount']
        # 计算差评页数

        if poorcount == 0:
            poorcomment_page_num = 1

        else:
            poorcomment_page_num = math.ceil(poorcount / 10)
        #获取差评
        for i in range(poorcomment_page_num):
            poorcomments=[]
            url='https://sclub.jd.com/comment/productPageComments.action?productId=%s&score=1&sortType=5&page=%s&pageSize=10'%(response.meta['sku'],i)
            headers={'User-Agent':random.choice(User_Agent_List)}
            r=requests.get(url,headers=headers,timeout=2)
            if r.status_code==200:
                poorcomment_summary=r.json()
                comments = poorcomment_summary['comments']
                if comments==[]:
                    poorcomments=['no poor comments']
                else:
                    for comment in comments:
                        content=comment['content']
                        poorcomments.append(content)
            else:
                print('爬取网页失败')
        item['sku']=response.meta['sku']
        item['url']=response.meta['url']
        item['name']=response.meta['name']
        item['price']=response.meta['price']
        item['comments']=poorcomments
        yield item









