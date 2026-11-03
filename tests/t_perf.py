import sys; sys.path.insert(0,'tests')
from lib import *
g = Game(save=(6, 3, 12, 1, 5))
g.tick(150); g.tap('start', 4); g.tick(100)
g.hold('right'); g.tick(40); g.hold()
g.tick(30)
for _ in range(8): g.tick(40); g.tap('a', 3)
g.tick(60)
# fight, measure dropped frames: game 'frame' counter vs emulator ticks
drops = 0; total = 0
last = g.peek('frame')
for f in range(1500):
    g.poke('p', 12, 99)
    pl = g.player(); b = g.boss()
    if not b['active']: break
    dx = (b['x'] + 16) - (pl['x'] + 8)
    if abs(dx) > 22: g.hold('right' if dx > 0 else 'left')
    else: g.hold()
    if f % 14 == 0: g.tap('b', 2, 0)
    g.tick(1)
    cur = g.peek('frame')
    d = (cur - last) & 255
    last = cur
    total += 1
    if d != 1: drops += 1
print('ticks', total, 'frames where game frame counter did not advance by 1:', drops)
