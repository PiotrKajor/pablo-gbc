#pragma bank 255
/* PABLO - dialogue, boss, projectiles, title, ending (banked) */
#include "game.h"

static uint8_t dlg_buf[72];

static void dlg_frame_draw(void) {
    uint8_t row[20], i, y;
    row[0] = TL_B_TL; for (i = 1; i < 19; i++) row[i] = TL_B_T; row[19] = TL_B_TR;
    put_tiles(0, 0, 20, row);
    for (y = 1; y < 6; y++) {
        row[0] = TL_B_L; for (i = 1; i < 19; i++) row[i] = TL_B_FILL; row[19] = TL_B_R;
        put_tiles(0, y, 20, row);
    }
    row[0] = TL_B_BL; for (i = 1; i < 19; i++) row[i] = TL_B_B; row[19] = TL_B_BR;
    put_tiles(0, 6, 20, row);
}

void dialog(uint8_t id) BANKED {
    uint8_t np = text_npages(id), pg, pos, done, t, blink = 0, c;
    dlg_frame_draw();
    for (pg = 0; pg < np; pg++) {
        text_page(id, pg, dlg_buf);
        /* clear text rows */
        for (c = 1; c < 6; c++) {
            uint8_t row[18], i;
            for (i = 0; i < 18; i++) row[i] = TL_B_FILL;
            put_tiles(1, c, 18, row);
        }
        pos = 0; done = 0;
        /* last used pos */
        t = 72;
        while (t > 0 && dlg_buf[t - 1] == ' ') t--;
        while (1) {
            oldjoy = joy; joy = joypad();
            if (pos < t) {
                uint8_t n = HELD(J_A | J_B) ? 3 : 1;
                while (n-- && pos < t) {
                    uint8_t tile = TL_FONT + (dlg_buf[pos] - 32);
                    set_bkg_tiles(1 + pos % 18, 1 + pos / 18, 1, 1, &tile);
                    if (dlg_buf[pos] != ' ' && (pos & 1)) sfx_play(SFX_BLIP);
                    pos++;
                }
            } else {
                blink++;
                {
                    uint8_t tile = (blink & 16) ? (TL_FONT + ('>' - 32)) : TL_B_FILL;
                    set_bkg_tiles(18, 5, 1, 1, &tile);
                }
                if (PRESSED(J_A | J_B | J_START)) { done = 1; sfx_play(SFX_SELECT); }
            }
            draw_world();
            for (c = 0; c < 40; c++)
                if (shadow_OAM[c].y && shadow_OAM[c].y < 72) shadow_OAM[c].y = 0;
            frame_sync();
            if (done) break;
        }
        {
            uint8_t tile = TL_B_FILL;
            set_bkg_tiles(18, 5, 1, 1, &tile);
        }
    }
    {
        uint8_t y;
        for (y = 2; y < 7; y++) put_tiles(0, y, 20, &map[(y - 2) * 20]);
        hud_draw();
        if (boss.active && boss.state != B_SLEEP) boss_bar_draw(); else clear_row(1);
    }
    oldjoy = joy;
}

static void boss_start_wind(uint8_t next) {
    boss.state = B_WIND;
    boss.next = next;
    boss.timer = (boss.hp <= BOSS_HP / 2) ? 40 : 56;
    sfx_play(SFX_ROAR);
}

static void boss_spawn_wave(void) {
    uint8_t i, n = 0;
    int16_t cx = (boss.x >> 4) + 16;
    for (i = 0; i < 3 && n < 2; i++)
        if (!pr[i].on) {
            pr[i].on = 1; pr[i].t = 0; pr[i].x = cx + (n ? 8 : -12);
            pr[i].vx = n ? 2 : -2;
            n++;
        }
}

