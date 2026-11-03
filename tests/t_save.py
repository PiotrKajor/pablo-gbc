import sys; sys.path.insert(0,'tests')
from lib import *
import os
if os.path.exists('build/test.gbc.ram'): os.remove('build/test.gbc.ram')
import shutil; shutil.copy('build/pablo.gbc','build/test.gbc')
if os.path.exists('build/test.gbc.ram'): os.remove('build/test.gbc.ram')
g = Game.__new__(Game)
from pyboy import PyBoy
g.sym = symbols(); g.held=set()
g.pb = PyBoy('build/test.gbc', window='null', sound_emulated=False); g.pb.set_emulation_speed(0)
g.tick(150); g.tap('start',4); g.tick(100)
g.skip_dialog(5); g.tick(30)
g.hold('left'); g.tick(70); g.hold(); g.tick(10)
g.tap('up',3); g.tick(10)
g.pb.stop(save=True)
d = open('build/test.gbc.ram','rb').read()
print('SRAM size', len(d), 'header', d[:8].hex(), 'room,bx,by,flags,maxhp =', list(d[2:7]))
