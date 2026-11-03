import sys; sys.path.insert(0,'tests')
from lib import *
for r in range(7):
    g = Game(save=(r, 5, 12, 1, 5))
    g.tick(150); g.tap('start', 4); g.tick(150)
    g.shot('room%d' % r)
    print(r, g.room(), g.player()['x'], g.player()['y'])
    g.pb.stop(save=False)
