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

    def read_dict(self, wuxing_file_name):
        num_pattern = re.compile('(\d+)')
        try:
            words_by_attr = [self.wuxing['jin'], self.wuxing['mu'], self.wuxing['shui'], self.wuxing['huo'], self.wuxing['tu']]
            attr_idx = -1
            wuxing_path=os.path.join(self.conf_dir, wuxing_file_name)
            with open(wuxing_path, 'r') as f:
                for l in f:
                    l = l.strip()
                    if 0 == len(l):
                        continue

                    match = re.match(num_pattern, l)
                    if match is not None:
                        strokes = match.group(1)
                        attr_idx = -1
                    else:
                        l = l.split(u'：')[1]
                        words = []
                        attr_idx += 1
                        for c in l:
                            c = c.strip()
                            if 0 == len(c):
                                continue
                            words.append((c, strokes))
                        words_by_attr[attr_idx].extend(words)
        except Exception as e:
            print(str(e))


    def read_word(self, n):
        num_pattern = re.compile('(\d+)')
        sep_pattern = re.compile('\s+')
        words = []
        try:
            with open(os.path.join(self.conf_dir, n), 'r') as f:
                for l in f:
                    match = re.match(num_pattern, l)
                    if match is not None:
                        strokes = match.group(1)
                        l = l.split(u'：')[1]

                    ws = re.split(sep_pattern, l)
                    for w in ws:
                        w = w.strip()
                        if 0 != len(w):
                            words.append((w, strokes))
        except Exception as e:
            print(str(e))

        return words

    def generate_names(self, second_dic, third_dic):
        #only second
        form_datas = {'2_'+s:{u'xs':self.xs, u'mz':w, u'action': u'test'} for w,s in second_dic}
        #only third
        form_datas.update({'3_'+s:{u'xs':self.xs, u'mz':w, u'action': u'test'} for w,s in third_dic})

        names = []
        for second,ss in self.second_dic:
            for third,st in self.third_dic:
                name1 = second+third
                name1 = {u'xs':self.xs, u'mz':name1} 
                key = '11_' + ss + '_' + st
                if key not in form_datas:
                    name1[u'action'] = u'test'
                    form_datas[key]=name1
                else:
                    name1[u'key'] = key
                    names.append(name1)

                name2 = third+second
                name2 = {u'xs':self.xs, u'mz':name2}
                key = '12_' + st + '_' + ss
                if key not in form_datas:
                    name2[u'action'] = u'test'
                    form_datas[key] = name2
                else:
                    name2[u'key'] = key
                    names.append(name2)

        return (names, form_datas)

    def __init__(self):
        self.conf_dir = dirname(realpath(__file__))
        cfg = self.get_config('qiming')
        self.out_file_name = cfg['out_file_name']
        self.xs = cfg[u'xs']
        self.wuxing = {'jin':[], 'mu':[], 'shui':[], 'huo':[], 'tu':[]}
        wuxing_file_name = cfg.get('wuxing_file_name', '')
        if 0 != len(wuxing_file_name):
            self.read_dict(wuxing_file_name)

        second_file_name = cfg['second_dic_file_name']
        if second_file_name in self.wuxing:
            self.second_dic = self.wuxing[second_file_name]
        else:
            self.second_dic = self.read_word(second_file_name)

        third_file_name = cfg['third_dic_file_name']
        if third_file_name in self.wuxing:
            self.third_dic = self.wuxing[third_file_name]
        else:
            self.third_dic = self.read_word(third_file_name)

        #print(self.xs)
        #print(self.second_dic)
        #print(self.third_dic)
        self.names, self.form_datas = self.generate_names(self.second_dic, self.third_dic)
        #print(self.names)
        #print(self.form_datas)
        #with open('/tmp/names.txt', 'wb') as f:
        #    for n in self.names:
        #        l = len(n[u'mz'])
        #        if l > 2:
        #            print(n[u'mz'])
        #        s = str(n) + '\n'
        #        f.write(s.encode('utf-8'))

        #    for k,form in self.form_datas.items():
        #        s = str(form) + '\n'
        #        f.write(s.encode('utf-8'))

        #raise IOError('xxxx')
        self.count = 0

    def parse(self, response):
        for key, formdata in self.form_datas.items():
            yield scrapy.FormRequest(url=response.url
                                     , method='POST'
                                     , meta = {u'key': key}
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
        score = float(result.extract()[0])
        key = response.meta[u'key']

        yield {u'name':''.join(name), u'score':score, u'key': key}

