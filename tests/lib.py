import re, os, shutil, struct
from pyboy import PyBoy

def symbols(noi='build/pablo.noi'):
    d = {}
    for l in open(noi):
        m = re.match(r'DEF (\w+) 0x([0-9A-Fa-f]+)', l)
        if m: d[m.group(1)] = int(m.group(2), 16)
    return d

class Game:
    def __init__(self, rom='build/pablo.gbc', save=None, speed=0):
        self.sym = symbols()
        if save:
            room, bx, by, fl, mh = save
            shutil.copy(rom, 'build/test.gbc')
            ram = bytearray(8192)
            ram[0] = ord('P'); ram[1] = ord('B')
            ram[2:7] = bytes([room, bx, by, fl, mh])
            ram[7] = (sum(ram[2:7]) + 0x5A) & 0xFF
            open('build/test.gbc.ram', 'wb').write(ram)
            rom = 'build/test.gbc'
        elif os.path.exists('build/test.gbc.ram'):
            os.remove('build/test.gbc.ram')
        self.pb = PyBoy(rom, window='null', sound_emulated=False)
        self.pb.set_emulation_speed(0)
        self.held = set()
        os.makedirs('preview/shots', exist_ok=True)
    def tick(self, n=1, god=False):
        for _ in range(n):
            if god: self.poke('p', 12, 99)
            self.pb.tick()
    def peek(self, name, off=0, n=1):
        a = self.sym['_' + name] + off
        return self.pb.memory[a] if n == 1 else list(self.pb.memory[a:a + n])
    def poke(self, name, off, val):
        self.pb.memory[self.sym['_' + name] + off] = val
    def s16(self, name, off):
        v = self.peek(name, off) | (self.peek(name, off + 1) << 8)
        return v - 65536 if v >= 32768 else v
    def player(self):
        return dict(x=self.s16('p', 0) / 16, y=self.s16('p', 2) / 16, vx=self.s16('p', 4) / 16, vy=self.s16('p', 6) / 16,
                    ground=self.peek('p', 9), hp=self.peek('p', 12), soul=self.peek('p', 14), hurt=self.peek('p', 15),
                    atk=self.peek('p', 17), dash=self.peek('p', 20), dead=self.peek('p', 24), face=self.peek('p', 8))
    def room(self): return self.peek('cur_room')
    def flags(self): return self.peek('gflags')
    def boss(self):
        return dict(active=self.peek('boss', 0), hp=self.peek('boss', 1), state=self.peek('boss', 2),
                    x=self.s16('boss', 9) / 16, y=self.s16('boss', 11) / 16)
    def hold(self, *b):
        for x in list(self.held):
            if x not in b: self.pb.button_release(x); self.held.discard(x)
        for x in b:
            if x not in self.held: self.pb.button_press(x); self.held.add(x)
    def release(self): self.hold()
    def tap(self, b, n=3, extra=3):
        keep = set(self.held)
        self.pb.button_press(b); self.tick(n); self.pb.button_release(b); self.tick(extra)
    def shot(self, name):
        self.pb.screen.image.convert('RGB').resize((480, 432)).save('preview/shots/%s.png' % name)
    def start_game(self, cont=False):
        self.tick(150)
        self.tap('start', 4); self.tick(120)
    def skip_dialog(self, n=12):
        for _ in range(n):
            self.tick(60); self.tap('a', 3)
