GBDK = $(CURDIR)/tools/gbdk
LCC = $(GBDK)/bin/lcc
OUT ?= build/pablo.gbc
SRCS = src/main.c src/common.c src/game.c src/scenes.c src/audio.c src/assets_gfx.c src/assets_title.c src/assets_world.c
MBC ?= 0x1B
DEFS ?=
FLAGS = -Wl-j -Wm-yt$(MBC) -Wm-yo4 -Wm-ya1 -Wm-yC -Wm-yn"PABLO" -autobank -Wb-ext=.rel -Wb-v -Wf--opt-code-size $(DEFS)

all: $(OUT)

build/assets.stamp: assets/art.py assets/world.py assets/music.py assets/build_assets.py
	mkdir -p build
	python3 assets/build_assets.py
	touch build/assets.stamp

$(OUT): build/assets.stamp $(SRCS) src/assets.h src/audio.h src/game.h src/music_data.inc
	mkdir -p build
	$(LCC) $(FLAGS) -o $(OUT) $(SRCS)

clean:
	rm -rf build/*.gbc build/*.map build/*.noi src/*.o src/*.rel src/*.lst src/*.sym src/*.asm src/*.ihx

.PHONY: all clean

variants: all
	$(MAKE) -B OUT=build/v_mbc1.gbc MBC=0x03
	$(MAKE) -B OUT=build/v_nofast.gbc DEFS=-Wf-DNOFAST
	$(LCC) -Wm-yC -Wm-yn"PABLOTEST" -o build/v_hello.gbc tests/hello/hello.c
	$(MAKE) -B
