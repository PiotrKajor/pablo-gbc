import sys; sys.path.insert(0,'tests')
from lib import *

def run(room, bx, ex_dir, jump_xs, label):
    g = Game(save=(room, bx, 12, 0, 5))
    g.tick(150); g.tap('start', 4); g.tick(110)
    en_off = g.sym['_en']
    g.hold('right' if ex_dir == 'r' else 'left')
    jumped = set()
    for f in range(900):
        for i in range(4): g.pb.memory[en_off + i * 17] = 0
        g.poke('p', 12, 99)
        pl = g.player()
        for jx in jump_xs:
            if jx not in jumped and pl['ground'] and abs(pl['x'] - jx) < 2.5:
                jumped.add(jx); g.pb.button_press('a')
        if 'held' in dir(g) and pl['vy'] > 0 and not pl['ground']: g.pb.button_release('a')
        if pl['vy'] < -50: pass
        g.tick(1)
        if g.pb is None: break
        if g.room() != room:
            print('%s: room %d -> %d at frame %d  PASS' % (label, room, g.room(), f)); g.pb.stop(save=False); return True
        if pl['vy'] > 0: g.pb.button_release('a')
    print('%s: FAIL stuck at x=%.0f' % (label, g.player()['x'])); g.pb.stop(save=False); return False
run(1, 3, 'r', [54], 'R1 pit jump')
run(2, 3, 'r', [54], 'R2 gap jump')
run(2, 17, 'l', [92], 'R2 gap jump back (left)')
run(0, 3, 'r', [], 'R0 walk')
run(5, 3, 'r', [], 'R5 walk')
