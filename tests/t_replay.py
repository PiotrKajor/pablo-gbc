import sys; sys.path.insert(0,'tests')
import sim
from lib import *
CASES = [  # room, bx, by, flags, exit, dash
    (0, 3, 12, 0, 'r'), (1, 3, 12, 0, 'r'), (2, 3, 12, 0, 'r'), (2, 3, 12, 0, 'd'),
    (3, 1, 12, 1, 'r'), (4, 9, 12, 0, 'u'), (5, 3, 12, 0, 'r'), (1, 17, 12, 0, 'l'),
]
ok_all = True
for room, bx, by, flags, ex in CASES:
    sx, sy = bx * 8, by * 8 + 8
    exits, seen = sim.reach(room, (sx, sy), bool(flags & 1))
    if ex not in exits:
        print('room', room, 'exit', ex, 'SIM: unreachable'); ok_all = False; continue
    path = sim.path_to_exit(exits, ex)
    g = Game(save=(room, bx, by, flags, 5))
    g.tick(150); g.tap('start', 4); g.tick(110)
    en_off = g.sym['_en']
    def clear_enemies():
        for i in range(4): g.pb.memory[en_off + i * 17] = 0
    done = False
    for (d, hold, dash_at, run) in path:
        for f in range(150):
            clear_enemies(); g.poke('p', 12, 99)
            btns = []
            if d < 0: btns.append('left')
            if d > 0: btns.append('right')
            if hold > 0 and f < hold: btns.append('a')
            g.hold(*btns)
            if dash_at is not None and f == dash_at:
                g.pb.button_press('select')
            g.tick(1)
            if dash_at is not None and f == dash_at: g.pb.button_release('select')
            if g.room() != room: done = True; break
            pl = g.player()
            if hold > 0 and f > 3 and pl['ground']: break
            if hold == 0 and f >= run and pl['ground']: break
        if done: break
    if not done:
        # keep pushing in exit direction (real player would)
        dirkey = {'l': 'left', 'r': 'right', 'u': 'up', 'd': 'down'}[ex]
        g.hold('left' if ex == 'l' else 'right' if ex == 'r' else 'a')
        for f in range(90):
            clear_enemies(); g.poke('p', 12, 99); g.tick(1)
            if g.room() != room: break
    g.release()
    import world
    want = world.ROOMS[room].exits[ex]
    done = (g.room() == want)
    print('room %d exit %s: macros=%d -> %s (now room %d)' % (room, ex, len(path), 'PASS' if done else 'FAIL', g.room()))
    ok_all &= done
    g.pb.stop(save=False)
print('ALL PASS' if ok_all else 'SOME FAILED')
