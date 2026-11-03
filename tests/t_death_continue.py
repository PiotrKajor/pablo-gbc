"""Śmierć u bossa -> respawn na ławce Stone Door; reset bossa; CONTINUE po restarcie konsoli. Tylko przyciski."""
import sys, shutil; sys.path.insert(0, 'tests')
from agent import Agent
ROM = 'build/dc.gbc'; shutil.copy('build/pablo.gbc', ROM); shutil.copy('build/pablo.noi', 'build/dc.noi')
ram = bytearray(8192); ram[0:2] = b'PB'; ram[2:7] = bytes([5, 3, 12, 1 | 4 | 8 | 16 | 32, 5]); ram[7] = (sum(ram[2:7]) + 0x5A) & 255
ok = True
def chk(n, c, i=''):
    global ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + n, i, flush=True)
A = Agent(ROM, ram=bytes(ram)); A.log = lambda s: None
A.step((), 150); A.tap('start', 4); A.step((), 120)
p = A.P(); chk('CONTINUE -> Stone Door na ławce', A.room() == 5 and p['x'] == 24 and p['hp'] == 5, str((A.room(), p)))
A.step(('right',), 200)
for _ in range(60):
    if A.in_dialog(): A.finish_dialog()
    A.step(('right',), 4)
    if A.room() == 6 and A.B()['state'] != 0: break
chk('boss obudzony', A.room() == 6 and A.B()['state'] != 0, str(A.B()))
chk('drzwi zamknięte', A.m('map', 9 * 20) != 0)
n = 0
while not A.P()['dead'] and n < 6000: A.step((), 1); n += 1
chk('śmierć od bossa (stanie w miejscu)', A.P()['dead'], 'po %d klatkach' % n)
A.step((), 200)
p = A.P(); chk('respawn na ławce Stone Door', A.room() == 5 and p['x'] == 24 and p['hp'] == 5 and not p['dead'], str((A.room(), p)))
A.step(('right',), 200)
for _ in range(10):
    A.step(('right',), 4)
    if A.room() == 6: break
b = A.B(); chk('boss zresetowany (20 HP, śpi)', A.room() == 6 and b['hp'] == 20 and b['state'] == 0, str(b))
A.pb.stop(save=True)
d = open(ROM + '.ram', 'rb').read(8)
chk('SRAM nadal z ławką Stone Door', d[:2] == b'PB' and d[2] == 5, d.hex())
# NEW GAME przy istniejącym zapisie (strzałka w górę)
A = Agent(ROM, keep_ram=True); A.log = lambda s: None
A.step((), 150); A.tap('up', 3); A.tap('start', 4)
for _ in range(200):
    A.step((), 2)
    if A.in_dialog(): break
chk('NEW GAME przy zapisie -> intro w Moss Hollow', A.in_dialog() and A.room() == 0 and A.flags() == 0)
A.pb.stop(save=False)
print('ALL PASS' if ok else 'SOME FAILED')
