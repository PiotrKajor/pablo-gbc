import sys; sys.path.insert(0,'tests')
import sim
from lib import *
room,bx,by,flags,ex=0,3,12,0,'r'
exits,seen=sim.reach(room,(bx*8,by*8+8),False)
path=sim.path_to_exit(exits,ex); print(path)
# sim trajectory of first macros
import world
rm=sim.Room(world.ROOMS[room])
st=(bx*8<<4,(by*8+8)<<4,0,0,1,5,0,0,0,0,0)
for _ in range(5): st,_h=sim.step(rm,st,0,False,False,False,False)
g = Game(save=(room,bx,by,flags,5)); g.tick(150); g.tap('start',4); g.tick(110)
print('emu start', g.player()['x'], g.player()['y'], 'sim', st[0]>>4, st[1]>>4)
for (d,hold,dash_at,run) in path[:2]:
    print('macro',d,hold,dash_at,run)
    for f in range(40):
        g.poke('p',12,99)
        b=[]
        if d<0:b.append('left')
        if d>0:b.append('right')
        if hold>0 and f<hold:b.append('a')
        g.hold(*b); g.tick(1)
        s0,_=sim.step(rm,st,d,hold>0 and f<hold,hold>0 and f==0,False,False); st=s0
        if f%4==0: print(f,'emu',g.player()['x'],g.player()['y'],'sim',st[0]/16,st[1]/16)
