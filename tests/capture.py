import sys, os; sys.path.insert(0,'tests'); sys.path.insert(0,'assets')
from lib import *
from PIL import Image
OUT = os.environ.get('OUT', os.path.expanduser('~/Pulpit/Pablo-screeny'))
def snap(g, name):
    g.pb.screen.image.convert('RGB').resize((640, 576), Image.NEAREST).save('%s/%s.png' % (OUT, name))
def clear(g):
    o = g.sym['_en']
    for i in range(4): g.pb.memory[o + i * 17] = 0

# title
g = Game(); g.tick(220); snap(g, '01_tytul')
g.tap('start', 4); g.tick(100); g.tick(40); snap(g, '02_intro_dialog'); g.pb.stop(save=False)
names = ['Moss_Hollow', 'Green_Path', 'Luma_Cavern', 'The_Gap', 'Archive_Cellar', 'Stone_Door']
for r in range(6):
    g = Game(save=(r, 5 if r != 5 else 3, 12, 1, 5)); g.tick(150); g.tap('start', 4); g.tick(200)
    snap(g, '%02d_pokoj_%s' % (r + 3, names[r])); g.pb.stop(save=False)
# dash
g = Game(save=(1, 3, 12, 1, 5)); g.tick(150); g.tap('start', 4); g.tick(200); clear(g)
g.hold('right'); g.tick(20); g.pb.button_press('select'); g.tick(4); snap(g, '09_dash'); g.pb.button_release('select'); g.pb.stop(save=False)
# attack
g = Game(save=(1, 3, 12, 1, 5)); g.tick(150); g.tap('start', 4); g.tick(200); clear(g)
g.pb.button_press('b'); g.tick(6); snap(g, '10_atak_nail'); g.pb.stop(save=False)
# NPC dialog (wanderer)
g = Game(save=(2, 5, 12, 1, 5)); g.tick(150); g.tap('start', 4); g.tick(200); clear(g)
g.hold('left'); g.tick(15); g.hold(); g.tick(10); g.tap('up', 3); g.tick(150); snap(g, '11_rozmowa_NPC'); g.pb.stop(save=False)
# boss
g = Game(save=(6, 3, 12, 1, 5)); g.tick(150); g.tap('start', 4); g.tick(100)
g.hold('right'); g.tick(40); g.hold(); g.tick(50); snap(g, '12_boss_intro')
for _ in range(8): g.tick(40); g.tap('a', 3)
shots = {300: '13_boss_walka_1', 520: '14_boss_walka_2'}
for f in range(2000):
    g.poke('p', 12, 99)
    pl = g.player(); b = g.boss()
    dx = (b['x'] + 16) - (pl['x'] + 8)
    if abs(dx) > 22: g.hold('right' if dx > 0 else 'left')
    else: g.hold()
    if f % 14 == 0: g.tap('b', 2, 0)
    g.tick(1)
    if f in shots: snap(g, shots[f])
    if not b['active']: break
g.hold(); g.tick(150); snap(g, '15_boss_pokonany_serce')
g.pb.stop(save=False)
g = Game(save=(6, 3, 12, 3, 5)); g.tick(150); g.tap('start', 4); g.tick(100)
g.hold('right'); g.tick(80); g.hold()
for i in range(40):
    g.tick(60); g.tap('a', 3)
    if g.flags() & 64: break
g.tick(120); snap(g, '16_napisy_koncowe'); g.pb.stop(save=False)
print(sorted(os.listdir(OUT)))
