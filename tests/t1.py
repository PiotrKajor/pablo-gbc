import sys; sys.path.insert(0,'tests')
from lib import *
g = Game()
g.start_game()
g.skip_dialog(5)
g.tick(60)
print('room', g.room(), g.player())
g.shot('t1_start')
# walk right
g.hold('right'); g.tick(240)
print('room', g.room(), g.player())
g.shot('t1_walk')