void boss_update(void) BANKED {
    int16_t bx = boss.x >> 4, by = boss.y >> 4;
    int16_t pcx = (p.x >> 4) + 8;
    uint8_t p2 = boss.hp <= BOSS_HP / 2;
    if (boss.flash) boss.flash--;

    switch (boss.state) {
    case B_SLEEP:
        if (pcx > 36 && p.ground) {
            /* seal the door and begin */
            uint8_t y, row[2];
            for (y = 9; y <= 12; y++) {
                map[y * 20] = TL_ROCK0; map[y * 20 + 1] = TL_ROCK0;
                row[0] = row[1] = TL_ROCK0;
                put_tiles(0, y + 2, 2, row);
            }
            music_stop();
            dialog(TXT_BOSS_INTRO);
            music_play(SONG_BOSS);
            boss.state = B_IDLE;
            boss.timer = 40;
            boss.face = 1;
            boss_bar_dirty = 1;
            sfx_play(SFX_ROAR);
            shake = 20;
        }
        return;
    case B_IDLE:
        boss.face = (pcx < bx + 16);
        {
            int16_t d = pcx - (bx + 16);
            if (d > 28) boss.x += p2 ? 10 : 7;
            else if (d < -28) boss.x -= p2 ? 10 : 7;
        }
        if (boss.x < (8 << 4)) boss.x = 8 << 4;
        if (boss.x > (112 << 4)) boss.x = 112 << 4;
        if (boss.timer) boss.timer--;
        else {
            int16_t d = pcx - (bx + 16);
            if (d < 0) d = -d;
            boss_start_wind((d > 56 && (rnd() & 3)) ? B_CHARGE : B_JUMP);
        }
        break;
    case B_WIND:
        boss.face = (pcx < bx + 16);
        if (boss.timer) boss.timer--;
        else {
            if (boss.next == B_CHARGE) { boss.state = B_CHARGE; boss.timer = 90; boss.vx = boss.face ? -(p2 ? 42 : 36) : (p2 ? 42 : 36); }
            else {
                int16_t d = (pcx - (bx + 16)) * 16 / 38;
                if (d > 44) d = 44;
                if (d < -44) d = -44;
                boss.state = B_JUMP; boss.vy = -76; boss.vx = d; boss.timer = 0;
                sfx_play(SFX_LAND);
            }
        }
        break;
    case B_CHARGE:
        boss.x += boss.vx;
        bx = boss.x >> 4;
        if (bx <= 8 || bx >= 112 || !boss.timer) {
            if (boss.timer) { shake = 14; sfx_play(SFX_SLAM); boss.state = B_STUN; boss.timer = 90; }
            else { boss.state = B_IDLE; boss.timer = 24; }
            if (bx < 8) boss.x = 8 << 4;
            if (bx > 112) boss.x = 112 << 4;
        } else boss.timer--;
        break;
    case B_JUMP:
        boss.x += boss.vx;
        boss.y += boss.vy;
        boss.vy += 4;
        if (boss.x < (8 << 4)) boss.x = 8 << 4;
        if (boss.x > (112 << 4)) boss.x = 112 << 4;
        if (boss.vy > 0 && boss.y >= ((int16_t)BOSS_FLOOR_Y << 4)) {
            boss.y = (int16_t)BOSS_FLOOR_Y << 4;
            boss.vy = 0; boss.vx = 0;
            boss.state = B_RECOVER; boss.timer = p2 ? 50 : 64;
            boss_spawn_wave();
            shake = 12;
            sfx_play(SFX_SLAM);
            if (p2) {
                uint8_t i, any = 0;
                for (i = 0; i < MAX_EN; i++) if (en[i].type) any = 1;
                if (!any) spawn_enemy(E_FLY, (boss.x >> 7) < 10 ? 14 : 3, 5);
            }
        }
        break;
    case B_RECOVER:
        if (boss.timer) boss.timer--;
        else { boss.state = B_IDLE; boss.timer = p2 ? 40 : 60; }
        break;
    case B_STUN:
        if (boss.timer) boss.timer--;
        else { boss.state = B_IDLE; boss.timer = 40; }
        break;
    case B_DEAD:
        if (boss.timer) {
            boss.timer--;
            if (!(boss.timer & 7)) {
                part_spawn(1, bx + 4 + (rnd() & 23), by + 6 + (rnd() & 23), 0, -1, 24);
                sfx_play(SFX_KILL);
            }
            if (boss.timer & 2) boss.flash = 2;
            shake = 2;
        } else {
            uint8_t y, row[2];
            boss.active = 0;
            gflags |= GF_BOSSDEAD;
            boss_bar_dirty = 1;
            boss_bar_draw();
            hide(26, 8);
            for (y = 9; y <= 12; y++) {
                map[y * 20] = TL_EMPTY; map[y * 20 + 1] = TL_EMPTY;
                row[0] = row[1] = TL_EMPTY;
                put_tiles(0, y + 2, 2, row);
            }
            dialog(TXT_BOSS_DEAD);
            music_play(SONG_QUIET);
            item_on = 1;
            save_game();
        }
        return;
    }
    bx = boss.x >> 4; by = boss.y >> 4;
    /* contact damage */
    if (!p.hurt && !p.dead && boss.state != B_SLEEP) {
        if (overlap((p.x >> 4) + HX, (p.y >> 4) + HY, HW, HH, bx + 3, by + 8, 26, 24))
            player_hurt(1, (pcx < bx + 16) ? -1 : 1);
    }
}

