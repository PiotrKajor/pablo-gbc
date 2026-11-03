/* PABLO - shared helpers, state and collision (lives in ROM bank 0) */
#include "game.h"

uint8_t map[320];
RoomMeta meta;
uint8_t cur_room;
uint8_t tflags[256], tattr[256];
uint16_t bgpal[32], objpal[32];
uint8_t joy, oldjoy;
uint8_t frame;
uint8_t gflags;
uint8_t save_room, save_bx, save_by, have_bench;
Player p;
Enemy en[MAX_EN];
Boss boss;
Proj pr[3];
Part pt[6];
uint8_t hitstop, shake, banner, hud_dirty, boss_bar_dirty;
uint8_t near_kind, near_idx;
uint8_t item_on;
uint8_t music_room;
static uint8_t rng = 77;

uint8_t rnd(void) {
    rng ^= rng << 3;
    rng ^= rng >> 5;
    rng ^= rng << 4;
    return rng;
}

void hide(uint8_t n, uint8_t cnt) {
    while (cnt--) move_sprite(n++, 0, 0);
}

void draw16(uint8_t slot, int16_t x, int16_t y, uint8_t tile, uint8_t pal, uint8_t flip) {
    if (x <= -16 || x >= 160 || y <= -16 || y >= 144) { move_sprite(slot, 0, 0); move_sprite(slot + 1, 0, 0); return; }
    if (flip) {
        set_sprite_tile(slot, tile + 2);
        set_sprite_tile(slot + 1, tile);
        set_sprite_prop(slot, pal | S_FLIPX);
        set_sprite_prop(slot + 1, pal | S_FLIPX);
    } else {
        set_sprite_tile(slot, tile);
        set_sprite_tile(slot + 1, tile + 2);
        set_sprite_prop(slot, pal);
        set_sprite_prop(slot + 1, pal);
    }
    move_sprite(slot, x + 8, y + 16);
    move_sprite(slot + 1, x + 16, y + 16);
}

void draw8(uint8_t slot, int16_t x, int16_t y, uint8_t tile, uint8_t pal) {
    if (x <= -8 || x >= 160 || y <= -16 || y >= 144) { move_sprite(slot, 0, 0); return; }
    set_sprite_tile(slot, tile);
    set_sprite_prop(slot, pal);
    move_sprite(slot, x + 8, y + 16);
}

uint16_t dim(uint16_t c, uint8_t l) {
    uint8_t r = c & 31, g = (c >> 5) & 31, b = (c >> 10) & 31;
    r = (uint8_t)((r * (4 - l)) >> 2);
    g = (uint8_t)((g * (4 - l)) >> 2);
    b = (uint8_t)((b * (4 - l)) >> 2);
    return (uint16_t)r | ((uint16_t)g << 5) | ((uint16_t)b << 10);
}

void frame_sync(void) {
    audio_update();
    wait_vbl_done();
    frame++;
}

void fade_apply(uint8_t l) {
    uint16_t tmp[32];
    uint8_t i;
    for (i = 0; i < 32; i++) tmp[i] = dim(bgpal[i], l);
    set_bkg_palette(0, 8, tmp);
    for (i = 0; i < 32; i++) tmp[i] = dim(objpal[i], l);
    set_sprite_palette(0, 8, tmp);
}

void fade_out(void) {
    uint8_t l;
    for (l = 1; l <= 4; l++) { fade_apply(l); frame_sync(); frame_sync(); }
}

void fade_in(void) {
    uint8_t l;
    for (l = 3; l != 255; l--) { fade_apply(l); frame_sync(); frame_sync(); }
}

void put_tiles(uint8_t x, uint8_t y, uint8_t w, const uint8_t *ids) {
    uint8_t a[20], i;
    for (i = 0; i < w; i++) a[i] = tattr[ids[i]];
    VBK_REG = 1;
    set_bkg_tiles(x, y, w, 1, a);
    VBK_REG = 0;
    set_bkg_tiles(x, y, w, 1, ids);
}

