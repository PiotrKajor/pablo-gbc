"""Po bossie: Heartlight -> END1 -> napisy 'THE END' -> START -> tytuł z CONTINUE; SRAM ma GF_ENDED. Tylko przyciski."""
import sys, shutil; sys.path.insert(0, 'tests')
from agent import Agent
ROM = 'build/en.gbc'; shutil.copy('build/pablo.gbc', ROM); shutil.copy('build/pablo.noi', 'build/en.noi')
ram = bytearray(8192); ram[0:2] = b'PB'; ram[2:7] = bytes([5, 3, 12, 63, 5]); ram[7] = (sum(ram[2:7]) + 0x5A) & 255
ok = True
def chk(n, c, i=''):
    global ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + n, i, flush=True)
A = Agent(ROM, ram=bytes(ram)); A.log = lambda s: None
A.step((), 150); A.tap('start', 4); A.step((), 100)
A.goto(5, x=80, y=105); A.talk(); chk('strażnik po bossie (GATEKEEPER2)', 'DOOR IS OPEN' in A.dialogs[-1][1], A.dialogs[-1][1])
A.exit_dir = 'r'; A.goto(5, exit_to=6); A.step((), 40)
chk('brak bossa po zwycięstwie', not A.B()['active'])
for _ in range(200):
    if A.in_dialog(): break
    A.step(('right',) if A.P()['x'] < 70 else (), 1)
chk('Heartlight -> END1', A.finish_dialog() == 4 and 'HEARTLIGHT' in A.dialogs[-4][1])
A.step((), 120)
row = lambda y: ''.join(chr(A.vram(c, y) - 85 + 32) if 85 <= A.vram(c, y) < 149 else ' ' for c in range(20)).strip()
chk('napisy', row(8) == 'THE END' and row(16) == 'PRESS START', '%r %r' % (row(8), row(16)))
A.step((), 600); chk('napisy czekają na START', row(8) == 'THE END')
A.tap('start', 4); A.step((), 150)
A.pb.stop(save=True)
d = open(ROM + '.ram', 'rb').read(8)
chk('SRAM: GF_ENDED zapisane', d[5] & 64 and d[7] == (sum(d[2:7]) + 0x5A) & 255, d.hex())
A = Agent(ROM, keep_ram=True); A.log = lambda s: None; A.step((), 150)
A.tap('start', 4); A.step((), 120)
chk('CONTINUE po zakończeniu -> Stone Door, ENDED wyczyszczone (Heartlight można zebrać ponownie)', A.room() == 5 and not (A.flags() & 64), str((A.room(), A.flags())))
A.pb.stop(save=False)
print('ALL PASS' if ok else 'SOME FAILED')
