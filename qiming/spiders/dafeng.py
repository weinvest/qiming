# -*- coding: utf-8 -*-
import os
import re
import json
import scrapy
from os.path import realpath,dirname

class DafengSpider(scrapy.Spider):
    name = 'dafeng'
    allowed_domains = ['xingming.com']
    start_urls = ['http://www.xingming.com/dafen/']

    def get_config(self, name):
        cfg_file_name = name+'.json'
        path = os.path.join(self.conf_dir, cfg_file_name)
        with open(path, 'r', encoding='utf-8') as f:
            return json.loads(f.read())

    def read_word(self, n):
        sep_pattern = re.compile('\s+')
        words = []
        try:
            with open(os.path.join(self.conf_dir, n), 'r') as f:
                for l in f:
                    ws = re.split(sep_pattern, l)
                    for w in ws:
                        w = w.strip()
                        if 0 != len(w):
                            words.append(w)
        except Exception as e:
            print(str(e))

        return words

    def generate_names(self, second_dic, third_dic):
        #only second
        names = [{u'xs':self.xs, u'mz':i, u'action': u'test'} for i in second_dic]
        #only third
        names.extend([{u'xs':self.xs, u'mz':i, u'action': u'test'} for i in third_dic])

        for second in self.second_dic:
            for third in self.third_dic:
                name1 = second+third
                name1 = {u'xs':self.xs, u'mz':name1, u'action': u'test'} 
                names.append(name1)

                name2 = third+second
                name2 = {u'xs':self.xs, u'mz':name2, u'action': u'test'} 
                names.append(name2)

        return names

    def __init__(self):
        self.conf_dir = dirname(realpath(__file__))
        cfg = self.get_config('qiming')
        self.out_file_name = cfg['out_file_name']
        self.xs = cfg[u'xs']
        self.second_dic = self.read_word(cfg['second_dic_file_name'])
        self.third_dic = self.read_word(cfg['third_dic_file_name'])
        #print(self.xs)
        #print(self.second_dic)
        #print(self.third_dic)
        self.names = self.generate_names(self.second_dic, self.third_dic)
        #print(self.names)
        with open('/tmp/names.txt', 'wb') as f:
            for n in self.names:
                l = len(n[u'mz'])
                if l > 2:
                    print(n[u'mz'])
                s = str(n) + '\n'
                f.write(s.encode('utf-8'))
        raise IOError('xxxx')
        self.count = 0

    def parse(self, response):
        for r in self.names:
            formdata = r
            yield scrapy.FormRequest(url=response.url
                                     , method='POST'
                                     , formdata=formdata
                                     , callback=self.parse_result
                                     , dont_filter = True)
    
    def parse_result(self, response):
        #from scrapy.shell import inspect_response
        #inspect_response(response, self)

        result = response.xpath('//font[@size=5]/text()')
        if 0 == result:
            return
        name = response.xpath('//form/input/@value').extract()[:2]
        score = int(result.extract()[0])

        yield {u'name':''.join(name), u'score':score}

