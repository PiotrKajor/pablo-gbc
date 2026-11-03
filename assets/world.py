"""Pablo GBC - world: rooms (DSL), entities and dialogue."""

W, H = 20, 16

ENT = dict(START=1, BENCH=2, TABLET=3, CRAWLID=4, FLY=5, NPC=6, CLOAK=7, HEART=8, BOSS=9)

# ------------------------------------------------------------------ texts
TEXTS = {}
TEXT_ORDER = []


def T(name, *pages):
    TEXT_ORDER.append(name)
    TEXTS[name] = pages


T('INTRO',
  "THE GLOW HAS FADED FROM THE VERDANT DEEP.",
  "BENEATH THE MOSS, A LITTLE VESSEL OPENS ITS EYES.",
  "IT HAS NO NAME. THE OLD ONES CALL IT... PABLO.")
T('ELDER1',
  "AH, YOU WAKE, LITTLE ONE. I AM ELDER MOTH.",
  "THE LAMPS ARE DYING. THE WARDEN SWALLOWED THE HEARTLIGHT.",
  "WITHOUT IT, THE DEEP WILL SLEEP FOREVER.",
  "TAKE UP YOUR NAIL, PABLO. GO RIGHT, AND MIND THE DARK.")
T('ELDER2',
  "THE PATH LIES TO THE RIGHT, LITTLE ONE.",
  "SIT AT A BENCH IF YOU TIRE. PRESS UP TO REST.")
T('ELDER3',
  "YOU HAVE WINGS NOW. GOOD.",
  "THE WARDEN WAITS BEYOND THE STONE DOOR. GO WELL, PABLO.")
T('TAB_CTRL',
  "A: JUMP. HOLD A TO LEAP HIGHER. B: STRIKE WITH THE NAIL.",
  "HOLD START TO FOCUS. SOUL MENDS A MASK.",
  "UP: TALK, OR REST AT A BENCH TO SAVE.",
  "DOWN: DROP THROUGH A LEDGE.")
T('WANDERER',
  "MANY CAME BEFORE YOU. ALL FELL AT THE GAP BEYOND.",
  "A JUMP WILL NOT CARRY YOU. ONLY WINGS CAN.",
  "THE ARCHIVIST HOLDS A CLOAK OF WINGS. DROP DOWN THE SHAFT.",
  "IF A LEDGE HOLDS YOU, PRESS DOWN TO FALL THROUGH.")
T('WANDERER2',
  "THE CELLAR IS BELOW THE SHAFT. PRESS DOWN TO DROP THROUGH LEDGES.",
  "DO NOT WORRY. THERE IS A WAY BACK UP.")
T('ARCHIVIST',
  "A VISITOR! I HAVE WAITED SO LONG, LITTLE VESSEL.",
  "THE MOTHWING CLOAK WAS MY LIFE'S WORK. TAKE IT, LITTLE ONE.")
T('ARCHIVIST2',
  "PRESS A IN MIDAIR TO DASH. OR PRESS SELECT. ONCE PER LEAP.",
  "THE GAP WILL NOT STOP YOU NOW. FAREWELL, PABLO.")
T('CLOAK_GOT',
  "PABLO GOT THE MOTHWING CLOAK!",
  "PRESS A IN MIDAIR TO DASH.")
T('TAB_GAP',
  "ONLY WINGS CROSS THE GAP. LEAP, THEN DASH.")
T('GATEKEEPER',
  "HALT. BEYOND THIS DOOR SLEEPS THE WARDEN.",
  "HE WAS A VESSEL LIKE YOU. THE HEARTLIGHT BROKE HIS MIND.",
  "BE KIND TO HIM IF YOU CAN. REST AT THE BENCH FIRST.")
T('GATEKEEPER2',
  "THE DOOR IS OPEN. THE DEEP WATCHES YOU, PABLO.")
