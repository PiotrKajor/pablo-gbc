#pragma bank 255
/* PABLO - rooms, player, enemies, combat, drawing, main loop (banked) */
#include "game.h"

static const int8_t bob_tab[16] = { 0, 1, 2, 3, 3, 4, 4, 4, 4, 4, 3, 3, 2, 1, 0, 0 };
static const uint8_t room_song[NUM_ROOMS] = { SONG_CAVE, SONG_CAVE, SONG_CAVE, SONG_CAVE, SONG_QUIET, SONG_CAVE, SONG_QUIET };

static void load_room_data(uint8_t id) {
    uint8_t i, y;
    cur_room = id;
    room_load(id, map, &meta);
    gfx_theme_pals(meta.theme, bgpal);
    memset(en, 0, sizeof(en));
    memset(pr, 0, sizeof(pr));
    memset(pt, 0, sizeof(pt));
    memset(&boss, 0, sizeof(boss));
    item_on = 0;
    for (i = 0; i < meta.nent; i++) {
        Ent *e = &meta.ent[i];
        switch (e->type) {
        case ENT_CRAWLID: spawn_enemy(E_CRAWL, e->tx, e->ty); break;
        case ENT_FLY: spawn_enemy(E_FLY, e->tx, e->ty); break;
        case ENT_CLOAK: item_on = !(gflags & GF_DASH); break;
        case ENT_HEART: item_on = (gflags & GF_BOSSDEAD) && !(gflags & GF_ENDED); break;
        case ENT_BOSS:
            if (!(gflags & GF_BOSSDEAD)) {
                boss.active = 1;
                boss.hp = BOSS_HP;
                boss.state = B_SLEEP;
                boss.x = ((int16_t)e->tx * 8) << 4;
                boss.y = (int16_t)BOSS_FLOOR_Y << 4;
                boss.face = 1;
            }
            break;
        }
    }
    for (y = 0; y < 16; y++) put_tiles(0, y + 2, 20, &map[y * 20]);
    hud_draw();
    clear_row(1);
    boss_bar_dirty = 0;
}

static void show_banner(void) {
    uint8_t n = 0;
    while (meta.name[n]) n++;
    clear_row(1);
    put_text((20 - n) / 2, 1, meta.name);
    banner = 150;
}

static void enter_room(uint8_t id, uint8_t dir) {
    fade_out();
    DISPLAY_OFF;
    load_room_data(id);
    if (dir == 1) { p.x = ((int16_t)2) << 4; }
    else if (dir == 2) { p.x = ((int16_t)142) << 4; }
    else if (dir == 3) { p.y = ((int16_t)112) << 4; p.vy = -64; p.boost = 40; }
    else if (dir == 4) { p.y = ((int16_t)8) << 4; }
    if (p.y < (16 << 4)) { if (dir != 4) p.y = (int16_t)16 << 4; }
    if (p.y > ((int16_t)126 << 4) && dir != 3) p.y = ((int16_t)120 << 4);
    p.safe_x = p.x; p.safe_y = p.y;
    SHOW_SPRITES; SHOW_BKG;
    gfx_obj_pals(objpal);
    DISPLAY_ON;
    fade_apply(4);
    show_banner();
    music_room = room_song[id];
    if (!(id == 6 && boss.active && boss.state != B_SLEEP)) music_play(music_room);
    draw_world();
    fade_in();
}

static void player_reset_vitals(void) {
    p.hp = p.maxhp;
    p.hurt = 0; p.stun = 0; p.atk = 0; p.atk_cd = 0; p.dash = 0; p.focus = 0; p.dead = 0;
    p.vx = 0; p.vy = 0;
}

static void spawn_at_bench(void) {
    p.x = ((int16_t)save_bx * 8) << 4;
    p.y = ((int16_t)save_by * 8 + 8) << 4;
}

static void player_hazard(void) {
    /* spike / pit: damage and put Pablo back on safe ground */
    player_hurt(1, 0);
    if (!p.dead) {
        p.x = p.safe_x; p.y = p.safe_y;
        p.vx = 0; p.vy = 0;
    }
}

