import sys; sys.path.insert(0,'tests')
from lib import *
g = Game(save=(6, 3, 12, 1, 5))   # flags: dash + bossdead? use 1 (dash only)
g.tick(150); g.tap('start', 4); g.tick(100)
# enter arena -> intro dialog
g.hold('right'); g.tick(40); g.hold()
g.tick(30)
print('room', g.room(), 'player', g.player(), 'boss', g.boss())
g.shot('boss_intro')
for _ in range(8):
    g.tick(40); g.tap('a', 3)
g.tick(60)
g.shot('boss_start')
print('boss', g.boss())
# bot: god mode, approach boss and attack
log=[]
for f in range(3000):
    g.poke('p', 12, 99)   # god mode hp
    pl = g.player(); b = g.boss()
    if not b['active']: break
    bx = b['x'] + 16
    dx = bx - (pl['x'] + 8)
    if abs(dx) > 22: g.hold('right' if dx > 0 else 'left')
    else: g.hold('left' if dx < 0 else 'right') if abs(dx)<10 else g.hold()
    if f % 14 == 0: g.tap('b', 2, 0)
    if f % 50 == 0 and pl['ground']: g.tap('a', 2, 0)
    g.tick(1)
    if f % 100 == 0:
        log.append((f, b['hp'], b['state'], int(pl['x']), pl['hp']))
    if f == 400: g.shot('boss_fight')
print(log)
print('boss', g.boss(), 'flags', g.flags(), 'room', g.room())
g.release()
g.tick(200)
g.shot('boss_dead')
for _ in range(10):
    g.tick(40); g.tap('a', 3)
g.shot('after_boss')