void win_put(uint8_t x, uint8_t y, uint8_t w, const uint8_t *ids) {
    uint8_t a[20], i;
    for (i = 0; i < w; i++) a[i] = tattr[ids[i]] | 0x80;
    VBK_REG = 1;
    set_win_tiles(x, y, w, 1, a);
    VBK_REG = 0;
    set_win_tiles(x, y, w, 1, ids);
}

void put_text(uint8_t x, uint8_t y, const char *s) {
    uint8_t row[20], n = 0;
    while (*s && n < 20) { row[n++] = TL_FONT + (uint8_t)(*s - 32); s++; }
    put_tiles(x, y, n, row);
}

void clear_row(uint8_t y) {
    uint8_t row[20], i;
    for (i = 0; i < 20; i++) row[i] = TL_HUDBG;
    put_tiles(0, y, 20, row);
}

void hud_draw(void) {
    uint8_t row[20], i, f;
    uint16_t fill;
    for (i = 0; i < 20; i++) row[i] = TL_HUDBG;
    for (i = 0; i < 5; i++)
        row[i] = (i < p.hp) ? TL_MASK_FULL : ((i < p.maxhp) ? TL_MASK_EMPTY : TL_HUDBG);
    fill = ((uint16_t)p.soul * 32) / 99;
    for (i = 0; i < 4; i++) {
        int16_t v = (int16_t)fill - (int16_t)i * 8;
        f = v < 0 ? 0 : (v > 8 ? 8 : (uint8_t)v);
        row[7 + i] = TL_SOUL0 + (i == 0 ? 0 : (i == 3 ? 18 : 9)) + f;
    }
    put_tiles(0, 0, 20, row);
    hud_dirty = 0;
}

void boss_bar_draw(void) {
    uint8_t row[20], i, f;
    int16_t v;
    uint16_t fill;
    for (i = 0; i < 20; i++) row[i] = TL_HUDBG;
    if (boss.active && boss.state != B_DEAD) {
        fill = ((uint16_t)boss.hp * 96) / BOSS_HP;
        for (i = 0; i < 12; i++) {
            v = (int16_t)fill - (int16_t)i * 8;
            f = v < 0 ? 0 : (v > 8 ? 8 : (uint8_t)v);
            row[4 + i] = TL_SOUL0 + (i == 0 ? 0 : (i == 11 ? 18 : 9)) + f;
        }
    }
    put_tiles(0, 1, 20, row);
    boss_bar_dirty = 0;
}

uint8_t cell_flags(int8_t tx, int8_t ty) {
    if (ty < 0) return meta.exit_u == NO_EXIT ? F_SOLID : 0;
    if (ty >= 16) return 0;
    if (tx < 0) return meta.exit_l == NO_EXIT ? F_SOLID : 0;
    if (tx >= 20) return meta.exit_r == NO_EXIT ? F_SOLID : 0;
    return tflags[map[((uint8_t)ty << 4) + ((uint8_t)ty << 2) + (uint8_t)tx]];
}

uint8_t box_flags(int16_t bx, int16_t by, uint8_t w, uint8_t h) {
    int8_t tx0 = (int8_t)(bx >> 3), tx1 = (int8_t)((bx + w - 1) >> 3);
    int8_t ty0 = (int8_t)((by - 16) >> 3), ty1 = (int8_t)((by - 16 + h - 1) >> 3);
    int8_t tx, ty;
    uint8_t f = 0;
    for (ty = ty0; ty <= ty1; ty++)
        for (tx = tx0; tx <= tx1; tx++) f |= cell_flags(tx, ty);
    return f;
}

uint8_t oneway_below(int16_t x, int16_t y) {
    int16_t feet = y + 16;
    int8_t tx0, tx1, tx, ty;
    if (feet & 7) return 0;
    if (HELD(J_DOWN)) return 0;
    ty = (int8_t)((feet - 16) >> 3);
    tx0 = (int8_t)((x + HX) >> 3);
    tx1 = (int8_t)((x + HX + HW - 1) >> 3);
    for (tx = tx0; tx <= tx1; tx++)
        if (cell_flags(tx, ty) & F_ONEWAY) return 1;
    return 0;
}

uint8_t px_solid(int16_t x, int16_t y) {
    return cell_flags((int8_t)(x >> 3), (int8_t)((y - 16) >> 3)) & F_SOLID;
}

