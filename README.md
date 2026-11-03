# PABLO - A Hollow Tale (Game Boy Color)

Fanowska gra w stylu Hollow Knight na GBC (GBDK-2020, C). ROM: `build/pablo.gbc` (64 KB, MBC5+RAM+bateria, tylko CGB).

Sterowanie: A skok (przytrzymaj = wyzej), B nail, SELECT dash (po Mothwing Cloak), START (przytrzymaj) focus/leczenie,
GORA = rozmowa / odpoczynek i zapis na lawce.

## Build
    make            # generuje assety (assets/*.py -> src/assets_*.c) i kompiluje ROM
    .venv/bin/python tests/t_boss.py   # testy w PyBoy (headless); tests/sim.py = BFS osiagalnosci pokoi

## Struktura
- assets/art.py     - cala grafika (kafle, sprite'y, font, ekran tytulowy), proceduralnie
- assets/world.py   - 7 pokoi (DSL), encje, dialogi
- assets/music.py   - muzyka tekstem (4 utwory + cichy)
- src/common.c      - stan wspolny, kolizje, zapis (bank 0); src/game.c, src/scenes.c, src/audio.c - banki przelaczane
- tools/gbdk        - GBDK-2020 (nie w repo)

## Zrzuty ekranu

![01_tytul](screenshots/01_tytul.png)
![02_intro_dialog](screenshots/02_intro_dialog.png)
![03_pokoj_Moss_Hollow](screenshots/03_pokoj_Moss_Hollow.png)
![04_pokoj_Green_Path](screenshots/04_pokoj_Green_Path.png)
![05_pokoj_Luma_Cavern](screenshots/05_pokoj_Luma_Cavern.png)
![06_pokoj_The_Gap](screenshots/06_pokoj_The_Gap.png)
![07_pokoj_Archive_Cellar](screenshots/07_pokoj_Archive_Cellar.png)
![08_pokoj_Stone_Door](screenshots/08_pokoj_Stone_Door.png)
![09_dash](screenshots/09_dash.png)
![10_atak_nail](screenshots/10_atak_nail.png)
![11_rozmowa_NPC](screenshots/11_rozmowa_NPC.png)
![12_boss_intro](screenshots/12_boss_intro.png)
![13_boss_walka_1](screenshots/13_boss_walka_1.png)
![14_boss_walka_2](screenshots/14_boss_walka_2.png)
![15_boss_pokonany_serce](screenshots/15_boss_pokonany_serce.png)
![16_napisy_koncowe](screenshots/16_napisy_koncowe.png)

Gotowy ROM: `release/Pablo.gbc` (EverDrive GB: Mapper = MBC5).
