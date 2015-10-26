import sys
import time
import json
import re
import urllib.request
import urllib.parse
from functools import reduce
# common
import fisheye

"""
Author: Chen Sun
Date: 10-25-2015
"""


class autoBooker():

    def __init__(self, name=''):
        self.path = sys.path[0]
        self.pref_path = self.path + '/data/preference.txt'
        self.pref_data = self.loadPrefData()
        self.url_base = 'http://www.chuiyanxiaochu.com'
        self.url_menu = self.url_base+'/action/get_dish_list?'\
                        'day=%s&type=2&stype=2&_=%d' % (
                            time.strftime("%Y-%m-%d", time.localtime()), time.time())
        self.url_token = self.url_base+'/team/menu/928fb88d95f71bee5fe6ad1a953831bc'
        self.url_order = {
            'url': self.url_base+'/action/team_mem_add_order',
            'data': {'name': name,
                     'teamId': 1000006,
                     'token': ''}}

    # get token
    def getToken(self):
        f = urllib.request.urlopen(url=self.url_token, timeout=10)
        d = f.read().decode()
        p = re.compile(r'var token = \'(.*?)\'')
        m = p.findall(d)
        self.url_order['data']['token'] = m[0]

    # get pref data
    def loadPrefData(self):
        f = open(self.pref_path, 'a+')
        f.close()
        f = open(self.pref_path, 'r')
        res = f.readlines()
        f.close()
        return res

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
        res = list(map(lambda x: x.strip(), self.pref_data))
        res = list(filter(lambda x:  x and x[0] != '#', res))
        return res

    # items in menu but not in pref
    def findNewDishes(self, pref, menu):
        new_dishes = []
        for m in menu:
            if m[1] not in pref:
                new_dishes.append(m[1])
        if new_dishes:
            # do not add it, if the new dish exists in pref list already
            res = list(filter(lambda x:  x[0] == '#', self.pref_data))
            f = open(self.pref_path, 'a')
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
        try:
            self.getToken()
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
                           execute='/usr/local/bin/subl ' + self.pref_path)
            fisheye.logger(self.__class__.__name__, time.strftime(
                '%Y-%m-%d %H:%M:%S\t') + title + '\t' + msg)
        except Exception as e:
            fisheye.logger(self.__class__.__name__, time.strftime(
                '%Y-%m-%d %H:%M:%S\t') + '[error] ' + str(e))


a = autoBooker('孙晨')
a.run()
