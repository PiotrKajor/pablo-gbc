"""Physics port of player_update() (game.c) + BFS reachability over the room grids from assets/world.py."""
import sys, itertools
sys.path.insert(0, 'assets')
import world

HX, HY, HW, HH = 3, 2, 10, 14
SOLID, ONEWAY, HAZ = 1, 2, 4

def flag_of(ch):
    return {'#': SOLID, '-': ONEWAY, '^': HAZ}.get(ch, 0)

class Room:
    def __init__(s, r):
        s.r = r
        s.ex = r.exits
    def cell(s, tx, ty):
        if ty < 0: return SOLID if s.ex['u'] == 0xFF else 0
        if ty >= 16: return 0
        if tx < 0: return SOLID if s.ex['l'] == 0xFF else 0
        if tx >= 20: return SOLID if s.ex['r'] == 0xFF else 0
        return flag_of(s.r.g[ty][tx])
    def box(s, bx, by, w, h):
        f = 0
        for ty in range((by - 16) >> 3, ((by - 16 + h - 1) >> 3) + 1):
            for tx in range(bx >> 3, ((bx + w - 1) >> 3) + 1):
                f |= s.cell(tx, ty)
        return f
    def oneway_below(s, x, y, down=False):
        feet = y + 16
        if feet & 7 or down: return False
        ty = (feet - 16) >> 3
        for tx in range((x + HX) >> 3, ((x + HX + HW - 1) >> 3) + 1):
            if s.cell(tx, ty) & ONEWAY: return True
        return False

def step(rm, st, dirn, a_held, a_press, sel_press, has_dash):
    x, y, vx, vy, ground, coyote, jbuf, dash, dash_cd, air_dash, face = st[:11]
    boost = st[11] if len(st) > 11 else 0
    if boost and (vy >= 0): boost = 0
    if dash_cd: dash_cd -= 1
    if coyote: coyote -= 1
    if jbuf: jbuf -= 1
    if dash:
        dash -= 1
        vx = -64 if face else 64
        vy = 0
        if not dash:
            vx = -16 if face else 16
            dash_cd = 14
    else:
        if dirn:
            face = 1 if dirn < 0 else 0
            vx += dirn * 6
            vx = max(-24, min(24, vx))
        else:
            if vx > 6: vx -= 6
            elif vx < -6: vx += 6
            else: vx = 0
        if a_press: jbuf = 5
        if jbuf and (ground or coyote):
            vy = -58; ground = 0; coyote = 0; jbuf = 0
        if not a_held and vy < -20 and not boost: vy = -20
        if sel_press and has_dash and not dash_cd and (ground or air_dash == 0):
            dash = 11
            if not ground: air_dash = 1
    if not dash:
        vy += 4
        if vy > 64: vy = 64
    # X
    nx = x + vx
    steps = (nx >> 4) - (x >> 4)
    sd = -1 if steps < 0 else 1
    moved = True
    while steps:
        px = (x >> 4) + sd; py = y >> 4
        if rm.box(px + HX, py + HY, HW, HH) & SOLID:
            moved = False; vx = 0
            if dash: dash = 1
            break
        x += sd * 16; steps -= sd
    if moved: x = nx
    # Y
    ny = y + vy
    steps = (ny >> 4) - (y >> 4)
    sd = -1 if steps < 0 else 1
    moved = True
    while steps:
        px = x >> 4; py = (y >> 4) + sd
        if sd > 0:
            if (rm.box(px + HX, py + HY, HW, HH) & SOLID) or rm.oneway_below(px, y >> 4):
                moved = False; vy = 0; break
        else:
            if rm.box(px + HX, py + HY, HW, HH) & SOLID:
                moved = False; vy = 0; break
        y += sd * 16; steps -= sd
    if moved: y = ny
    px, py = x >> 4, y >> 4
    ground = 0
    if vy >= 0:
        if (rm.box(px + HX, py + HY + 1, HW, HH) & SOLID) or rm.oneway_below(px, py): ground = 1
    if ground:
        coyote = 5; air_dash = 0
    haz = bool(rm.box(px + HX + 1, py + HY + 4, HW - 2, HH - 4) & HAZ)
    return (x, y, vx, vy, ground, coyote, jbuf, dash, dash_cd, air_dash, face, boost), haz

def exit_of(rm, st):
    x, y, vy = st[0], st[1], st[3]
    cx, cy = (x >> 4) + 8, (y >> 4) + 8
    if cx < 0 and rm.ex['l'] != 0xFF: return 'l'
    if cx >= 160 and rm.ex['r'] != 0xFF: return 'r'
    if cy < 16 and rm.ex['u'] != 0xFF and vy < 0: return 'u'
    if cy >= 150 and rm.ex['d'] != 0xFF: return 'd'
    return None

def reach(room_id, start_px, has_dash, start_state=None, max_nodes=4000):
    """BFS over grounded nodes. returns (set of exits, set of grounded (x,y) nodes)"""
    rm = Room(world.ROOMS[room_id])
    x0, y0 = start_px
    if start_state is None:
        st = (x0 << 4, y0 << 4, 0, 0, 1, 5, 0, 0, 0, 0, 0)
    else:
        st = start_state
    # settle
    for _ in range(5):
        st, _h = step(rm, st, 0, False, False, False, has_dash)
    seen = {}
    exits = {}
    parent = {}
    def key(s): return (s[0] >> 4, s[1] >> 4, s[10])
    frontier = [st]
    seen[key(st)] = st
    macros = []
    for d in (-1, 0, 1):
        for hold in (0, 4, 8, 12, 16, 22, 30):  # 0 = walk
            for dash_at in ((None,) if not has_dash else (None, 4, 8, 14, 20, 26)):
                for run in ((10, 24) if hold == 0 else (None,)):
                    macros.append((d, hold, dash_at, run))
    nodes = 0
    while frontier and nodes < max_nodes:
        s0 = frontier.pop()
        nodes += 1
        for (d, hold, dash_at, run) in macros:
            s = s0
            ok = True
            pressed_a = hold > 0
            for f in range(140):
                a_held = pressed_a and f < hold
                a_press = pressed_a and f == 0
                sel = dash_at is not None and f == dash_at
                if hold == 0 and f >= run and s[4]: break
                s, haz = step(rm, s, d, a_held, a_press, sel, has_dash)
                if haz: ok = False; break
                e = exit_of(rm, s)
                if e:
                    exits.setdefault(e, (s[0] >> 4, s[1] >> 4, key(s0), (d, hold, dash_at, run))); ok = False; break
                if hold > 0 and f > 3 and s[4]: break
            if not ok: continue
            if s[4]:
                k = key(s)
                if k not in seen:
                    seen[k] = s
                    parent[k] = (key(s0), (d, hold, dash_at, run))
                    frontier.append(s)
    reach.parent = parent
    reach.startkey = key(st)
    return exits, seen

def path_to_exit(exits, e):
    px, py, k, macro = exits[e]
    path = [macro]
    while k in reach.parent:
        k, m = reach.parent[k]
        path.append(m)
    return path[::-1]

if __name__ == '__main__':
    import sys
    for dash in (False, True):
        print('--- has_dash =', dash)
        # (room, start px (x,y sprite top), expected)
        tests = [
            (0, (56, 104)), (1, (16, 104)), (2, (16, 104)), (3, (8, 104)), (4, (72, 104)), (5, (16, 104)), (6, (16, 104)),
        ]
        for rid, st in tests:
            ex, seen = reach(rid, st, dash)
            print('room %d (%s): exits reachable: %s   nodes=%d' % (rid, world.ROOMS[rid].name, sorted(ex), len(seen)))
