import os
import sys

# notify function
def notify(title='', message='', url='', group='', execute=''):
    t = '-title {!r}'.format(title)
    m = '-message {!r}'.format(message)
    u = '-open {!r}'.format(url)
    g = '-group {!r}'.format(group)
    e = '-execute {!r}'.format(execute)
    os.system(
        '/usr/local/bin/terminal-notifier {}'.format(' '.join([m, t, u, g, e])))

# if unicode char is chinese
def isChinese(uchar):
    return True if uchar >= u'\u4e00' and uchar <= u'\u9fa5' else False

# log
def logger(name=__name__, msg=''):
    path = sys.path[0] + '/log/' + name + '.log'
    f = open(path, 'a')
    f.write(msg + '\n')
    f.close()
