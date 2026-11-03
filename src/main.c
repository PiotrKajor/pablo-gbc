#include <gb/gb.h>
#include <gb/cgb.h>
void game_main(void) BANKED;
void main(void) {
    /* boot beacon: if the screen turns teal, main() is running (white = code never started) */
    if (_cpu == CGB_TYPE) {
        palette_color_t p[4] = { RGB8(0, 48, 56), RGB8(0, 48, 56), RGB8(0, 48, 56), RGB8(0, 48, 56) };
        set_bkg_palette(0, 1, p);
    }
    game_main();
}
