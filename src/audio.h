#ifndef AUDIO_H
#define AUDIO_H
#include <gb/gb.h>
#include <stdint.h>

enum { SFX_JUMP, SFX_ATTACK, SFX_HIT, SFX_HURT, SFX_DASH, SFX_HEAL, SFX_PICKUP, SFX_SAVE,
       SFX_BLIP, SFX_ROAR, SFX_DIE, SFX_SLAM, SFX_KILL, SFX_SELECT, SFX_LAND };

void audio_init(void) BANKED;
void music_play(uint8_t song) BANKED;
void music_stop(void) BANKED;
void audio_update(void) BANKED;
void sfx_play(uint8_t id) BANKED;
uint8_t music_current(void) BANKED;
#endif
