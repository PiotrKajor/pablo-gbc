import sys; sys.path.insert(0,'tests')
import numpy as np
from pyboy import PyBoy
pb = PyBoy('build/pablo.gbc', window='null', sound_emulated=True)
pb.set_emulation_speed(0)
chunks = []
for i in range(60*12):
    pb.tick()
    a = pb.sound.ndarray.copy()
    chunks.append(a)
x = np.concatenate(chunks).astype(np.float32)
print('shape', x.shape, 'rate', pb.sound.sample_rate)
m = x.mean(axis=1) if x.ndim > 1 else x
sr = pb.sound.sample_rate
for sec in range(2, 12, 2):
    seg = m[sec*sr:(sec+1)*sr]
    rms = float(np.sqrt((seg**2).mean()))
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1/sr)
    top = f[np.argsort(spec)[-4:]]
    print('t=%ds rms=%.1f peaks=%s' % (sec, rms, sorted(int(t) for t in top)))
print('--- lead band (250-1400 Hz)')
for sec in range(1, 12, 1):
    seg = m[sec*sr:(sec+1)*sr]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); f = np.fft.rfftfreq(len(seg), 1/sr)
    band = (f > 250) & (f < 1400)
    e = float(spec[band].sum()); lo = float(spec[(f>60)&(f<250)].sum())
    print('t=%d lead/bass energy ratio=%.2f  lead peak=%d' % (sec, e/lo, int(f[band][np.argmax(spec[band])])))