void boss_hit(void) BANKED {
    if (boss.hp > 1) boss.hp--; else boss.hp = 0;
    boss.flash = 6;
    sfx_play(SFX_HIT);
    part_spawn(0, (boss.x >> 4) + 16, (boss.y >> 4) + 18, 0, 0, 9);
    if (p.soul < 99) { p.soul = (p.soul > 88) ? 99 : p.soul + 11; hud_dirty = 1; }
    hitstop = 3;
    boss_bar_dirty = 1;
    if (!boss.hp) {
        boss.state = B_DEAD;
        boss.timer = 110;
        sfx_play(SFX_ROAR);
        music_stop();
        {
            uint8_t i;
            for (i = 0; i < MAX_EN; i++) en[i].type = 0;
            for (i = 0; i < 3; i++) pr[i].on = 0;
        }
    }
}

void proj_update(void) BANKED {
    uint8_t i;
    for (i = 0; i < 3; i++) {
        if (!pr[i].on) { move_sprite(17 + i, 0, 0); continue; }
        pr[i].x += pr[i].vx;
        pr[i].t++;
        if (pr[i].x < 4 || pr[i].x > 148 || px_solid(pr[i].x + 4, 112)) { pr[i].on = 0; continue; }
        if (!p.hurt && !p.dead &&
            overlap((p.x >> 4) + HX, (p.y >> 4) + HY, HW, HH, pr[i].x + 1, 104, 6, 16))
            player_hurt(1, pr[i].vx > 0 ? 1 : -1);
    }
}

static void center_text(uint8_t y, const char *str) {
    uint8_t n = 0;
    while (str[n]) n++;
    put_text((20 - n) >> 1, y, str);
}

void credits(void) BANKED {
    uint8_t y;
    music_play(SONG_END);
    fade_out();
    DISPLAY_OFF;
    hide(0, 40);
    HIDE_WIN;
    for (y = 0; y < 18; y++) clear_row(y);
    center_text(3, "PABLO");
    center_text(5, "A HOLLOW TALE");
    center_text(8, "THE END");
    center_text(11, "THANKS FOR PLAYING");
    center_text(13, "A FAN TRIBUTE TO");
    center_text(14, "HOLLOW KNIGHT");
    center_text(16, "PRESS START");
    DISPLAY_ON;
    fade_apply(4);
    fade_in();
    while (1) {
        oldjoy = joy; joy = joypad();
        if (PRESSED(J_START | J_A)) break;
        frame_sync();
    }
    fade_out();
}

void ending(void) BANKED {
    uint8_t i;
    music_stop();
    sfx_play(SFX_PICKUP);
    for (i = 0; i < 40; i++) { draw_world(); frame_sync(); }
    dialog(TXT_END1);
    gflags |= GF_ENDED;
    save_game();
    credits();
}

uint8_t title_screen(void) BANKED {
    uint8_t sel = 0, has_save, t = 0;
    uint16_t tpal[32];
    uint8_t i;
    DISPLAY_OFF;
    HIDE_WIN;
    HIDE_SPRITES;
    SPRITES_8x16;
    SCX_REG = SCY_REG = 0;
    gfx_load_ingame(tflags, tattr);
    gfx_load_title(tpal);
    memcpy(bgpal, tpal, sizeof(bgpal));
    has_save = load_game();
    if (has_save) sel = 1;
    if (!has_save) bgpal[29] = bgpal[30] = bgpal[31] = bgpal[28];
    gfx_obj_pals(objpal);
    set_bkg_palette(0, 8, bgpal);
    set_sprite_palette(0, 8, objpal);
    SHOW_BKG; SHOW_SPRITES;
    hide(0, 40);
    DISPLAY_ON;
    music_play(SONG_TITLE);
    fade_apply(4);
    fade_in();
    while (1) {
        oldjoy = joy; joy = joypad();
        t++;
        if (has_save) {
            if (PRESSED(J_UP | J_DOWN)) { sel ^= 1; sfx_play(SFX_SELECT); }
        }
        if (PRESSED(J_START | J_A)) { sfx_play(SFX_PICKUP); break; }
        draw8(0, 53 + ((t >> 4) & 1), 124 + 8 * sel, SPR_ARROWR, 1);
        /* soft glow on press line */
        i = (t >> 3) & 7;
        (void)i;
        frame_sync();
    }
    for (i = 0; i < 30; i++) { frame_sync(); }
    fade_out();
    hide(0, 40);
    return has_save ? (sel == 0 ? 1 : 2) : 1;  /* 1: new game, 2: continue */
}

