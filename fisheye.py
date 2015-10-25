# -*- coding: utf-8 -*-

# 常用函数
import os

# notify function


def notify(title='', message='', url='', group='', execute=''):
    t = '-title {!r}'.format(title)
    m = '-message {!r}'.format(message)
    u = '-open {!r}'.format(url)
    g = '-group {!r}'.format(group)
    e = '-execute {!r}'.format(execute)
    os.system(
        '/usr/local/bin/terminal-notifier {}'.format(' '.join([m, t, u, g, e])))
