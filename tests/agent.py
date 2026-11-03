"""Uczciwy agent do PABLO: steruje WYŁĄCZNIE przyciskami (zero poke do RAM-u).
RAM jest tylko czytany (pozycje, HP). Decyzje: MPC na save_state/load_state PyBoya -
dla każdego szablonu wejść odgrywa ~40 klatek przyszłości, wybiera najlepszy, wykonuje 8 klatek, powtarza."""
import io, sys, os, shutil, random
sys.path.insert(0, os.path.dirname(__file__))
from lib import symbols
from pyboy import PyBoy

TL_B_TL, TL_FONT = 75, 85
B_SLEEP, B_IDLE, B_WIND, B_CHARGE, B_JUMP, B_RECOVER, B_STUN, B_DEAD = range(8)


class Agent:
    def __init__(self, rom, ram=None, keep_ram=False):
        self.sym = symbols(rom.replace('.gbc', '.noi') if os.path.exists(rom.replace('.gbc', '.noi')) else 'build/pablo.noi')
        self.rom = rom
        if not keep_ram and os.path.exists(rom + '.ram'): os.remove(rom + '.ram')
        if ram is not None: open(rom + '.ram', 'wb').write(ram)
        self.pb = PyBoy(rom, window='null', sound_emulated=False)
        self.pb.set_emulation_speed(0)
        self.held = set()
        self.frames = 0          # klatki "na serio" (bez rolloutów)
        self.dialogs = []        # przeczytane strony dialogów
        self.rng = random.Random(1)
        self.log = print

    # ---------------------------------------------------------- RAM (tylko odczyt)
    def m(self, name, off=0): return self.pb.memory[self.sym['_' + name] + off]
    def s16(self, name, off):
        v = self.m(name, off) | (self.m(name, off + 1) << 8)
        return v - 65536 if v >= 32768 else v
    def P(self):
        return dict(x=self.s16('p', 0) / 16, y=self.s16('p', 2) / 16, ground=self.m('p', 9), hp=self.m('p', 12),
                    maxhp=self.m('p', 13), soul=self.m('p', 14), hurt=self.m('p', 15), dead=int(self.m('p', 24) == 1), ending=int(self.m('p', 24) == 2))
    def B(self):
        return dict(active=self.m('boss', 0), hp=self.m('boss', 1), state=self.m('boss', 2), next=self.m('boss', 3),
                    x=self.s16('boss', 9) / 16, y=self.s16('boss', 11) / 16)
    def room(self): return self.m('cur_room')
    def flags(self): return self.m('gflags')
    def enemy_hp(self): return sum(self.m('en', i * 17 + 1) for i in range(4) if self.m('en', i * 17))
    def vram(self, x, y): return self.pb.memory[0, 0x9800 + y * 32 + x]
    def in_dialog(self): return self.vram(0, 0) == TL_B_TL and self.vram(19, 6) == TL_B_TL + 7
    def dialog_text(self):
        rows = []
        for r in range(1, 5):
            rows.append(''.join(chr(t - TL_FONT + 32) if TL_FONT <= t < TL_FONT + 64 else ' ' for t in (self.vram(c, r) for c in range(1, 19))).rstrip())
        return ' '.join(x for x in rows if x)

    # ---------------------------------------------------------- wejście
    def keys(self, ks):
        ks = set(ks)
        for k in self.held - ks: self.pb.button_release(k)
        for k in ks - self.held: self.pb.button_press(k)
        self.held = ks
    def step(self, ks=(), n=1, real=True):
        self.keys(ks)
        for _ in range(n):
            self.pb.tick(1, False)
            if real: self.frames += 1
    def tap(self, k, n=3, after=3):
        self.step({k}, n); self.step((), after)
    def snap(self):
        b = io.BytesIO(); self.pb.save_state(b); return (b, set(self.held))
    def restore(self, s):
        s[0].seek(0); self.pb.load_state(s[0]); self.held = set(s[1])

    # ---------------------------------------------------------- dialogi
    def finish_dialog(self, limit=3000):
        """Czeka aż strona się dopisze, czyta ją, A - dalej. Zwraca liczbę stron."""
        pages, last, t = 0, None, 0
        while self.in_dialog() and t < limit:
            self.step((), 4); t += 4
            txt = self.dialog_text()
            if self.vram(18, 5) == TL_FONT + ord('>') - 32 and txt != last:
                self.dialogs.append((self.room(), txt)); self.log('   [dialog] ' + txt)
                last = txt; pages += 1
                self.tap('a', 3, 6)
        if t >= limit: raise RuntimeError('dialog się nie kończy')
        self.step((), 4)
        return pages

    # ---------------------------------------------------------- planowanie
    def plans(self, toward, H, allow_focus):
        away = 'left' if toward == 'right' else 'right'
        P = {}
        P['idle'] = [()] * H
        for nm, d in (('to', toward), ('away', away)):
            P['walk_' + nm] = [(d,)] * H
            P['walk_' + nm + '_s'] = [(d,)] * 6 + [()] * (H - 6)
            for k in (0, 6):
                P['atk%d_%s' % (k, nm)] = [(d,)] * (k + 1) + [(d, 'b')] * 2 + [()] * (H - k - 3) if nm == 'to' else None
            P['jump_' + nm] = [(d, 'a')] * 14 + [(d,)] * (H - 14)
            P['jump_' + nm + '_s'] = [(d, 'a')] * 14 + [()] * (H - 14)
            for f in (5, 9, 13):
                P['jdash%d_%s' % (f, nm)] = [(d, 'a')] * f + [(d, 'a', 'select')] * 2 + [(d,)] * (H - f - 2)
            P['dash_' + nm] = [(d,)] + [(d, 'select')] * 2 + [()] * (H - 3)
            P['dash_' + nm + '_run'] = [(d,)] + [(d, 'select')] * 2 + [(d,)] * (H - 3)
        P['jump'] = [('a',)] * 14 + [()] * (H - 14)
        P['down'] = [('down',)] * 10 + [()] * (H - 10)
        P['down_to'] = [('down', toward)] * 10 + [(toward,)] * (H - 10)
        P['jump_atk'] = [(toward, 'a')] * 8 + [(toward, 'a', 'b')] * 2 + [(toward,)] * (H - 10)
        if allow_focus: P['focus'] = [('start',)] * H
        return {k: v for k, v in P.items() if v}

    def rollout(self, plan, score, stop):
        for i, ks in enumerate(plan):
            self.step(ks, 1, real=False)
            if stop(): break
        return score()

    def mpc(self, toward, score, stop, H=40, C=8, allow_focus=False, prefer=None):
        s0 = self.snap()
        best, bname, bplan = -1e18, None, None
        for name, plan in self.plans(toward, H, allow_focus).items():
            self.restore(s0)
            sc = self.rollout(plan, score, stop) + self.rng.random() * 0.01
            if prefer and name.startswith(prefer): sc += 0.5
            if sc > best: best, bname, bplan = sc, name, plan
        self.restore(s0)
        for ks in bplan[:C]:
            self.step(ks, 1)
            if self.in_dialog() or self.P()['dead']: break
        return bname, best

    # ---------------------------------------------------------- nawigacja
    def goto(self, room, x=None, y=None, exit_to=None, tol=3, max_steps=400, prefer=None):
        """Idzie do (x,y) w pokoju `room` albo do pokoju `exit_to`. Walczy z wrogami, unika obrażeń."""
        for it in range(max_steps):
            if self.in_dialog(): self.finish_dialog(); continue
            p = self.P()
            if p['dead']: return 'dead'
            r = self.room()
            if exit_to is not None and r == exit_to: return 'ok'
            if exit_to is None and r == room and abs(p['x'] - x) <= tol and (y is None or abs(p['y'] - y) <= 4) and p['ground']:
                self.step((), 2); return 'ok'
            hp0, ehp0 = p['hp'], self.enemy_hp()
            def score():
                q = self.P(); rr = self.room()
                s = -400 * max(0, hp0 - q['hp']) - 5000 * q['dead'] + 15 * (ehp0 - self.enemy_hp() if rr == r else 0)
                if exit_to is not None:
                    if rr == exit_to: return s + 10000
                    if rr != r: return s - 5000
                    tx = {'l': -30, 'r': 190}.get(self.exit_dir, x if x is not None else 80)
                    s -= abs(q['x'] - tx)
                    if self.exit_dir == 'd': s -= abs(q['x'] - x) + (200 - q['y'])
                    if self.exit_dir == 'u': s -= abs(q['x'] - x) * 0.5 + q['y'] * 2
                else:
                    if rr != r: return s - 5000
                    s -= abs(q['x'] - x) + (abs(q['y'] - y) * 2 if y is not None else 0)
                return s
            stop = lambda: self.P()['dead'] or self.in_dialog() or self.room() != r
            if exit_to is not None:
                tgt = {'l': -30, 'r': 190}.get(self.exit_dir, x)
            else: tgt = x
            toward = 'right' if tgt > p['x'] else 'left'
            self.mpc(toward, score, stop, H=40, C=8, prefer=prefer)
        return 'timeout'

    def go_exit(self, d, to, x=None, **kw):
        self.exit_dir = d
        return self.goto(self.room(), x=x, exit_to=to, **kw)

    def talk(self):
        """UP przy NPC/tabliczce/ławce; zwraca liczbę stron dialogu (0 = np. ławka)."""
        self.tap('up', 3, 4)
        n = 0
        for _ in range(10):
            if self.in_dialog(): n = self.finish_dialog(); break
            self.step((), 2)
        return n

    # ---------------------------------------------------------- boss
    def fight_boss(self, max_frames=20000):
        """Walka z Wardenem bez żadnych cheatów. Zwraca dict ze statystyką."""
        deaths, f0, hits_taken = 0, self.frames, 0
        while self.frames - f0 < max_frames:
            if self.in_dialog(): self.finish_dialog(); continue
            if self.flags() & 2: break
            p, b = self.P(), self.B()
            if p['dead']:
                deaths += 1; self.log('   ŚMIERĆ #%d (boss hp %d)' % (deaths, b['hp']))
                self.step((), 200)
                if self.room() != 5: self.log('   respawn w pokoju %d?!' % self.room())
                return dict(won=False, deaths=deaths, frames=self.frames - f0, hits=hits_taken, boss_hp=b['hp'], respawn_room=self.room(), respawn=self.P())
            if self.room() != 6: return dict(won=False, deaths=deaths, frames=self.frames - f0, hits=hits_taken, err='poza areną')
            if not b['active'] or b['state'] == B_DEAD:
                self.step((), 4); continue
            if b['state'] == B_SLEEP:
                self.step(('right',), 4); continue
            hp0, bhp0 = p['hp'], b['hp']
            def score():
                q, c = self.P(), self.B()
                s = 50 * (bhp0 - c['hp']) - 400 * max(0, hp0 - q['hp']) + 250 * max(0, q['hp'] - hp0) - 5000 * q['dead']
                if c['state'] == B_DEAD or c['hp'] == 0: return s + 5000
                ad = abs((q['x'] + 8) - (c['x'] + 16))
                s -= 0.4 * max(0, ad - 30)
                if ad < 22: s -= 40
                return s + q['soul'] * 0.05
            stop = lambda: self.P()['hp'] < hp0 or self.in_dialog()
            toward = 'right' if (b['x'] + 16) > (p['x'] + 8) else 'left'
            focus_ok = p['soul'] >= 33 and p['hp'] < p['maxhp'] and p['ground']
            self.mpc(toward, score, stop, H=44, C=8, allow_focus=focus_ok)
            q = self.P()
            if q['hp'] < hp0: hits_taken += hp0 - q['hp']; self.log('   -%d maska (hp %d, boss %d, stan %d)' % (hp0 - q['hp'], q['hp'], self.B()['hp'], self.B()['state']))
        won = bool(self.flags() & 2)
        return dict(won=won, deaths=deaths, frames=self.frames - f0, hits=hits_taken, hp_left=self.P()['hp'])
