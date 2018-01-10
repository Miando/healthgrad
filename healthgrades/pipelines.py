# -*- coding: utf-8 -*-
import MySQLdb
import datetime
import time
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class HealthgradesPipeline(object):

    def __init__(self):
        # time.sleep(1)
        self.conn = MySQLdb.connect('159.89.39.167',
                                    'root', '&/rDGW,GHv?fFCM{3HnG', 'health', charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        spider_names = ['amerihealth' ,'horizonblue', '1199']
        if spider.name in spider_names:
            for field in item:
                item[field] = item.get(field, "")
                if item[field]:
                    try:
                        item[field] = item[field].strip()
                        item[field] = item[field].replace('\r', '')
                    except:
                        pass
                else:
                    item[field] = ""
            item['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            item['spider_name'] = spider.name
            try:
                self.cursor.execute("""INSERT INTO data (full_name, url, first_name, last_name, speciality, city,
                                                             state, general_plan, plans, date, spider_name)
                                                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                    (item.get('full_name'), item.get('url'), item.get('first_name'),
                                     item.get('last_name'),
                                     item.get('speciality'), item.get('city'), item.get('state'),
                                     item.get('general_plan'),
                                     item.get('plans'), item.get('date'), item.get('spider_name'),))
                self.conn.commit()
            except MySQLdb.Error as e:
                print("Error %d: %s" % (e.args[0], e.args[1]))
        return item
