import sys; sys.path.insert(0,'tests')
from lib import *
g = Game(save=(1, 3, 12, 0, 5)); g.tick(150); g.tap('start',4); g.tick(110)
en_off=g.sym['_en']
g.hold('right'); jumped=False
for f in range(120):
    for i in range(4): g.pb.memory[en_off+i*17]=0
    g.poke('p',12,99)
    pl=g.player()
    if not jumped and pl['ground'] and pl['x']>=54:
        g.pb.button_press('a'); jumped=True; print('jump at',pl['x'])
    g.tick(1)
    if jumped and g.player()['vy']>0: g.pb.button_release('a')
    if f%5==0 and f>15: print(f, g.player()['x'], g.player()['y'], g.player()['ground'], g.player()['vy'], g.room())