static void player_update(void) {
    int8_t dir = 0;
    int16_t px, py, nx, ny;
    int8_t steps, sd;
    uint8_t moved;

    if (p.hurt) p.hurt--;
    if (p.boost && (p.vy >= 0 || !--p.boost)) p.boost = 0;
    if (p.atk_cd) p.atk_cd--;
    if (p.dash_cd) p.dash_cd--;
    if (p.coyote) p.coyote--;
    if (p.jbuf) p.jbuf--;

    if (HELD(J_LEFT)) dir = -1;
    if (HELD(J_RIGHT)) dir = 1;

    if (p.stun) {
        p.stun--;
    } else if (p.dash) {
        p.dash--;
        p.vx = p.face ? -64 : 64;
        p.vy = 0;
        if (!p.dash) { p.vx = p.face ? -16 : 16; p.dash_cd = 14; }
    } else {
        /* focus */
        if (p.ground && HELD(J_START) && p.soul >= 33 && p.hp < p.maxhp && !HELD(J_LEFT | J_RIGHT)) {
            p.focus++;
            p.vx = 0;
            if ((p.focus & 7) == 1) part_spawn(1, (p.x >> 4) + 4 + (rnd() & 7), (p.y >> 4) + 14, 0, -1, 24);
            if (p.focus == 1) sfx_play(SFX_HEAL);
            if (p.focus >= 70) {
                p.focus = 0;
                p.soul -= 33;
                p.hp++;
                hud_dirty = 1;
                sfx_play(SFX_PICKUP);
                part_spawn(0, (p.x >> 4) + 8, (p.y >> 4) + 6, 0, 0, 9);
            }
        } else {
            p.focus = 0;
        }
        if (!p.focus) {
            /* walking */
            if (dir) {
                p.face = dir < 0;
                p.vx += dir * 6;
                if (p.vx > 24) p.vx = 24;
                if (p.vx < -24) p.vx = -24;
            } else {
                if (p.vx > 6) p.vx -= 6;
                else if (p.vx < -6) p.vx += 6;
                else p.vx = 0;
            }
            /* jump */
            if (PRESSED(J_A)) p.jbuf = 5;
            if (p.jbuf && (p.ground || p.coyote)) {
                p.vy = -58;
                p.ground = 0; p.coyote = 0; p.jbuf = 0;
                sfx_play(SFX_JUMP);
            }
            if (!HELD(J_A) && p.vy < -20 && !p.boost) p.vy = -20;
            /* attack */
            if (PRESSED(J_B) && !p.atk_cd) {
                p.atk = 14; p.atk_cd = 18; p.swing++;
                sfx_play(SFX_ATTACK);
            }
            /* dash */
            if (PRESSED(J_SELECT) && (gflags & GF_DASH) && !p.dash_cd && (p.ground || p.air_dash == 0)) {
                p.dash = 11;
                if (!p.ground) p.air_dash = 1;
                p.atk = 0;
                sfx_play(SFX_DASH);
            }
        }
    }
    if (p.atk) p.atk--;

    /* gravity */
    if (!p.dash) {
        p.vy += 4;
        if (p.vy > 64) p.vy = 64;
    }

    /* ---- move X */
    nx = p.x + p.vx;
    steps = (int8_t)((nx >> 4) - (p.x >> 4));
    sd = steps < 0 ? -1 : 1;
    moved = 1;
    while (steps) {
        px = (p.x >> 4) + sd;
        py = p.y >> 4;
        if (box_flags(px + HX, py + HY, HW, HH) & F_SOLID) { moved = 0; p.vx = 0; if (p.dash) p.dash = 1; break; }
        p.x += sd * 16;
        steps -= sd;
    }
    if (moved) p.x = nx;

    /* ---- move Y */
    ny = p.y + p.vy;
    steps = (int8_t)((ny >> 4) - (p.y >> 4));
    sd = steps < 0 ? -1 : 1;
    moved = 1;
    while (steps) {
        px = p.x >> 4;
        py = (p.y >> 4) + sd;
        if (sd > 0) {
            if ((box_flags(px + HX, py + HY, HW, HH) & F_SOLID) || oneway_below(px, p.y >> 4)) { moved = 0; if (p.vy > 40) sfx_play(SFX_LAND); p.vy = 0; break; }
        } else {
            if (box_flags(px + HX, py + HY, HW, HH) & F_SOLID) { moved = 0; p.vy = 0; break; }
        }
        p.y += sd * 16;
        steps -= sd;
    }
    if (moved) p.y = ny;

    /* ground detection */
    px = p.x >> 4; py = p.y >> 4;
    p.ground = 0;
    if (p.vy >= 0) {
        if ((box_flags(px + HX, py + HY + 1, HW, HH) & F_SOLID) || oneway_below(px, py)) p.ground = 1;
    }
    if (p.ground) {
        p.coyote = 5;
        p.air_dash = 0;
        if (!(box_flags(px + HX - 1, py + HY, HW + 2, HH + 2) & F_HAZARD) && !(box_flags(px + HX, py + 16, HW, 1) & F_HAZARD)) {
            p.safe_x = p.x; p.safe_y = p.y;
        }
    }

    /* hazards */
    if (!p.dead && (box_flags(px + HX + 1, py + HY + 4, HW - 2, HH - 4) & F_HAZARD)) player_hazard();
    if (!p.dead && meta.exit_d == NO_EXIT && py > 140) player_hazard();
}

