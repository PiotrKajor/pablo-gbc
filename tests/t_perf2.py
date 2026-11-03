import sys; sys.path.insert(0,'tests')
from lib import *
def measure(g, n, f=None):
    last = g.peek('frame'); d0 = 0; d2 = 0
    for i in range(n):
        if f: f(i)
        g.tick(1)
        cur = g.peek('frame'); d = (cur - last) & 255; last = cur
        if d == 0: d0 += 1
        elif d > 1: d2 += 1
    return d0, d2
g = Game(save=(0, 7, 12, 1, 5))
g.tick(150); g.tap('start', 4); g.tick(150)
print('idle room0: no-advance / multi-advance ticks:', measure(g, 600))
g.hold('right')
print('walking:', measure(g, 100))
g.pb.stop(save=False)
g = Game(save=(1, 3, 12, 1, 5))
g.tick(150); g.tap('start', 4); g.tick(150)
print('room1 idle (2 crawlids):', measure(g, 600))
