"""Pablo GBC - songs written as text. Notes: C2..B6, 'R' = rest. name:ticks"""

NOTE_IDX = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def parse(seq):
    out = []
    for tok in seq.split():
        n, l = tok.split(':')
        l = int(l)
        if n == 'R':
            out.append((0, l))
        else:
            name, octv = n[:-1], int(n[-1])
            idx = (octv - 2) * 12 + NOTE_IDX[name]
            assert 0 <= idx < 60, n
            out.append((idx + 1, l))
    return out


def total(p):
    return sum(l for _, l in p)


SONGS = {}


def song(name, tick, duty, ch1, ch3, ch1b=None):
    a, b = parse(ch1), parse(ch3)
    assert total(a) == total(b), (name, total(a), total(b))
    SONGS[name] = dict(tick=tick, duty=duty, ch1=a, ch3=b)


# 0: TITLE - slow, melancholic, A minor
song('TITLE', 9, 1,
     "E4:4 A4:4 C5:6 B4:2  A4:4 C5:4 F5:4 E5:2 D5:2  E5:6 D5:2 C5:4 G4:4  B4:4 D5:4 G5:6 E5:2 "
     "A4:6 C5:2 E5:4 D5:2 C5:2  C5:4 A4:4 F4:6 A4:2  D5:4 F5:4 A5:4 G5:2 F5:2  E5:10 R:6",
     "A2:8 E3:8  F2:8 C3:8  C3:8 G3:8  G2:8 D3:8  A2:8 E3:8  F2:8 C3:8  D3:8 A2:8  E2:8 B2:8")

# 1: CAVE - mysterious arpeggios, E minor
song('CAVE', 7, 2,
     "E4:2 G4:2 B4:2 E5:2 B4:2 G4:2 E4:2 G4:2  C4:2 E4:2 G4:2 C5:2 G4:2 E4:2 C4:2 E4:2  "
     "G4:2 B4:2 D5:2 G5:2 D5:2 B4:2 G4:2 B4:2  D4:2 F#4:2 A4:2 D5:2 A4:2 F#4:2 D4:2 F#4:2  "
     "B4:6 A4:2 G4:4 E4:4  G4:6 E4:2 C5:8  D5:6 B4:2 G4:8  A4:4 F#4:4 E4:8",
     "E2:8 B2:8  C3:8 G2:8  G2:8 D3:8  D3:8 A2:8  E2:8 B2:8  C3:8 G2:8  G2:8 D3:8  B2:8 F#2:8")

# 2: BOSS - driving, A minor
_am = "A2:2 A2:2 A3:2 A2:2 A2:2 A3:2 A2:2 E3:2"
_f = "F2:2 F2:2 F3:2 F2:2 F2:2 F3:2 F2:2 C3:2"
_e = "E2:2 E2:2 E3:2 E2:2 E2:2 E3:2 E2:2 B2:2"
_dm = "D2:2 D2:2 D3:2 D2:2 D2:2 D3:2 D2:2 A2:2"
song('BOSS', 5, 0,
     "A4:2 R:2 C5:2 R:2 E5:4 D5:2 C5:2  E5:2 R:2 E5:2 R:2 A5:4 G5:2 E5:2  "
     "A4:2 R:2 C5:2 R:2 F5:4 E5:2 C5:2  G#4:2 R:2 B4:2 R:2 E5:4 D5:2 B4:2  "
     "A4:2 R:2 C5:2 R:2 E5:4 D5:2 C5:2  E5:2 R:2 E5:2 R:2 A5:4 G5:2 E5:2  "
     "A4:2 R:2 D5:2 R:2 F5:4 E5:2 D5:2  E5:2 D5:2 C5:2 B4:2 G#4:4 B4:4",
     " ".join([_am, _am, _f, _e, _am, _am, _dm, _e]))

# 3: END - hopeful, C major
song('END', 10, 1,
     "E5:4 G5:4 C6:4 G5:2 E5:2  D5:4 G5:4 B5:4 G5:2 D5:2  C5:4 E5:4 A5:4 E5:2 C5:2  A4:4 C5:4 F5:6 E5:2  "
     "E5:4 G5:4 C6:4 G5:2 E5:2  D5:4 G5:4 B5:4 G5:2 D5:2  C5:4 E5:4 A5:4 G5:2 E5:2  F5:4 E5:4 C5:8",
     "C3:8 G3:8  G2:8 D3:8  A2:8 E3:8  F2:8 C3:8  C3:8 G3:8  G2:8 D3:8  A2:8 E3:8  F2:8 G2:8")

# 4: SAD (death / quiet) - short
song('QUIET', 12, 1,
     "A4:6 E4:6 C4:4  G4:6 D4:6 B3:4  A4:6 E4:6 C4:4  E4:16",
     "A2:16 G2:16 A2:16 E2:16")

SONG_ORDER = ['TITLE', 'CAVE', 'BOSS', 'END', 'QUIET']


def freq_tables():
    sq, wv = [], []
    for i in range(60):
        # C2 = 65.406 Hz
        f = 65.406 * (2 ** (i / 12.0))
        sq.append(2048 - round(131072 / f))
        wv.append(2048 - round(65536 / f))
    return sq, wv
