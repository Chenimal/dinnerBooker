import sys
import time
import json
import urllib.request
import urllib.parse
from functools import reduce
# common
import fisheye

"""
todo:
1. add log
2. handle error
"""


class autoBooker():

    def __init__(self):
        self.path = sys.path[0]  # time.strftime("%Y-%m-%d", time.localtime())
        self.pref_data = self.path + '/data/preference.txt'
        self.url_menu = 'http://www.chuiyanxiaochu.com/action/get_dish_list?'\
                        'day=%s&type=2&stype=2&_=%d' % (
                            '2015-10-26', time.time())
        self.url_order = {
            'url': 'http://www.chuiyanxiaochu.com/action/team_mem_add_order',
            'data': {'name': '孙晨',
                     'teamId': 1000006,
                     'token': 'e254855def8e14e365be656c458f006b'}}

    # download data
    def fetch(self):
        f = urllib.request.urlopen(url=self.url_menu, timeout=10)
        d = f.read().decode()
        d = json.loads(d)['data']['list']  # ['data']['list']
        return list(map(lambda x: [x['did'], x['name']], d))

    # eliminate non-chinese characters
    def parse(self, str):
        return reduce(lambda x, y: x + y if fisheye.isChinese(y) else x, str, '')

    def getTodaysMenu(self):
        menu_today = self.fetch()
        cleaned = []
        for m in menu_today:
            cleaned.append([m[0], self.parse(m[1])])
        return cleaned

    # existing dish list. The order indicates preference
    def getMyPreference(self):
        f = open(self.pref_data, 'a+')
        f.seek(0, 0)
        res = f.readlines()
        res = map(lambda x: x.strip(), res)
        res = list(filter(lambda x:  x[0] != '#', res))
        f.close()
        return res

    # items in menu but not in pref
    def findNewDishes(self, pref, menu):
        new_dishes = []
        for m in menu:
            if m[1] not in pref:
                new_dishes.append(m[1])
        if new_dishes:
            f = open(self.pref_data, 'a+')
            f.seek(0, 0)
            res = f.readlines()
            # do not add it, if the new dish exists in pref list already
            res = list(filter(lambda x:  x[0] == '#', res))
            for n in new_dishes:
                n = '# ' + n + '\n'
                if n not in res:
                    f.write(n)
            f.close()
        return new_dishes

    # start from the top of my preference list, find the first one that occurs
    # in today's menu
    def decide(self, pref, menu):
        for p in pref:
            for m in menu:
                if p == m[1]:
                    return m
        return None

    # send order request
    def makeOrder(self, did):
        self.url_order['data']['did'] = did
        f = urllib.request.urlopen(
            url=self.url_order['url'], data=urllib.parse.urlencode(self.url_order['data']).encode('utf8'))
        res = f.read().decode("utf8")
        res = json.loads(res)
        return res

    # main function
    def run(self):
        menu = self.getTodaysMenu()
        pref = self.getMyPreference()
        new_dishes = self.findNewDishes(pref, menu)
        msg = 'New dishes: ' + \
            ','.join(new_dishes) if new_dishes else "Nothing new"
        target = self.decide(pref, menu)
        if not target:
            title = 'Nothing has been ordered'
        else:
            res = self.makeOrder(target[0])
            if res['rtn'] == 0:
                title = 'Ordered ' + target[1]
            else:
                title = res['data']['msg']
        fisheye.notify(title=title, message=msg, group='dinner',
                       execute='/usr/local/bin/subl ' + self.pref_data)
        fisheye.logger(self.__class__.__name__, time.strftime(
            '%Y-%m-%d %H:%M:%S\t') + title + '\t' + msg)


a = autoBooker()
a.run()
