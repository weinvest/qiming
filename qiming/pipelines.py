# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class QimingPipeline(object):
    def open_spider(self, spider):
        self.name_scores = []

    def close_spider(self, spider):
        key_2_score = {}
        for name_score in self.name_scores:
            score = name_score[u'score']
            key = name_score[u'key']
            key_2_score[key] = score

        for name in spider.names:
            key = name[u'key']
            score = key_2_score[key]
            name[u'score'] = score;
            name[u'name'] = name[u'xs']+name[u'mz']

        self.name_scores.extend(spider.names)
        self.name_scores.sort(key=lambda i : i[u'score'], reverse=True)

        self.file = open(spider.out_file_name, 'wb')
        for name_score in self.name_scores:
            name = name_score[u'name']
            score = name_score[u'score']

            out_result = name+':'+str(score)+'\n'
            out_result = out_result.encode('utf-8')
            self.file.write(out_result)

        self.file.close()

    def process_item(self, item, spider):
        self.name_scores.append(item)
        return item
