import sys; sys.path.insert(0,'tests')
from lib import *
# --- death & respawn: room 1, bench (3,12); put hp=1 and run into crawlid
g = Game(save=(1, 3, 12, 1, 5))
g.tick(150); g.tap('start', 4); g.tick(100)
g.poke('p', 12, 1)
g.hold('right')
died = False
for i in range(400):
    g.tick(1)
    pl = g.player()
    if pl['dead']: died = True; print('died at frame', i, 'x', pl['x']); break
g.hold()
g.shot('death')
g.tick(200)
pl = g.player(); print('respawned:', died, 'room', g.room(), 'x', pl['x'], 'hp', pl['hp'], 'dead', pl['dead'])
g.shot('respawn')
g.pb.stop(save=False)
# --- focus heal
g = Game(save=(0, 7, 12, 1, 5))
g.tick(150); g.tap('start', 4); g.tick(100)
g.poke('p', 12, 2); g.poke('p', 14, 99)
g.tick(5)
g.hold('start'); g.tick(100); g.hold()
pl = g.player(); print('focus: hp', pl['hp'], 'soul', pl['soul'])
# --- bench rest: bench at tile (3,12) room 0 -> go left and press up
g.hold('left'); g.tick(70); g.hold(); g.tick(10)
g.tap('up', 3); g.tick(10)
g.shot('bench')
print('bench rest x', g.player()['x'])
g.pb.stop(save=False)