static void enemy_update(Enemy *e) {
    int16_t ex = e->x >> 4, ey = e->y >> 4;
    int16_t pcx = (p.x >> 4) + 8, pcy = (p.y >> 4) + 8;
    if (e->flash) e->flash--;
    if (e->timer) {
        /* knockback */
        e->timer--;
        e->x += e->vx;
        if (e->type == E_CRAWL) {
            if (px_solid((e->x >> 4) + (e->vx > 0 ? 15 : 0), ey + 10)) e->x -= e->vx;
        }
    } else if (e->type == E_CRAWL) {
        int16_t fx = e->dir ? ex + 16 : ex - 1;
        if (px_solid(fx, ey + 10)) e->dir ^= 1;
        else {
            uint8_t fl = cell_flags((int8_t)(fx >> 3), (int8_t)((ey + 16 - 16) >> 3));
            if (!(fl & (F_SOLID | F_ONEWAY))) e->dir ^= 1;
        }
        e->x += e->dir ? 8 : -8;
    } else {
        /* vengefly */
        int16_t dx = pcx - (ex + 8), dy = pcy - (ey + 8);
        if (e->state == 0) {
            e->y = e->oy + ((int16_t)bob_tab[(frame >> 2) & 15] << 4);
            if (dx < 56 && dx > -56 && dy < 48 && dy > -48) e->state = 1;
        } else {
            if (dx > 0) { if (e->vx < 11) e->vx += 1; } else { if (e->vx > -11) e->vx -= 1; }
            if (dy > 0) { if (e->vy < 9) e->vy += 1; } else { if (e->vy > -9) e->vy -= 1; }
            if (!(box_flags((e->x + e->vx) / 16 + 2, ey + 4, 12, 10) & F_SOLID)) e->x += e->vx; else e->vx = 0;
            if (!(box_flags(ex + 2, (e->y + e->vy) / 16 + 4, 12, 10) & F_SOLID)) e->y += e->vy; else e->vy = 0;
            e->oy = e->y;
            if (dx > 110 || dx < -110) e->state = 0;
        }
        e->dir = dx < 0;
    }
    ex = e->x >> 4; ey = e->y >> 4;
    /* contact */
    if (!p.hurt && !p.dead) {
        int16_t bx = ex + (e->type == E_CRAWL ? 1 : 2), by = ey + (e->type == E_CRAWL ? 6 : 4);
        uint8_t bw = e->type == E_CRAWL ? 14 : 12, bh = 10;
        if (overlap((p.x >> 4) + HX, (p.y >> 4) + HY, HW, HH, bx, by, bw, bh))
            player_hurt(1, (pcx < ex + 8) ? -1 : 1);
    }
}

static void enemy_hit(Enemy *e) {
    e->hp--;
    e->flash = 6;
    e->timer = 8;
    e->vx = p.face ? -30 : 30;
    sfx_play(SFX_HIT);
    part_spawn(0, (e->x >> 4) + 8, (e->y >> 4) + 8, 0, 0, 9);
    if (p.soul < 99) { p.soul = (p.soul > 88) ? 99 : p.soul + 11; hud_dirty = 1; }
    hitstop = 3;
    if (!e->hp) {
        kill_fx((e->x >> 4) + 8, (e->y >> 4) + 8);
        e->type = 0;
    }
}

static void attack_check(void) {
    int16_t ax, ay, px = p.x >> 4, py = p.y >> 4;
    uint8_t i;
    if (!(p.atk <= 11 && p.atk >= 4)) return;
    ay = py + 2;
    ax = p.face ? px - 16 + 5 : px + 11;
    for (i = 0; i < MAX_EN; i++) {
        Enemy *e = &en[i];
        if (!e->type || e->swing == p.swing) continue;
        if (overlap(ax, ay, 16, 14, (e->x >> 4) + 1, (e->y >> 4) + 4, 14, 12)) {
            e->swing = p.swing;
            enemy_hit(e);
        }
    }
    if (boss.active && boss.state != B_SLEEP && boss.state != B_DEAD && boss.swing != p.swing) {
        if (overlap(ax, ay, 16, 14, (boss.x >> 4) + 3, (boss.y >> 4) + 8, 26, 24)) {
            boss.swing = p.swing;
            boss_hit();
        }
    }
}

