#include <gb/gb.h>
#include <gb/cgb.h>
#include <stdio.h>
#include <gbdk/console.h>

void main(void) {
    palette_color_t pal[4] = { RGB8(0, 40, 60), RGB8(70, 110, 140), RGB8(160, 210, 230), RGB8(255, 255, 255) };
    if (_cpu == CGB_TYPE) set_bkg_palette(0, 1, pal);
    gotoxy(1, 2);
    printf("PABLO TEST 1");
    gotoxy(1, 4);
    printf(_cpu == CGB_TYPE ? "MODE: GBC (CGB)" : "MODE: DMG/NOT CGB");
    gotoxy(1, 6);
    printf("NO MAPPER NEEDED");
    gotoxy(1, 8);
    printf("IF YOU SEE THIS");
    gotoxy(1, 9);
    printf("THE CART WORKS.");
    SHOW_BKG;
    while (1) wait_vbl_done();
}
