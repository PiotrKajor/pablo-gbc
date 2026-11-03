import sys, io, time; sys.path.insert(0, 'tests')
from lib import *

ACTIONS = {  # name: (dpad keys, buttons pressed at start, A held frames)
    'stay': ([], [], 0), 'left': (['left'], [], 0), 'right': (['right'], [], 0),
    'jump': ([], ['a'], 14), 'jump_l': (['left'], ['a'], 14), 'jump_r': (['right'], ['a'], 14),
    'atk': ([], ['b'], 0), 'atk_l': (['left'], ['b'], 0), 'atk_r': (['right'], ['b'], 0),
    'dash_l': (['left'], ['select'], 0), 'dash_r': (['right'], ['select'], 0),
    'focus': ([], ['start_hold'], 0),
}
H_ACT = 8       # frames an action is applied
H_ROLL = 36     # rollout horizon

def apply(g, act, n):
    keys, press, ahold = ACTIONS[act]
    held = list(keys)
    if 'start_hold' in press: held.append('start')
    g.hold(*held)
    for b in press:
        if b in ('b', 'select'): g.pb.button_press(b)
        if b == 'a': g.pb.button_press('a')
    for i in range(n):
        if i == 2:
            for b in press:
                if b in ('b', 'select'): g.pb.button_release(b)
        if 'a' in press and i == min(ahold, n - 1):
            g.pb.button_release('a')
        g.tick(1)
    for b in ('a', 'b', 'select'): g.pb.button_release(b)

def score(g, hp0, bhp0):
    pl = g.player(); b = g.boss()
    s = (bhp0 - b['hp']) * 30 - (hp0 - pl['hp']) * 100 if pl['hp'] <= hp0 else (bhp0 - b['hp']) * 30 + 40
    if pl['dead']: s -= 1000
    s += pl['soul'] * 0.02
    return s

def play(max_frames=12000, verbose=False):
    g = Game(save=(6, 3, 12, 1, 5)); g.tick(150); g.tap('start', 4); g.tick(100)
    g.hold('right'); g.tick(40); g.hold()
    for _ in range(40):
        g.tick(25)
        if g.peek('boss', 2) != 0: break
        g.tap('a', 3)
    deaths = 0; t0 = time.time(); frames = 0; min_hp = 5
    while frames < max_frames:
        if g.flags() & 2: break
        pl = g.player(); b = g.boss()
        if pl['dead']:
            deaths += 1
            if deaths >= 5: break
            g.release(); g.tick(220)
            g.hold('right'); g.tick(40); g.hold()
            for _ in range(40):
                g.tick(25)
                if g.peek('boss', 2) != 0: break
                g.tap('a', 3)
            continue
        if not b['active']:
            g.tick(4); frames += 4; continue
        hp0, bhp0 = pl['hp'], b['hp']
        buf = io.BytesIO(); g.pb.save_state(buf)
        best, besta = -1e9, 'stay'
        for name in ACTIONS:
            if name == 'focus' and not (pl['soul'] >= 33 and pl['hp'] < 5 and pl['ground']): continue
            buf.seek(0); g.pb.load_state(buf)
            g.held = set()
            apply(g, name, H_ACT)
            if name == 'focus': apply(g, 'focus', H_ROLL - H_ACT)      # heal needs long hold
            else: apply(g, 'stay', H_ROLL - H_ACT)
            sc = score(g, hp0, bhp0)
            # prefer positions close to boss (to attack) but not overlapping
            pl2 = g.player(); b2 = g.boss()
            ad = abs((pl2['x'] + 8) - (b2['x'] + 16))
            sc -= max(0, ad - 30) * 0.15
            if name == 'focus' and pl2['hp'] > hp0: sc += 60
            if sc > best: best, besta = sc, name
        buf.seek(0); g.pb.load_state(buf); g.held = set()
        apply(g, besta, H_ACT); frames += H_ACT
        min_hp = min(min_hp, g.player()['hp'])
        if verbose and frames % 200 == 0:
            print(frames, 'hp', g.player()['hp'], 'boss', g.boss()['hp'], besta)
    won = bool(g.flags() & 2)
    res = dict(won=won, deaths=deaths, hp_left=g.player()['hp'], seconds=frames / 60.0, boss_hp=g.boss()['hp'], wall=time.time() - t0)
    g.pb.stop(save=False)
    return res

if __name__ == '__main__':
    print(play(verbose=True))