static void find_interaction(void) {
    uint8_t i;
    int16_t pcx = (p.x >> 4) + 8, pcy = (p.y >> 4) + 8;
    near_kind = 0;
    for (i = 0; i < meta.nent; i++) {
        Ent *e = &meta.ent[i];
        int16_t cx = (int16_t)e->tx * 8 + 8, cy = (int16_t)e->ty * 8 + 16 + 4;
        int16_t dx = pcx - cx, dy = pcy - cy;
        if (e->type == ENT_NPC || e->type == ENT_TABLET || e->type == ENT_BENCH) {
            if (dx < 0) dx = -dx;
            if (dy < 0) dy = -dy;
            if (dx < 18 && dy < 18) { near_kind = e->type; near_idx = i; return; }
        }
    }
}

static uint8_t npc_text(uint8_t kind) {
    switch (kind) {
    case 0:
        if (!(gflags & GF_ELDER)) { gflags |= GF_ELDER; return TXT_ELDER1; }
        return (gflags & GF_DASH) ? TXT_ELDER3 : TXT_ELDER2;
    case 1:
        if (!(gflags & GF_WAND)) { gflags |= GF_WAND; return TXT_WANDERER; }
        return TXT_WANDERER2;
    case 2:
        gflags |= GF_ARCH;
        return (gflags & GF_DASH) ? TXT_ARCHIVIST2 : TXT_ARCHIVIST;
    default:
        gflags |= GF_GATE;
        return (gflags & GF_BOSSDEAD) ? TXT_GATEKEEPER2 : TXT_GATEKEEPER;
    }
}

static void bench_rest(Ent *e) {
    have_bench = 1;
    save_room = cur_room; save_bx = e->tx; save_by = e->ty;
    p.hp = p.maxhp;
    hud_dirty = 1;
    save_game();
    sfx_play(SFX_SAVE);
    part_spawn(0, (p.x >> 4) + 8, (p.y >> 4) + 6, 0, 0, 9);
    part_spawn(1, (p.x >> 4) + 4, (p.y >> 4) + 14, -1, -1, 24);
    part_spawn(1, (p.x >> 4) + 12, (p.y >> 4) + 14, 1, -1, 24);
    clear_row(1);
    put_text(7, 1, "SAVED");
    banner = 90;
}

static void check_items(void) {
    uint8_t i;
    if (!item_on) return;
    for (i = 0; i < meta.nent; i++) {
        Ent *e = &meta.ent[i];
        if (e->type == ENT_CLOAK || e->type == ENT_HEART) {
            int16_t ix = (int16_t)e->tx * 8, iy = (int16_t)e->ty * 8 + 8;
            if (overlap((p.x >> 4) + HX, (p.y >> 4) + HY, HW, HH, ix + 2, iy + 2, 12, 12)) {
                item_on = 0;
                if (e->type == ENT_CLOAK) {
                    gflags |= GF_DASH;
                    sfx_play(SFX_PICKUP);
                    music_stop();
                    dialog(TXT_CLOAK_GOT);
                    music_play(music_room);
                    save_game();
                } else {
                    p.vx = 0;
                    /* ending is handled by the main loop */
                    p.dead = 2;
                }
            }
        }
    }
}

static void draw_player(void) {
    uint8_t f, vis = 1;
    int16_t px = p.x >> 4, py = p.y >> 4;
    if (p.dead == 1) {
        hide(0, 4);
        return;
    }
    if (p.hurt && p.stun == 0 && ((p.hurt >> 2) & 1)) vis = 0;
    if (p.stun) f = 10;
    else if (p.focus) f = 11;
    else if (p.dash) f = 9;
    else if (p.atk) f = 8;
    else if (!p.ground) f = (p.vy < 0) ? 6 : 7;
    else if (p.vx > 2 || p.vx < -2) f = 2 + ((frame >> 2) & 3);
    else f = (frame >> 5) & 1;
    if (vis) draw16(0, px, py, PF(f), 0, p.face);
    else hide(0, 2);
    /* slash */
    if (p.atk >= 3 && p.atk <= 12 && !p.stun) {
        uint8_t sf = (p.atk > 9) ? 0 : (p.atk > 6 ? 1 : 2);
        draw16(2, p.face ? px - 13 : px + 13, py, SPR_SLASH0 + sf * 4, 1, p.face);
    } else hide(2, 2);
}

