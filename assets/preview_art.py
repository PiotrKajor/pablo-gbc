import sys
sys.path.insert(0,'.')
from art import *
from PIL import Image
T=themes()
ts=build_tileset()
print('bg tiles',len(ts.tiles))
ss=build_sprites()
print('spr tiles',len(ss.data))
def rgbpal(p): return [x for c in p for x in c]
# tileset sheet
sheet=Image.new('RGB',(16*8*3,((len(ts.tiles)+15)//16)*8*3))
for i,c in enumerate(ts.tiles):
    pal=T[1][ts.pal[i]]
    im=Image.new('RGB',(8,8))
    for y in range(8):
        for x in range(8): im.putpixel((x,y),pal[c.get(x,y)])
    im=im.resize((24,24),Image.NEAREST)
    sheet.paste(im,((i%16)*24,(i//16)*24))
sheet.save('../preview/tiles.png')
# sprites sheet
n=len(ss.frames)
cols=12
sheet=Image.new('RGB',(cols*34*2,((n+cols-1)//cols)*34*2),(30,30,40))
for i,(name,c,p) in enumerate(ss.frames):
    pal=OBJ_PALS[p]
    im=Image.new('RGB',(c.w,c.h),(30,30,40))
    for y in range(c.h):
        for x in range(c.w):
            v=c.get(x,y)
            if v: im.putpixel((x,y),pal[v])
    im=im.resize((c.w*2,c.h*2),Image.NEAREST)
    sheet.paste(im,((i%cols)*68,(i//cols)*68))
sheet=sheet.resize((sheet.width*2//1,sheet.height*2//1),Image.NEAREST)
sheet.save('../preview/sprites.png')
# title
tc=title_image()
tiles,m=tiles_from_canvas(tc)
print('title tiles',len(tiles))
pal=title_palettes()
im=Image.new('RGB',(160,144))
for y in range(144):
    for x in range(160):
        im.putpixel((x,y),pal[TITLE_ROW_PAL[y//8]][tc.get(x,y)])
im.resize((480,432),Image.NEAREST).save('../preview/title.png')
