import sys, os
from pyboy import PyBoy
rom = sys.argv[1]
script = sys.argv[2:]
for tok in script:
    if tok.startswith('save:'):
        import shutil
        _, room, bx, by, fl, mh = tok.split(':')
        shutil.copy(rom, 'build/test.gbc')
        ram = bytearray(8192)
        ram[0] = ord('P'); ram[1] = ord('B')
        ram[2:7] = bytes([int(room), int(bx), int(by), int(fl), int(mh)])
        ram[7] = (sum(ram[2:7]) + 0x5A) & 0xFF
        open('build/test.gbc.ram', 'wb').write(ram)
        rom = 'build/test.gbc'
script = [t for t in script if not t.startswith('save:')]   # tokens: wait:N  press:BTN:N  shot:name  hold:BTN:N
pb = PyBoy(rom, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
os.makedirs('preview/shots', exist_ok=True)
def tick(n=1):
    for _ in range(n): pb.tick()
for tok in script:
    parts = tok.split(':')
    if parts[0] == 'wait': tick(int(parts[1]))
    elif parts[0] in ('press', 'hold'):
        b = parts[1]; n = int(parts[2]) if len(parts) > 2 else 4
        pb.button_press(b); tick(n); pb.button_release(b); tick(2)
    elif parts[0] == 'shot':
        pb.screen.image.convert('RGB').resize((480, 432)).save('preview/shots/%s.png' % parts[1])
pb.stop(save=False)