void draw_world(void) BANKED {
    uint8_t i;
    int16_t cx, cy;
    draw_player();
    for (i = 0; i < MAX_EN; i++) {
        Enemy *e = &en[i];
        if (!e->type) { hide(4 + i * 2, 2); continue; }
        if (e->type == E_CRAWL)
            draw16(4 + i * 2, e->x >> 4, e->y >> 4, SPR_CRAWL0 + ((frame >> 3) & 1) * 4, e->flash ? 7 : 2, !e->dir);
        else
            draw16(4 + i * 2, e->x >> 4, e->y >> 4, SPR_FLY0 + ((frame >> 2) & 1) * 4, e->flash ? 7 : 3, e->dir);
    }
    /* NPCs, tablets, items */
    hide(12, 2);
    hide(14, 2);
    move_sprite(16, 0, 0);
    for (i = 0; i < meta.nent; i++) {
        Ent *e = &meta.ent[i];
        cx = (int16_t)e->tx * 8;
        cy = (int16_t)e->ty * 8 + 8;
        if (e->type == ENT_NPC) {
            int16_t pcx = (p.x >> 4) + 8;
            draw16(12, cx, cy, SPR_NPC0 + e->arg * 8 + ((frame >> 5) & 1) * 4, 5, pcx < cx + 8);
        } else if (e->type == ENT_CLOAK && item_on) {
            draw16(14, cx, cy - bob_tab[(frame >> 2) & 15] + 2, SPR_CLOAK, 6, 0);
        } else if (e->type == ENT_HEART && item_on) {
            draw16(14, cx, cy - bob_tab[(frame >> 2) & 15] + 2, SPR_HEART0 + ((frame >> 3) & 1) * 4, 4, 0);
        }
    }
    if (near_kind && !p.dead && !p.stun) {
        Ent *e = &meta.ent[near_idx];
        draw8(16, (int16_t)e->tx * 8 + (near_kind == ENT_BENCH ? 4 : 0), (int16_t)e->ty * 8 + 8 - 14 - bob_tab[(frame >> 2) & 15] / 2 - (near_kind == ENT_NPC ? 6 : 0), SPR_UPMARK, 1);
    }
    /* projectiles */
    for (i = 0; i < 3; i++)
        if (pr[i].on) draw8(17 + i, pr[i].x, 104, SPR_SHOCK0 + ((frame >> 2) & 1) * 2, 4);
        else move_sprite(17 + i, 0, 0);
    /* boss */
    if (boss.active) {
        uint8_t fr, pal = boss.flash ? 7 : 4, c, r;
        int16_t bx = boss.x >> 4, by = boss.y >> 4;
        if (boss.state == B_WIND || boss.state == B_STUN) fr = 2;
        else if (boss.state == B_CHARGE) fr = 3;
        else if (boss.state == B_JUMP) fr = 4;
        else fr = (frame >> 5) & 1;
        if (boss.state == B_WIND && (boss.timer & 4)) pal = 7;
        if (boss.state == B_SLEEP) fr = 2;
        for (c = 0; c < 4; c++)
            for (r = 0; r < 2; r++) {
                uint8_t slot = 26 + c * 2 + r;
                {
                    uint8_t art_c = (boss.face ? c : 3 - c);
                    set_sprite_tile(slot, SPR_BOSS0 + fr * 16 + (art_c * 2 + r) * 2);
                    set_sprite_prop(slot, pal | (boss.face ? 0 : S_FLIPX));
                    move_sprite(slot, bx + c * 8 + 8, by + r * 16 + 16);
                }
            }
    } else hide(26, 8);
    part_update();
}

