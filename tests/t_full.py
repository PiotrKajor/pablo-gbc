"""PEŁNE PRZEJŚCIE PABLO od NEW GAME do napisów, tylko przyciski (agent MPC, zero poke)."""
import sys, os, time, shutil, hashlib; sys.path.insert(0, 'tests')
from agent import Agent
ROM = 'build/full.gbc'
shutil.copy('build/pablo.gbc', ROM); shutil.copy('build/pablo.noi', 'build/full.noi')
t0 = time.time()
A = Agent(ROM)
res = {}
def chk(name, cond, info=''):
    res[name] = bool(cond); print(('PASS ' if cond else 'FAIL ') + name, info, flush=True)
def at(): p = A.P(); return 'room=%d x=%.0f y=%.0f hp=%d soul=%d flags=%d f=%d' % (A.room(), p['x'], p['y'], p['hp'], p['soul'], A.flags(), A.frames)

A.step((), 150); A.tap('start', 4); 
for _ in range(200):
    A.step((), 2)
    if A.in_dialog(): break
chk('intro dialog', A.finish_dialog() == 3, at())
# Moss Hollow: Elder
A.goto(0, x=104, y=105); chk('elder', A.talk() == 4 and A.flags() & 4, at())
A.goto(0, x=24, y=105); A.talk(); chk('ławka room0 (zapis)', A.m('have_bench') and A.m('save_room') == 0, at())
A.go_exit('r', 1); chk('-> Green Path', A.room() == 1, at())
A.goto(1, x=32, y=105); chk('tabliczka sterowania', A.talk() == 4, at())
A.go_exit('r', 2); chk('-> Luma Cavern', A.room() == 2, at())
A.goto(2, x=24, y=105); chk('wędrowiec', A.talk() == 4, at())
A.go_exit('d', 4, x=72); chk('-> Archive Cellar (szyb)', A.room() == 4, at())
A.goto(4, x=104, y=105); chk('archiwista', A.talk() == 2, at())
A.goto(4, x=86, tol=4); 
for _ in range(30):
    if A.flags() & 1: break
    A.step((), 4)
chk('Mothwing Cloak', A.flags() & 1, at())
A.goto(4, x=104, y=105); chk('archiwista 2', A.talk() == 2, at())
A.go_exit('u', 2, x=72, max_steps=600); chk('powrót szybem w górę', A.room() == 2, at())
A.go_exit('r', 3); chk('-> The Gap', A.room() == 3, at())
A.goto(3, x=16, y=105); chk('tabliczka GAP', A.talk() == 1, at())
A.go_exit('r', 5, max_steps=600); chk('przejście Gap (dash)', A.room() == 5, at())
A.goto(5, x=24, y=105); A.talk(); chk('ławka Stone Door', A.m('save_room') == 5 and A.m('have_bench'), at())
A.goto(5, x=80, y=105); chk('strażnik', A.talk() == 3, at())
A.goto(5, x=24, y=105); A.talk()
fights = []
while True:
    A.go_exit('r', 6); chk('-> Warden\'s Den', A.room() == 6, at())
    t1 = time.time(); r = A.fight_boss(); r['wall_s'] = round(time.time() - t1); fights.append(r); print('   walka:', r, flush=True)
    if r['won'] or len(fights) >= 8: break
    if A.room() != 5: break
chk('BOSS POKONANY (bez godmode)', fights[-1]['won'], str(fights))
for _ in range(100):
    if A.in_dialog(): A.finish_dialog()
    A.step((), 2)
for _ in range(400):
    if A.in_dialog(): A.finish_dialog(); break
    A.step(('right',) if A.P()['x'] < 70 else ('left',) if A.P()['x'] > 74 else (), 1)
chk('zakończenie (END1)', any('HEARTLIGHT' in t for r_, t in A.dialogs[-4:]) and A.flags() & 64, at())
A.step((), 300)
cr = ''.join(chr(A.vram(c, 8) - 85 + 32) if 85 <= A.vram(c, 8) < 149 else ' ' for c in range(20)).strip()
chk('napisy końcowe', cr == 'THE END', repr(cr))
A.tap('start', 4); A.step((), 200)
A.pb.stop(save=True)
print('frames(real)=%d (%.1f min gry), wall=%.0fs' % (A.frames, A.frames / 3600, time.time() - t0))
print('dialogi:', len(A.dialogs))
open('build/full_dialogs.txt', 'w').write('\n'.join('%d: %s' % d for d in A.dialogs))
print('ALL PASS' if all(res.values()) else 'FAILED: ' + ', '.join(k for k, v in res.items() if not v))
