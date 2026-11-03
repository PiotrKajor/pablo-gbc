import sys; sys.path.insert(0,'tests')
from lib import *
g = Game(save=(4, 9, 12, 1, 5))
g.tick(150); g.tap('start', 4); g.tick(120)
def show(tag):
    pl=g.player(); print('%-10s room=%d x=%.0f y=%.0f ground=%d' % (tag, g.room(), pl['x'], pl['y'], pl['ground']))
show('start')
# climb: platforms A(24-55,y104) B(72-103,y88) C(24-55,y72) D(72-103,y56); exit top x 64-87
def jump_to(dirn, hold_frames, jump_hold=22):
    g.hold(dirn); g.pb.button_press('a')
    for i in range(70):
        g.tick(1)
        if i==jump_hold: g.pb.button_release('a')
        if i==hold_frames: g.hold()
    g.hold(); g.pb.button_release('a'); g.tick(10)
# from x=72 floor go left onto A
jump_to('left', 18); show('afterA')
jump_to('right', 20); show('afterB')
jump_to('left', 20); show('afterC')
jump_to('right', 14); show('afterD')
# jump up through shaft
g.hold('left'); g.pb.button_press('a'); 
for i in range(60):
    g.tick(1)
    if i==8: g.hold()
    if g.room()!=4: break
show('exit')