static void update_frame(void) {
    uint8_t i;
    oldjoy = joy; joy = joypad();
    if (hitstop) { hitstop--; return; }
    if (p.dead == 0) player_update();
    else if (p.dead == 1) { p.vy += 0; }
    if (p.dead == 0) {
        attack_check();
        for (i = 0; i < MAX_EN; i++) if (en[i].type) enemy_update(&en[i]);
        if (boss.active) boss_update();
        proj_update();
        find_interaction();
        check_items();
        if (near_kind && PRESSED(J_UP) && p.ground && !p.stun) {
            Ent *e = &meta.ent[near_idx];
            p.vx = 0;
            if (near_kind == ENT_NPC) dialog(npc_text(e->arg));
            else if (near_kind == ENT_TABLET) dialog(e->arg);
            else bench_rest(e);
            oldjoy = joy;
        }
    }
    if (hud_dirty) hud_draw();
    if (boss_bar_dirty) { boss_bar_draw(); }
    if (banner) { banner--; if (!banner && !(boss.active && boss.state != B_SLEEP)) clear_row(1); }
    if (shake) { shake--; SCX_REG = (shake & 1) ? 1 : 0; SCY_REG = (shake & 2) ? 1 : 0; } else { SCX_REG = 0; SCY_REG = 0; }
    /* room exits */
    {
        int16_t cx = (p.x >> 4) + 8, cy = (p.y >> 4) + 8;
        if (cx < 0 && meta.exit_l != NO_EXIT) enter_room(meta.exit_l, 2);
        else if (cx >= 160 && meta.exit_r != NO_EXIT) enter_room(meta.exit_r, 1);
        else if (cy < 16 && meta.exit_u != NO_EXIT && p.vy < 0) enter_room(meta.exit_u, 3);
        else if (cy >= 150 && meta.exit_d != NO_EXIT) enter_room(meta.exit_d, 4);
    }
}

static void game_over_respawn(void) {
    uint8_t i;
    /* death animation */
    for (i = 0; i < 6; i++) part_spawn(0, (p.x >> 4) + 8, (p.y >> 4) + 8, (int8_t)(rnd() & 3) - 1, (int8_t)(rnd() & 3) - 2, 9);
    for (i = 0; i < 60; i++) { draw_world(); frame_sync(); }
    music_stop();
    fade_out();
    DISPLAY_OFF;
    if (!have_bench) { save_room = 0; save_bx = 7; save_by = 12; }
    player_reset_vitals();
    p.soul = 0;
    p.face = 0;
    spawn_at_bench();
    p.safe_x = p.x; p.safe_y = p.y;
    load_room_data(save_room);
    gfx_obj_pals(objpal);
    SHOW_SPRITES; SHOW_BKG;
    DISPLAY_ON;
    fade_apply(4);
    show_banner();
    music_room = room_song[save_room];
    music_play(music_room);
    draw_world();
    fade_in();
}

static void run_game(uint8_t new_game, uint8_t from_save) {
    uint8_t start_room;
    memset(&p, 0, sizeof(p));
    p.maxhp = 5;
    gflags = 0; have_bench = 0;
    if (from_save && load_game()) {
        have_bench = 1;
        start_room = save_room;
        gflags &= ~GF_ENDED;
    } else {
        start_room = 0;
        new_game = 1;
    }
    p.hp = p.maxhp;
    p.soul = 0;
    if (new_game) {
        /* find start from room 0 data */
        static RoomMeta m0;
        static uint8_t m[320];
        uint8_t i;
        room_load(0, m, &m0);
        save_bx = 7; save_by = 12;
        for (i = 0; i < m0.nent; i++) if (m0.ent[i].type == ENT_START) { save_bx = m0.ent[i].tx; save_by = m0.ent[i].ty; }
        gflags = 0;
        have_bench = 0;
        save_room = 0;
    }
    spawn_at_bench();
    p.safe_x = p.x; p.safe_y = p.y;
    music_stop();
    DISPLAY_OFF;
    gfx_load_ingame(tflags, tattr);
    gfx_obj_pals(objpal);
    SPRITES_8x16;
    SHOW_SPRITES; SHOW_BKG;
    HIDE_WIN;
    VBK_REG = 0;
    load_room_data(start_room);
    SCX_REG = SCY_REG = 0;
    DISPLAY_ON;
    fade_apply(4);
    show_banner();
    music_room = room_song[start_room];
    draw_world();
    fade_in();
    music_play(music_room);
    if (new_game) dialog(TXT_INTRO);
    while (1) {
        update_frame();
        draw_world();
        frame_sync();
        if (p.dead == 1) {
            game_over_respawn();
        } else if (p.dead == 2) {
            ending();
            return;
        }
    }
}

void game_main(void) BANKED {
    if (_cpu != CGB_TYPE) {
        /* GBC only: show nothing useful on DMG */
        while (1) { wait_vbl_done(); }
    }
    SWITCH_RAM(0);
#ifndef NOFAST
    cpu_fast();
#endif
    audio_init();
    SPRITES_8x16;
    while (1) {
        uint8_t m = title_screen();
        /* sprite data must be present for title arrow: load in-game gfx lazily */
        run_game(m == 1, m == 2);
    }
}

