# Jak zagrać w PABLO w emulatorze

ROM: [`release/Pablo.gbc`](../release/Pablo.gbc). Gra jest **tylko na Game Boy Color**, więc emulator musi
działać w trybie CGB (kolory). Wszystkie poniższe emulatory robią to automatycznie.

## mGBA (Windows / Linux / macOS)

1. Pobierz mGBA z <https://mgba.io/downloads.html> (Linux: `sudo dnf install mgba-qt` albo Flatpak `io.mgba.mGBA`).
2. **File → Load ROM…** i wskaż `Pablo.gbc` (można też przeciągnąć plik na okno).
3. Domyślne klawisze:

   | Game Boy | Klawiatura |
   |---|---|
   | D-pad | strzałki |
   | A (skok, dash w powietrzu) | `X` |
   | B (atak) | `Z` |
   | START | `Enter` |
   | SELECT (drugi dash) | `Backspace` |

   Zmiana: **Tools → Settings → Controls (Keyboard)**. Pada podłączonego przez USB mGBA wykryje sam.
4. **Zapis:** ławki zapisują grę do `Pablo.sav` obok ROM-u. Do tego mGBA ma zapis stanu:
   `Shift+F1` zapisuje stan w slocie 1, `F1` go wczytuje (menu **File → Save state / Load state**).
5. Wygładzanie pikseli i skala: **Tools → Settings → Interface/Video** (zalecane: integer scaling, bez filtra).
   Szybkie przewijanie na czas testów: przytrzymaj `Tab`.
6. Jeśli ekran jest czarno-biały: **Tools → Settings → Emulation → Game Boy model: Game Boy Color** (dla CGB).

## W przeglądarce (bez instalacji)

Gra nie jest hostowana online, ROM zostaje na twoim komputerze: emulator wczytuje plik lokalnie.

- **binjgb** – <https://binji.github.io/binjgb/> (obsługuje GBC). Kliknij **Select ROM** i wybierz `Pablo.gbc`.
  Klawisze: strzałki, `Z` = B, `X` = A, `Enter` = Start, `Tab` = Select. Zapis (baterii) trzyma w pamięci przeglądarki.
- **EmulatorJS** – demo na <https://demo.emulatorjs.org/>: wybierz system *Game Boy Color* i wgraj ROM.
  Klawisze i zapisy ustawisz w menu emulatora.

> Przeglądarkowe emulatory zapisują stan w pamięci przeglądarki (localStorage/IndexedDB), więc wyczyszczenie danych
> witryny skasuje zapis gry. Przed czyszczeniem wyeksportuj `.sav` lub użyj mGBA.

## Najczęstsze kłopoty

| Objaw | Rozwiązanie |
|---|---|
| Biały/pusty ekran w emulatorze | wybierz tryb **Game Boy Color** albo inny emulator (mGBA) |
| Brak dźwięku w przeglądarce | kliknij okno gry, przeglądarki wymagają kliknięcia przed odtwarzaniem |
| Gra za wolna | włącz akcelerację/odpowiedni tryb CGB w opcjach, lub skorzystaj z mGBA |
| Biały ekran na EverDrive GB | ustaw **Mapper = MBC5** w opcjach ROM |