T('BOSS_INTRO',
  "...MINE...",
  "THE LIGHT IS MINE! ALL OF IT! MINE!")
T('BOSS_DEAD',
  "THE WARDEN SINKS TO HIS KNEES. THE MOSS FALLS FROM HIM LIKE RAIN.",
  "...SO WARM... THE LIGHT... I REMEMBER NOW...",
  "THANK YOU, LITTLE ONE.")
T('END1',
  "PABLO LIFTS THE HEARTLIGHT. THE LAMPS BLOOM WITH GREEN FIRE.",
  "THE MOSS GROWS SOFT. THE LUMAFLIES RETURN.",
  "THE VERDANT DEEP DREAMS AGAIN.",
  "AND PABLO, WHO HAD NO NAME, AT LAST HAD A HOME.")
T('SAVED', "RESTED AND SAVED.")


def wrap_pages(pages, width=18, lines=4):
    out = []
    for p in pages:
        words = p.split()
        cur = ''
        ls = []
        for w in words:
            if len(cur) + (1 if cur else 0) + len(w) <= width:
                cur = (cur + ' ' + w) if cur else w
            else:
                ls.append(cur)
                cur = w
        if cur:
            ls.append(cur)
        for i in range(0, len(ls), lines):
            chunk = ls[i:i + lines]
            while len(chunk) < lines:
                chunk.append('')
            out.append([c.ljust(width) for c in chunk])
    return out


