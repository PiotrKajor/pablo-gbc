#ifndef GAME_H
#define GAME_H
/* PABLO - A Hollow Tale  (Game Boy Color, GBDK-2020)
 * A: jump  B: nail  SELECT: dash (after Mothwing Cloak)  START(hold): focus  UP: talk / rest
 */
#include <gb/gb.h>
#include <gb/cgb.h>
#include <stdint.h>
#include <string.h>
#include "assets.h"
#include "audio.h"

/* ------------------------------------------------------------ constants */
#define F_SOLID   1
#define F_ONEWAY  2
#define F_HAZARD  4

#define GF_DASH      1
#define GF_BOSSDEAD  2
#define GF_ELDER     4
#define GF_WAND      8
#define GF_ARCH      16
#define GF_GATE      32
#define GF_ENDED     64

#define HX 3
#define HY 2
#define HW 10
#define HH 14

#define E_CRAWL 1
#define E_FLY   2
#define MAX_EN  4

#define PF(n) (SPR_PABLO0 + (n) * 4)

/* boss states */
#define B_SLEEP   0
#define B_IDLE    1
#define B_WIND    2
#define B_CHARGE  3
#define B_JUMP    4
#define B_RECOVER 5
#define B_STUN    6
#define B_DEAD    7
#define BOSS_HP   20
#define BOSS_FLOOR_Y 88   /* top-left y when standing (floor top 120 - 32) */

/* ------------------------------------------------------------ data */
typedef struct {
    int16_t x, y, vx, vy;
    uint8_t face, ground, coyote, jbuf;
    uint8_t hp, maxhp, soul;
    uint8_t hurt, stun;
    uint8_t atk, atk_cd, swing;
    uint8_t dash, dash_cd, air_dash;
    uint8_t focus;
    uint8_t dead, boost;
    int16_t safe_x, safe_y;
} Player;

typedef struct {
    uint8_t type, hp, dir, flash, timer, swing, state;
    int16_t x, y, vx, vy, oy;
} Enemy;

typedef struct {
    uint8_t active, hp, state, next, timer, face, flash, swing, intro;
    int16_t x, y, vx, vy;
} Boss;

typedef struct { uint8_t on, t; int16_t x; int8_t vx; } Proj;
typedef struct { uint8_t life, kind; int16_t x, y; int8_t vx, vy; } Part;


extern uint8_t map[320];
extern RoomMeta meta;
extern uint8_t cur_room;
extern uint8_t tflags[256], tattr[256];
extern uint16_t bgpal[32], objpal[32];
extern uint8_t joy, oldjoy;
extern uint8_t frame;
extern uint8_t gflags;
extern uint8_t save_room, save_bx, save_by, have_bench;
extern Player p;
extern Enemy en[MAX_EN];
extern Boss boss;
extern Proj pr[3];
extern Part pt[6];
extern uint8_t hitstop, shake, banner, hud_dirty, boss_bar_dirty;
extern uint8_t near_kind, near_idx;
extern uint8_t item_on;
extern uint8_t music_room;

#define PRESSED(k) ((joy & ~oldjoy) & (k))
#define HELD(k) (joy & (k))

/* ---- common.c (bank 0) ---- */
uint8_t rnd(void);
void hide(uint8_t n, uint8_t cnt);
void draw16(uint8_t slot, int16_t x, int16_t y, uint8_t tile, uint8_t pal, uint8_t flip);
void draw8(uint8_t slot, int16_t x, int16_t y, uint8_t tile, uint8_t pal);
uint16_t dim(uint16_t c, uint8_t l);
void frame_sync(void);
void fade_apply(uint8_t l);
void fade_out(void);
void fade_in(void);
void put_tiles(uint8_t x, uint8_t y, uint8_t w, const uint8_t *ids);
void win_put(uint8_t x, uint8_t y, uint8_t w, const uint8_t *ids);
void put_text(uint8_t x, uint8_t y, const char *s);
void clear_row(uint8_t y);
void hud_draw(void);
void boss_bar_draw(void);
uint8_t cell_flags(int8_t tx, int8_t ty);
uint8_t box_flags(int16_t bx, int16_t by, uint8_t w, uint8_t h);
uint8_t oneway_below(int16_t x, int16_t y);
uint8_t px_solid(int16_t x, int16_t y);
void part_spawn(uint8_t kind, int16_t x, int16_t y, int8_t vx, int8_t vy, uint8_t life);
void part_update(void);
uint8_t save_sum(volatile uint8_t *s);
void save_game(void);
uint8_t load_game(void);
void erase_save(void);
void spawn_enemy(uint8_t type, uint8_t tx, uint8_t ty);
void player_hurt(uint8_t amount, int8_t dirx);
uint8_t overlap(int16_t ax, int16_t ay, uint8_t aw, uint8_t ah, int16_t bx, int16_t by, uint8_t bw, uint8_t bh);
void kill_fx(int16_t cx, int16_t cy);

/* ---- game.c (banked) ---- */
void draw_world(void) BANKED;
void game_main(void) BANKED;
/* ---- scenes.c (banked) ---- */
void dialog(uint8_t id) BANKED;
void boss_update(void) BANKED;
void boss_hit(void) BANKED;
void proj_update(void) BANKED;
uint8_t title_screen(void) BANKED;
void credits(void) BANKED;
void ending(void) BANKED;
#endif
