"""Spadki klatek: licznik `frame` (frame_sync) vs ticki emulatora, w walce z bossem (god-mode tylko tu, do pomiaru)."""
import sys; sys.path.insert(0, 'tests')
from lib import *
g = Game(save=(6, 3, 12, 1, 5)); g.tick(150); g.tap('start', 4); g.tick(100)
g.hold('right'); g.tick(40); g.hold(); g.tick(30)
for _ in range(8): g.tick(40); g.tap('a', 3)
g.tick(60)
ticks = lag = 0; last = g.peek('frame'); hits = 0; bhp = g.boss()['hp']; lag_on_hit = 0
for f in range(1500):
    g.poke('p', 12, 99)
    pl, b = g.player(), g.boss()
    if not b['active']: break
    dx = (b['x'] + 16) - (pl['x'] + 8)
    g.hold('right' if dx > 0 else 'left') if abs(dx) > 22 else g.hold()
    if f % 14 == 0: g.pb.button_press('b')
    if f % 14 == 2: g.pb.button_release('b')
    g.tick(1); ticks += 1
    cur = g.peek('frame'); d = (cur - last) & 255; last = cur
    nb = g.boss()['hp']
    if nb < bhp: hits += 1
    if d == 0:
        lag += 1
        if nb < bhp or g.peek('hitstop'): lag_on_hit += 1
    bhp = nb
print('ticki %d, klatki bez frame_sync %d (%.1f%%), z tego w hitstopie/przy trafieniu %d, trafień %d' % (ticks, lag, 100 * lag / ticks, lag_on_hit, hits))