# ------------------------------------------------------------------ rooms
class Room:
    def __init__(s, name, theme, **exits):
        s.name = name
        s.theme = theme
        s.exits = {k: exits.get(k, 0xFF) for k in 'lrud'}
        s.g = [['.'] * W for _ in range(H)]
        s.npc_args = []
        s.tablet_args = []
        # default shell: ceiling rows 0-1, walls cols 0-1 / 18-19, floor 13-15
        s.fill(0, 0, 19, 1, '#')
        s.fill(0, 0, 1, 15, '#')
        s.fill(18, 0, 19, 15, '#')
        s.fill(0, 13, 19, 15, '#')

    def fill(s, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s.g[y][x] = ch

    def put(s, x, y, ch):
        s.g[y][x] = ch

    def open_left(s, y0=9, y1=12):
        s.fill(0, y0, 1, y1, '.')

    def open_right(s, y0=9, y1=12):
        s.fill(18, y0, 19, y1, '.')

    def open_top(s, x0, x1):
        s.fill(x0, 0, x1, 1, '.')

    def hole_floor(s, x0, x1, y0=13, y1=15):
        s.fill(x0, y0, x1, y1, '.')

    def lamp(s, x, y):
        for yy in range(2, y):
            s.put(x, yy, 'i')
        s.put(x, y, 'l')

    def stal(s, *xs):
        for x in xs:
            s.put(x, 2, 'v')

    def vine(s, x, n=2):
        for k in range(n):
            s.put(x, 2 + k, 'w')


ROOMS = []


def room(*a, **k):
    r = Room(*a, **k)
    ROOMS.append(r)
    return r


# 0 -------- MOSS HOLLOW
r = room("MOSS HOLLOW", 1, r=1)
r.open_right()
r.put(3, 12, 'B')
r.put(7, 12, 'S')
r.put(13, 12, 'N'); r.npc_args.append(0)
r.lamp(5, 4); r.lamp(15, 4)
r.stal(3, 9, 11, 16)
r.vine(7); r.vine(12, 3)
r.put(11, 12, 'm'); r.put(16, 12, 'm'); r.put(9, 12, 'm')
r.fill(6, 9, 9, 9, '-')
r.fill(11, 6, 14, 6, '-')
r.put(2, 12, 'p'); r.put(17, 12, 'p')

# 1 -------- GREEN PATH
r = room("GREEN PATH", 1, l=0, r=2)
r.open_left(); r.open_right()
r.hole_floor(8, 10, 13, 14)
r.fill(8, 15, 10, 15, '^')
r.put(4, 12, 't'); r.tablet_args.append('TAB_CTRL')
r.put(14, 12, 'k')
r.fill(12, 9, 16, 9, '-')
r.put(14, 8, 'k')
r.fill(16, 11, 17, 12, '#')
r.fill(3, 10, 6, 10, '-')
r.stal(4, 8, 14); r.vine(10, 3); r.vine(17)
r.lamp(6, 5)
r.put(2, 12, 'm'); r.put(12, 12, 'm')

# 2 -------- LUMA CAVERN
r = room("LUMA CAVERN", 0, l=1, r=3, d=4)
r.open_left(); r.open_right()
r.hole_floor(8, 10)
r.put(3, 12, 'N'); r.npc_args.append(1)
r.put(15, 12, 'B')
r.put(12, 12, 'k')
r.put(12, 5, 'f')
r.fill(2, 10, 5, 10, '-')
r.fill(13, 10, 16, 10, '-')
r.fill(8, 7, 11, 7, '-')
r.lamp(4, 4); r.lamp(9, 5); r.lamp(14, 4); r.lamp(17, 3)
r.put(6, 12, 'c'); r.put(17, 12, 'c'); r.put(11, 12, 'c')
r.stal(2, 6, 12)

# 3 -------- THE GAP
r = room("THE GAP", 0, l=2, r=5)
r.open_left(); r.open_right()
r.hole_floor(6, 12, 13, 14)
r.fill(6, 15, 12, 15, '^')
r.put(3, 12, 't'); r.tablet_args.append('TAB_GAP')
r.put(9, 6, 'f')
r.stal(4, 7, 10, 13, 16)
r.lamp(15, 5); r.lamp(3, 4)
r.put(17, 12, 'c')

# 4 -------- ARCHIVE CELLAR
r = room("ARCHIVE CELLAR", 2, u=2)
r.open_top(8, 10)
r.put(14, 12, 'N'); r.npc_args.append(2)
r.put(11, 12, 'C')
r.fill(3, 11, 6, 11, '-')
r.fill(9, 9, 12, 9, '-')
r.fill(3, 7, 6, 7, '-')
r.fill(9, 5, 12, 5, '-')
r.fill(8, 3, 11, 3, '-')
r.lamp(15, 6); r.lamp(3, 4)
r.put(8, 12, 'c'); r.put(17, 12, 'c'); r.put(2, 12, 'c')
r.stal(4, 13, 16)
# back wall of old books/bricks
for y in range(4, 13):
    for x in (2, 17):
        pass

# 5 -------- STONE DOOR
r = room("STONE DOOR", 1, l=3, r=6)
r.open_left(); r.open_right()
r.put(3, 12, 'B')
r.put(11, 12, 'N'); r.npc_args.append(3)
r.put(9, 12, 'k')  # tx nieparzysty = startuje w prawo, nie na ławkę (respawn bez darmowego ciosu)
r.put(16, 12, 'k')
r.put(14, 5, 'f')
r.fill(5, 9, 8, 9, '-')
r.fill(13, 9, 16, 9, '-')
r.stal(5, 9, 13)
r.lamp(7, 4); r.lamp(15, 4)
r.fill(18, 2, 19, 8, '#')
r.put(14, 12, 'm')

# 6 -------- WARDEN'S DEN
r = room("WARDEN'S DEN", 3, l=5)
r.open_left()
r.fill(18, 0, 19, 15, '#')
r.put(14, 12, 'W')
r.put(9, 12, 'H')
r.fill(3, 9, 5, 9, '-')
r.fill(8, 7, 10, 7, '-')
r.fill(13, 6, 16, 6, '-')
r.lamp(4, 4); r.lamp(10, 3); r.lamp(16, 4)
r.stal(2, 6, 12, 14)
r.put(2, 12, 'p'); r.put(17, 12, 'p')
