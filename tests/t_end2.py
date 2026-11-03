import sys; sys.path.insert(0,'tests')
from lib import *
g = Game(save=(6, 3, 12, 3, 5))
g.tick(150); g.tap('start', 4); g.tick(100)
g.hold('right')
for i in range(40):
    g.tick(10); pl=g.player()
    if i%3==0: print(i, pl['x'], pl['dead'], g.flags())
g.hold()
for i in range(40):
    g.tick(60); g.tap('a',3)
    pl=g.player(); print('t',i, pl['dead'], g.flags(), g.pb.screen.image.getpixel((10,10)))
    if g.flags() & 64: break
g.tick(100)
g.shot('credits2')
