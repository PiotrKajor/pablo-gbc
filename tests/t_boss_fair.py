import sys, random; sys.path.insert(0, 'tests')
from lib import *
IDLE, WIND, CHARGE, JUMP, RECOVER, STUN, DEAD = 1, 2, 3, 4, 5, 6, 7

def projs(g):
    o = g.sym['_pr']; r = []
    for i in range(3):
        on = g.pb.memory[o + i * 5]
        if on:
            x = g.s16('pr', i * 5 + 2); vx = g.peek('pr', i * 5 + 4)
            vx = vx - 256 if vx > 127 else vx
            r.append((x, vx))
    return r

def enter(g, rnd):
    g.hold('right'); g.tick(30 + rnd.randrange(30)); g.hold()
    for _ in range(40):
        g.tick(25)
        if g.peek('boss', 2) != 0: break
        g.tap('a', 3)

def play(seed, verbose=False, max_frames=9000):
    rnd = random.Random(seed)
    g = Game(save=(6, 3, 12, 1, 5)); g.tick(150); g.tap('start', 4); g.tick(100)
    enter(g, rnd)
    deaths = 0; atk_t = 0; jump_t = 0; focus = False; commit = None
    for f in range(max_frames):
        pl = g.player(); b = g.boss()
        if verbose and f < 3: print('dbg', pl, b, g.room(), g.flags())
        if g.flags() & 2: break                     # boss dead flag set
        if pl['dead']:
            g.release(); g.tick(200)
            if g.room() == 6: g.tick(60)
            deaths += 1
            if deaths >= 6: break
            enter(g, rnd); continue
        if not b['active']: g.tick(1); continue
        bst = g.peek('boss', 2); bnext = g.peek('boss', 3); bx = b['x']
        d = (pl['x'] + 8) - (bx + 16)                # >0 : player right of boss
        keys = []
        ad = abs(d)
        want_jump = False
        # 1. shockwaves
        for (px_, vx) in projs(g):
            dx = (pl['x'] + 8) - (px_ + 4)
            if pl['ground'] and abs(dx) < 30 and dx * vx < 0 and pl['y'] > 100: want_jump = True
        # 2. charge dodge
        if bst == CHARGE and pl['ground'] and ad < 40 and d * (-1 if g.peek('boss', 5) else 1) < 0 : pass
        if bst == CHARGE and pl['ground'] and ad < 44: want_jump = True
        # movement
        center = 76
        pcx = pl['x'] + 8
        if bst not in (WIND, JUMP): commit = None
        if bst == WIND and bnext == 4 and commit is None:
            if abs(pcx - center) > 14: commit = 'right' if pcx < center else 'left'
            else: commit = 'right' if d > 0 else 'left'
        if bst in (WIND, JUMP) and commit is not None and (bst == JUMP or bnext == 4):
            keys.append(commit)
        elif bst == WIND:                        # charge incoming: keep some distance
            if ad < 46: keys.append('right' if d > 0 else 'left')
        elif bst == CHARGE:
            if ad < 70: keys.append('right' if d > 0 else 'left')
        elif bst in (IDLE, RECOVER, STUN):
            if pl['hp'] <= 2 and pl['soul'] >= 33 and ad > 70 and bst != STUN:
                focus = True
            if ad > 30: keys.append('left' if d > 0 else 'right')
            elif ad < 22: keys.append('right' if d > 0 else 'left')
            # attack when close
            if ad < 33 and atk_t <= 0 and bst in (RECOVER, STUN, IDLE):
                g.pb.button_press('b'); atk_t = 20
        if focus and pl['soul'] >= 33 and pl['hp'] < 5 and bst in (IDLE, RECOVER) and ad > 60 and not keys:
            keys.append('start')
        else:
            focus = False
        if want_jump and jump_t <= 0:
            g.pb.button_press('a'); jump_t = 26
        if verbose and pl['hp'] != getattr(play, 'lasthp', None):
            print('f', f, 'HP', pl['hp'], 'px', int(pl['x']), 'boss st', bst, 'bx', int(bx), 'd', int(d), 'keys', keys, 'jump', want_jump)
            play.lasthp = pl['hp']
        if verbose and False: print('  f', f, 'hp', pl['hp'], 'px', int(pl['x']), 'py', int(pl['y']), 'bst', bst, 'bx', int(bx), 'by', int(b['y']), 'keys', keys)
        atk_t -= 1; jump_t -= 1
        if jump_t == 14: g.pb.button_release('a')   # hold ~12 frames
        if atk_t == 17: g.pb.button_release('b')
        g.hold(*keys)
        g.tick(1)
        if verbose and f % 120 == 0: print(f, 'hp', pl['hp'], 'boss', b['hp'], 'st', bst, 'd', int(d))
    won = bool(g.flags() & 2)
    res = (won, deaths, g.player()['hp'], f)
    g.pb.stop(save=False)
    return res

if __name__ == '__main__':
    seeds = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5]
    for s in seeds:
        won, deaths, hp, f = play(s)
        print('seed %d: %s  deaths=%d  hp_left=%d  frames=%d (%.0fs)' % (s, 'WON' if won else 'LOST', deaths, hp, f, f / 60))
