import sys; sys.path.insert(0,'tests')
from lib import *
g = Game()
g.tick(150); g.tap('start', 4); g.tick(100)
# intro dialog: 3 pages
for _ in range(6): g.tick(80); g.tap('a', 3)
print('after intro: room', g.room(), 'flags', g.flags(), 'player', g.player()['x'])
g.hold('right'); g.tick(40); g.hold(); g.tick(10)
g.tap('up', 3); g.tick(10)
for _ in range(8): g.tick(90); g.tap('a', 3)
print('after elder: flags', g.flags(), '(4 = talked)')
g.tick(30); g.shot('ng_after')
# jump and attack sanity
g.hold('right'); g.pb.button_press('a'); g.tick(8); g.pb.button_release('a'); g.tap('b', 3); g.tick(30); g.hold()
print('player', g.player())
