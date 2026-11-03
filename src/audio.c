#pragma bank 255
#include <gb/gb.h>
#include <stdint.h>
#include "assets.h"
#include "audio.h"

typedef struct { const uint8_t *ch1, *ch3; uint8_t tick, duty; } SongDef;
#include "music_data.inc"

/* sfx: part on channel 2 (square) and part on channel 4 (noise) */
typedef struct { uint8_t len2; uint16_t f2a, f2b; uint8_t v2, d2; uint8_t len4; uint8_t n4a, n4b, v4; } Sfx;
static const Sfx sfx_tab[] = {
    /* JUMP   */ { 8, 1500, 1800, 7, 2,   0, 0, 0, 0 },
    /* ATTACK */ { 0, 0, 0, 0, 0,         7, 0x40, 0x20, 9 },
    /* HIT    */ { 6, 1750, 1650, 10, 1,  8, 0x31, 0x11, 12 },
    /* HURT   */ { 20, 1700, 1100, 12, 2, 16, 0x51, 0x71, 12 },
    /* DASH   */ { 0, 0, 0, 0, 0,         14, 0x20, 0x50, 10 },
    /* HEAL   */ { 24, 1500, 1900, 8, 2,  0, 0, 0, 0 },
    /* PICKUP */ { 36, 1400, 1990, 10, 2, 0, 0, 0, 0 },
    /* SAVE   */ { 22, 1800, 1500, 9, 2,  0, 0, 0, 0 },
    /* BLIP   */ { 2, 1900, 1900, 4, 2,   0, 0, 0, 0 },
    /* ROAR   */ { 44, 300, 150, 15, 0,   44, 0x63, 0x73, 14 },
    /* DIE    */ { 44, 1600, 300, 12, 2,  44, 0x30, 0x77, 12 },
    /* SLAM   */ { 0, 0, 0, 0, 0,         24, 0x74, 0x50, 15 },
    /* KILL   */ { 10, 1700, 1200, 10, 1, 10, 0x31, 0x41, 10 },
    /* SELECT */ { 6, 1800, 1950, 7, 2,   0, 0, 0, 0 },
    /* LAND   */ { 0, 0, 0, 0, 0,         4, 0x44, 0x34, 6 },
};

static uint8_t song_cur = 255, playing;
static const uint8_t *p1, *p3;
static uint8_t t1, t3, fc, rest1;
static uint8_t s2_id, s2_t, s2_on, s4_t, s4_on;

void audio_init(void) BANKED {
    uint8_t i;
    NR52_REG = 0x80;
    NR50_REG = 0x77;
    NR51_REG = 0xFF;
    NR30_REG = 0x00;
    for (i = 0; i < 16; i++) {
        uint8_t a = (i * 2), b = (i * 2 + 1);
        uint8_t sa = a < 16 ? a : 31 - a;
        uint8_t sb = b < 16 ? b : 31 - b;
        ((volatile uint8_t *)0xFF30)[i] = (sa << 4) | sb;
    }
    NR30_REG = 0x80;
    playing = 0;
}

static void note_ch1(uint8_t n, uint8_t duty) {
    if (!n) { NR12_REG = 0x00; return; }
    NR11_REG = (uint8_t)(duty << 6);
    NR12_REG = 0xA3;
    NR13_REG = (uint8_t)(freq_sq[n - 1] & 0xFF);
    NR14_REG = 0x80 | (uint8_t)(freq_sq[n - 1] >> 8);
}
static void note_ch3(uint8_t n) {
    if (!n) { NR32_REG = 0x00; return; }
    NR30_REG = 0x80;
    NR32_REG = 0x20;
    NR33_REG = (uint8_t)(freq_wv[n - 1] & 0xFF);
    NR34_REG = 0x80 | (uint8_t)(freq_wv[n - 1] >> 8);
}

void music_play(uint8_t song) BANKED {
    if (song == song_cur && playing) return;
    song_cur = song;
    p1 = songs[song].ch1;
    p3 = songs[song].ch3;
    t1 = t3 = 1;
    fc = songs[song].tick;
    playing = 1;
}
void music_stop(void) BANKED {
    playing = 0;
    song_cur = 255;
    NR12_REG = 0;
    NR32_REG = 0;
}
uint8_t music_current(void) BANKED { return song_cur; }

static void step_music(void) {
    const SongDef *s = &songs[song_cur];
    if (--t1 == 0) {
        if (p1[0] == 255) p1 = s->ch1;
        note_ch1(p1[0], s->duty);
        t1 = p1[1];
        p1 += 2;
    }
    if (--t3 == 0) {
        if (p3[0] == 255) p3 = s->ch3;
        note_ch3(p3[0]);
        t3 = p3[1];
        p3 += 2;
    }
}

void sfx_play(uint8_t id) BANKED {
    const Sfx *s = &sfx_tab[id];
    if (s->len2) {
        s2_id = id; s2_t = 0; s2_on = 1;
        NR21_REG = (uint8_t)(s->d2 << 6);
        NR22_REG = (uint8_t)((s->v2 << 4) | 1);
        NR23_REG = (uint8_t)(s->f2a & 0xFF);
        NR24_REG = 0x80 | (uint8_t)(s->f2a >> 8);
    }
    if (s->len4) {
        s4_on = id + 1; s4_t = 0;
        NR41_REG = 0;
        NR42_REG = (uint8_t)((s->v4 << 4) | 1);
        NR43_REG = s->n4a;
        NR44_REG = 0x80;
    }
}

void audio_update(void) BANKED {
    if (playing) {
        if (++fc >= songs[song_cur].tick) {
            fc = 0;
            step_music();
        }
    }
    if (s2_on) {
        const Sfx *s = &sfx_tab[s2_id];
        s2_t++;
        if (s2_t >= s->len2) { s2_on = 0; NR22_REG = 0; }
        else {
            int16_t f = (int16_t)s->f2a + (int16_t)(((int32_t)((int16_t)s->f2b - (int16_t)s->f2a) * s2_t) / s->len2);
            NR23_REG = (uint8_t)(f & 0xFF);
            NR24_REG = (uint8_t)(f >> 8) & 0x07;
        }
    }
    if (s4_on) {
        const Sfx *s = &sfx_tab[s4_on - 1];
        s4_t++;
        if (s4_t >= s->len4) { s4_on = 0; NR42_REG = 0; }
        else {
            NR43_REG = (uint8_t)((int16_t)s->n4a + (((int16_t)s->n4b - (int16_t)s->n4a) * s4_t) / s->len4);
        }
    }
}
