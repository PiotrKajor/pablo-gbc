<div align="center">

<img src="screenshots/01_tytul.png" width="480" alt="PABLO – A Hollow Tale">

# PABLO – A Hollow Tale

**Fanowska metroidvania w klimacie *Hollow Knight* na Game Boy Color**

![platforma](https://img.shields.io/badge/platforma-Game%20Boy%20Color-6a9955)
![język](https://img.shields.io/badge/C-GBDK--2020-blue)
![ROM](https://img.shields.io/badge/ROM-64%20KB%20MBC5-lightgrey)
![klatki](https://img.shields.io/badge/60%20FPS-CGB%20double%20speed-success)

</div>

Mały naczynie bez imienia budzi się pod mchem Verdant Deep. Lampy gasną, bo Strażnik połknął Heartlight.
Weź swój nail, zdobądź Mothwing Cloak, przeskocz Przepaść i pokonaj Strażnika.

**7 pokoi · 1 boss · dash · leczenie (focus) · ławki z zapisem na baterii · 4 utwory muzyczne · napisy końcowe.**
Cała grafika, muzyka i dialogi są generowane proceduralnie skryptami w Pythonie.

## Pobierz i graj

Gotowy ROM: [`release/Pablo.gbc`](release/Pablo.gbc) (tylko Game Boy Color).

- **Emulator** (mGBA, SameBoy, BGB) lub **przeglądarka**: krótki poradnik w [`docs/EMULATORY.md`](docs/EMULATORY.md).
- **EverDrive GB:** skopiuj na kartę, w opcjach ROM ustaw **Mapper = MBC5**, RAM 8K, Save RAM = YES.
  Przy mapperze „ROM” ekran zostaje biały po logo.

## Sterowanie

| Przycisk | Akcja |
|---|---|
| ←/→ | ruch |
| **A** | skok (przytrzymaj = wyżej) |
| **B** | uderzenie nailem |
| **A** w powietrzu lub **SELECT** | dash (po zdobyciu Mothwing Cloak) |
| **START** (przytrzymaj) | focus – leczy maskę kosztem duszy |
| **↑** | rozmowa / odpoczynek i zapis na ławce |
| **↓** | zeskok z cienkiej platformy |

## Gameplay

| Start gry | Ruch i atak |
|:-:|:-:|
| ![start](docs/gifs/01_start.gif) | ![ruch](docs/gifs/02_ruch_i_atak.gif) |

| Dash (A w powietrzu) przez Przepaść |
|:-:|
| ![dash](docs/gifs/03_dash_przez_przepasc.gif) |

## Zrzuty ekranu

| | | |
|:-:|:-:|:-:|
| ![](screenshots/02_intro_dialog.png) | ![](screenshots/03_pokoj_Moss_Hollow.png) | ![](screenshots/04_pokoj_Green_Path.png) |
| Intro | Moss Hollow | Green Path |
| ![](screenshots/05_pokoj_Luma_Cavern.png) | ![](screenshots/06_pokoj_The_Gap.png) | ![](screenshots/07_pokoj_Archive_Cellar.png) |
| Luma Cavern | The Gap | Archive Cellar |
| ![](screenshots/08_pokoj_Stone_Door.png) | ![](screenshots/09_dash.png) | ![](screenshots/10_atak_nail.png) |
| Stone Door | Dash | Atak nailem |
| ![](screenshots/11_rozmowa_NPC.png) | ![](screenshots/12_boss_intro.png) | ![](screenshots/13_boss_walka_1.png) |
| Rozmowa | Boss – wstęp | Walka ze Strażnikiem |
| ![](screenshots/14_boss_walka_2.png) | ![](screenshots/15_boss_pokonany_serce.png) | ![](screenshots/16_napisy_koncowe.png) |
| Walka, faza 2 | Heartlight odzyskany | Napisy końcowe |

## Budowanie

Wymagane: [GBDK-2020](https://github.com/gbdk-2020/gbdk-2020) w `tools/gbdk`, Python 3 z Pillow i PyBoy w `.venv`.

```sh
make                       # generuje assety i buduje build/pablo.gbc
.venv/bin/python tests/t_full.py   # pełne przejście gry (headless PyBoy)
```

## Struktura

```
assets/   art.py (grafika), world.py (pokoje DSL, dialogi), music.py, build_assets.py
src/      common.c (bank 0), game.c, scenes.c, audio.c, main.c
tests/    PyBoy: pełne przejście, boss, śmierć/CONTINUE, zakończenie, lag, symulator fizyki (sim.py)
release/  gotowy ROM
```

Szczegóły techniczne: CGB-only, MBC5+RAM+BATT, 8×16 sprite'y, `cpu_fast()` dla 60 FPS, zapis w SRAM z sumą kontrolną.

## Uwaga

Projekt fanowski i niekomercyjny, niezwiązany z Team Cherry. *Hollow Knight* należy do swoich właścicieli.
