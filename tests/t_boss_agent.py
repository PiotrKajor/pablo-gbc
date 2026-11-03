"""Boss bez cheatów: CONTINUE z ławki Stone Door, agent MPC, do 6 podejść. Arg: seed."""
import sys, time, shutil; sys.path.insert(0, 'tests')
from agent import Agent
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
ROM = 'build/boss%d.gbc' % seed
shutil.copy('build/pablo.gbc', ROM); shutil.copy('build/pablo.noi', ROM.replace('.gbc', '.noi'))
ram = bytearray(8192); ram[0:2] = b'PB'; ram[2:7] = bytes([5, 3, 12, 1 | 4 | 8 | 16 | 32, 5]); ram[7] = (sum(ram[2:7]) + 0x5A) & 255
A = Agent(ROM, ram=bytes(ram)); A.rng.seed(seed)
A.step((), 150); A.tap('start', 4); A.step((), 120 + seed * 7)
fights = []; t0 = time.time()
while len(fights) < 6:
    A.exit_dir = 'r'; A.goto(5, exit_to=6)
    t1 = time.time(); r = A.fight_boss(); r['wall_s'] = round(time.time() - t1); fights.append(r)
    print('podejście', len(fights), r, flush=True)
    if r['won']: break
print('WYNIK seed %d: %s po %d podejściach, łącznie %.0f s gry, %.0f s zegara' % (seed, 'WYGRANA' if fights[-1]['won'] else 'PRZEGRANA', len(fights), sum(f['frames'] for f in fights) / 60, time.time() - t0))
