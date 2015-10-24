# -*- coding: utf-8 -*-
import sys
import urllib2
import time
import json
# resolve chinese character encoding problem
reload(sys)
sys.setdefaultencoding('utf8')
# common
from fisheye import notify


class autoBooker():

    def __init__(self):
        self.path = sys.path[0]
        self.url_menu = 'http://www.chuiyanxiaochu.com/action/get_dish_list?'\
                        'day=%s&type=2&stype=2&_=%d' % (time.strftime("%Y-%m-%d", time.localtime()),
                                                        time.time())

    # download data
    def fetch(self):
        f = urllib2.urlopen(url=self.url_menu, timeout=10)
        d = f.read()
        d = json.loads(d)['data']['list']
        return map(lambda x: x['name'], d)

    # eliminate non-chinese characters
    def parse(self, str):
        return reduce(lambda x, y: x + y if self.isChinese(y) else x, str, '')

    # if unicode char is chinese
    def isChinese(self, uchar):
        return True if uchar >= u'\u4e00' and uchar <= u'\u9fa5' else False

    def getTodaysMenu(self):
        menu_today = self.fetch()
        menu_today = map(self.parse, menu_today)
        return menu_today

    # existing dish list. The order indicates preference
    def getMyPreference(self):
        f = open(self.path + '/data/preference.txt', 'w+')
        res = f.readlines()
        f.close()
        return res

    # items in menu but not in pref
    def findNewDishes(self, pref, menu):
        new_dishes = []
        for m in menu:
            if m not in pref:
                new_dishes.append(m)
        return new_dishes

    # start from the top of my preference list, find the first one that occurs
    # in today's menu
    def decide(self, pref, menu):
        for p in pref:
            if p in menu:
                return p
        return None

    # send order request
    def makeOrder(self, dishid):
        pass

    # main function
    def run(self):
        menu = self.getTodaysMenu()
        print menu
        pref = self.getMyPreference()
        print pref
        new_dishes = self.findNewDishes(pref, menu)
        msg = 'New dishes: ' + new_dishes if new_dishes else "Nothing new"
        target = self.decide(pref, menu)
        if not target:
            title = 'Nothing has been ordered'
        else:
            res = self.makeOrder(target)
            title = 'You ordered ' + target if res else 'Order failed'
        notify(title=title, message=msg)


a = autoBooker()
a.run()
