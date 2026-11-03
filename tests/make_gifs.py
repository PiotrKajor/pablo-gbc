import sys, os; sys.path.insert(0,'tests')
from lib import *
from PIL import Image
OUT = 'docs/gifs'; os.makedirs(OUT, exist_ok=True)
def frame(g): return g.pb.screen.image.convert('RGB').resize((320, 288), Image.NEAREST)
def run(g, fr, n, every=3):
    for i in range(n):
        g.tick(1)
        if i % every == 0: fr.append(frame(g))
def save(fr, name, ms=50):
    fr[0].save('%s/%s.gif' % (OUT, name), save_all=True, append_images=fr[1:], duration=ms, loop=0, optimize=True)
    print(name, len(fr))
def clear(g):
    o = g.sym['_en']
    for i in range(4): g.pb.memory[o + i * 17] = 0
# 1 title + intro
g = Game(); fr = []; run(g, fr, 200); g.tap('start', 4); run(g, fr, 120); save(fr, '01_start', 70); g.pb.stop(save=False)
# 2 ruch, skok, atak (Green Path)
g = Game(save=(1, 3, 12, 1, 5)); g.tick(150); g.tap('start', 4); g.tick(200); clear(g); fr = []
g.hold('right'); run(g, fr, 30)
g.pb.button_press('a'); run(g, fr, 25); g.pb.button_release('a'); run(g, fr, 25)
g.pb.button_press('b'); g.tick(2); g.pb.button_release('b'); run(g, fr, 30)
g.pb.button_press('b'); g.tick(2); g.pb.button_release('b'); run(g, fr, 30)
save(fr, '02_ruch_i_atak'); g.pb.stop(save=False)
# 3 dash A w powietrzu przez przepasc (The Gap)
g = Game(save=(3, 1, 12, 1, 5)); g.tick(150); g.tap('start', 4); g.tick(120); fr = []
g.hold('right')
for i in range(200):
    g.tick(1)
    if g.player()['x'] >= 34: break
g.pb.button_press('a'); d = False
for i in range(110):
    g.tick(1)
    if i % 2 == 0: fr.append(frame(g))
    if i == 12 and not d: g.pb.button_release('a'); g.tick(1); g.pb.button_press('a'); g.tick(2); d = True
    if i == 30: g.pb.button_release('a')
save(fr, '03_dash_przez_przepasc', 40); g.pb.stop(save=False)