void part_spawn(uint8_t kind, int16_t x, int16_t y, int8_t vx, int8_t vy, uint8_t life) {
    uint8_t i;
    for (i = 0; i < 6; i++)
        if (!pt[i].life) {
            pt[i].life = life; pt[i].kind = kind; pt[i].x = x; pt[i].y = y; pt[i].vx = vx; pt[i].vy = vy;
            return;
        }
}

void part_update(void) {
    uint8_t i;
    for (i = 0; i < 6; i++) {
        if (!pt[i].life) { move_sprite(20 + i, 0, 0); continue; }
        pt[i].life--;
        pt[i].x += pt[i].vx;
        pt[i].y += pt[i].vy;
        if (pt[i].kind == 0)
            draw8(20 + i, pt[i].x - 4, pt[i].y - 12, SPR_SPARK0 + ((9 - pt[i].life) / 3) * 2, 1);
        else
            draw8(20 + i, pt[i].x - 4, pt[i].y - 3, SPR_SPORE0 + ((pt[i].life >> 2) & 1) * 2, 4);
        if (!pt[i].life) move_sprite(20 + i, 0, 0);
    }
}

uint8_t save_sum(volatile uint8_t *s) {
    return (uint8_t)(s[2] + s[3] + s[4] + s[5] + s[6] + 0x5A);
}

void save_game(void) {
    volatile uint8_t *s = (volatile uint8_t *)0xA000;
    ENABLE_RAM;
    s[0] = 'P'; s[1] = 'B';
    s[2] = save_room; s[3] = save_bx; s[4] = save_by; s[5] = gflags; s[6] = p.maxhp;
    s[7] = save_sum(s);
    DISABLE_RAM;
}

uint8_t load_game(void) {
    volatile uint8_t *s = (volatile uint8_t *)0xA000;
    uint8_t ok = 0;
    ENABLE_RAM;
    if (s[0] == 'P' && s[1] == 'B' && s[7] == save_sum(s)) {
        save_room = s[2]; save_bx = s[3]; save_by = s[4]; gflags = s[5]; p.maxhp = s[6];
        ok = 1;
    }
    DISABLE_RAM;
    return ok;
}

void erase_save(void) {
    volatile uint8_t *s = (volatile uint8_t *)0xA000;
    ENABLE_RAM; s[0] = 0; s[1] = 0; DISABLE_RAM;
}

void spawn_enemy(uint8_t type, uint8_t tx, uint8_t ty) {
    uint8_t i;
    Enemy *e;
    for (i = 0; i < MAX_EN; i++) if (!en[i].type) break;
    if (i == MAX_EN) return;
    e = &en[i];
    memset(e, 0, sizeof(Enemy));
    e->type = type;
    e->x = ((int16_t)tx * 8) << 4;
    e->y = ((int16_t)ty * 8 + 8) << 4;
    e->oy = e->y;
    e->hp = (type == E_CRAWL) ? 2 : 3;
    e->dir = (tx & 1);
}

void player_hurt(uint8_t amount, int8_t dirx) {
    if (p.hurt || p.dead) return;
    p.hp = (p.hp > amount) ? p.hp - amount : 0;
    p.hurt = 80;
    p.stun = 14;
    p.focus = 0;
    p.dash = 0;
    p.atk = 0;
    p.vx = dirx * 26;
    p.vy = -34;
    hitstop = 5;
    shake = 8;
    hud_dirty = 1;
    sfx_play(SFX_HURT);
    if (p.hp == 0) { p.dead = 1; sfx_play(SFX_DIE); }
}

uint8_t overlap(int16_t ax, int16_t ay, uint8_t aw, uint8_t ah, int16_t bx, int16_t by, uint8_t bw, uint8_t bh) {
    return ax < bx + bw && bx < ax + aw && ay < by + bh && by < ay + ah;
}

void kill_fx(int16_t cx, int16_t cy) {
    sfx_play(SFX_KILL);
    part_spawn(0, cx, cy, 0, 0, 9);
    part_spawn(1, cx - 4, cy, -1, -1, 20);
    part_spawn(1, cx + 4, cy, 1, -1, 20);
}

