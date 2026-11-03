import sys; sys.path.insert(0,'tests')
from lib import *
def attempt(flags, use_dash):
    g = Game(save=(3, 1, 12, flags, 5))
    g.tick(150); g.tap('start', 4); g.tick(120)
    g.hold('right'); 
    # run to edge
    for i in range(200):
        g.tick(1)
        pl = g.player()
        if pl['x'] >= 34: break
    # jump
    g.pb.button_press('a')
    t0=g.player()['x']
    dashed=False
    best=0
    for i in range(160):
        g.tick(1)
        pl = g.player()
        if use_dash and not dashed and i == 12:
            g.pb.button_release('a'); g.tick(1); g.pb.button_press('a'); g.tick(2); dashed=True
        if i == 30: g.pb.button_release('a')
        best=max(best,pl['x'])
        if g.room() != 3: break
    pl = g.player()
    res = 'room %d x=%.1f y=%.1f hp=%d maxx=%.1f' % (g.room(), pl['x'], pl['y'], pl['hp'], best)
    g.pb.stop(save=False)
    return res
print('no dash:', attempt(0, False))
print('dash   :', attempt(1, True))
