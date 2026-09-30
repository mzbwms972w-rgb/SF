from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, math, os, sys
W,H = 1600,2000
CREAM=(233,220,198); BLACK=(18,16,14); WHITE=(246,242,232)
PINK=(232,68,122); YELLOW=(232,179,60); ORANGE=(214,106,40); RED=(206,60,46); GREEN=(74,124,66); SKY=(96,150,190)
F = lambda n,s: ImageFont.truetype("assets/fonts/"+n,s)
russo=lambda s: F("RussoOne-Regular.ttf",s)
script=lambda s: F("MarckScript-Regular.ttf",s)
narrow=lambda s: F("PT_Sans-Narrow-Web-Bold.ttf",s)
IMG="flyers/img/"

def fit(img,w,h):
    iw,ih=img.size; s=max(w/iw,h/ih)
    img=img.resize((round(iw*s),round(ih*s)),Image.LANCZOS)
    iw,ih=img.size; x=(iw-w)//2; y=(ih-h)//2
    return img.crop((x,y,x+w,y+h))

def cropf(img,f):
    iw,ih=img.size
    x0,y0,x1,y1=f
    return img.crop((int(iw*x0),int(ih*y0),int(iw*x1),int(ih*y1)))

ICONS={}
def icon(name):
    def reg(fn): ICONS[name]=fn; return fn
    return reg
@icon("burger")
def _(d,cx,cy,s,col):
    d.arc([cx-s,cy-s,cx+s,cy+s//2],180,360,fill=col,width=7)
    d.line([(cx-s,cy),(cx+s,cy)],fill=col,width=6)
    d.arc([cx-s,cy-s//2,cx+s,cy+s],0,180,fill=col,width=7)
@icon("fries")
def _(d,cx,cy,s,col):
    d.polygon([(cx-s//1.4,cy-s//3),(cx+s//1.4,cy-s//3),(cx+s//2,cy+s),(cx-s//2,cy+s)],fill=col)
    for i in range(-2,3): d.line([(cx+i*s//3,cy-s//3),(cx+i*s//4,cy-s)],fill=col,width=5)
@icon("cup")
def _(d,cx,cy,s,col):
    d.polygon([(cx-s//1.3,cy-s//2),(cx+s//1.3,cy-s//2),(cx+s//2,cy+s),(cx-s//2,cy+s)],outline=col,width=6)
    d.line([(cx+s//6,cy-s//2),(cx+s//2,cy-s)],fill=col,width=6)
@icon("clock")
def _(d,cx,cy,s,col):
    d.ellipse([cx-s,cy-s,cx+s,cy+s],outline=col,width=6)
    d.line([(cx,cy),(cx,cy-s//1.5)],fill=col,width=6); d.line([(cx,cy),(cx+s//1.6,cy+s//4)],fill=col,width=6)
@icon("target")
def _(d,cx,cy,s,col):
    for r in (s,s//1.6,s//2.6): d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=col,width=5)
    d.ellipse([cx-3,cy-3,cx+3,cy+3],fill=col)
@icon("bullet")
def _(d,cx,cy,s,col):
    d.rectangle([cx-s//3,cy-s//2,cx+s//3,cy+s],fill=col)
    d.polygon([(cx-s//3,cy-s//2),(cx,cy-s),(cx+s//3,cy-s//2)],fill=col)
@icon("shield")
def _(d,cx,cy,s,col):
    d.polygon([(cx-s,cy-s),(cx+s,cy-s),(cx+s,cy),(cx,cy+s),(cx-s,cy)],outline=col,width=6)
@icon("card")
def _(d,cx,cy,s,col):
    d.rectangle([cx-s,cy-s//1.5,cx+s,cy+s//1.5],outline=col,width=5)
    d.line([(cx-s//1.5,cy-s//4),(cx+s//4,cy-s//4)],fill=col,width=5)
    d.line([(cx-s//1.5,cy+s//3),(cx+s//2,cy+s//3)],fill=col,width=5)
@icon("drumstick")
def _(d,cx,cy,s,col):
    d.ellipse([cx-s//1.2,cy-s,cx+s//2,cy+s//3],fill=col)
    d.line([(cx+s//4,cy+s//4),(cx+s,cy+s)],fill=col,width=8)
    d.ellipse([cx+s-4,cy+s-8,cx+s+8,cy+s+4],fill=col)
@icon("wings")
def _(d,cx,cy,s,col):
    d.arc([cx-s,cy-s//2,cx,cy+s//2],180,360,fill=col,width=7)
    d.arc([cx,cy-s//2,cx+s,cy+s//2],180,360,fill=col,width=7)
@icon("box")
def _(d,cx,cy,s,col):
    d.rectangle([cx-s,cy-s//2,cx+s,cy+s],outline=col,width=6)
    d.line([(cx-s,cy-s//2),(cx-s//2,cy-s),(cx+s//2,cy-s),(cx+s,cy-s//2)],fill=col,width=6)
@icon("cabin")
def _(d,cx,cy,s,col):
    d.line([(cx,cy-s),(cx,cy-s//2)],fill=col,width=5)
    d.rectangle([cx-s//1.4,cy-s//2,cx+s//1.4,cy+s],outline=col,width=6)
    d.line([(cx-s//1.4,cy),(cx+s//1.4,cy)],fill=col,width=5)
@icon("para")
def _(d,cx,cy,s,col):
    d.arc([cx-s,cy-s,cx+s,cy+s//2],180,360,fill=col,width=7)
    for xx in (-s//1.2,0,s//1.2): d.line([(cx+xx,cy-s//2),(cx,cy+s)],fill=col,width=4)
    d.ellipse([cx-5,cy+s-5,cx+5,cy+s+5],fill=col)
@icon("mountain")
def _(d,cx,cy,s,col):
    d.polygon([(cx-s,cy+s),(cx-s//4,cy-s),(cx+s//2,cy+s)],outline=col,width=6)
    d.polygon([(cx,cy+s),(cx+s//1.6,cy-s//2),(cx+s,cy+s)],outline=col,width=6)
@icon("flag")
def _(d,cx,cy,s,col):
    d.line([(cx-s//2,cy+s),(cx-s//2,cy-s)],fill=col,width=6)
    d.polygon([(cx-s//2,cy-s),(cx+s,cy-s//2),(cx-s//2,cy)],fill=col)

def make(cfg):
    seed=cfg["seed"]; random.seed(seed)
    accent=cfg["accent"]; accent2=cfg["accent2"]
    canvas=Image.new("RGB",(W,H),CREAM)
    noise=Image.effect_noise((W,H),18).convert("L").point(lambda p:128+int((p-128)*0.35))
    canvas=Image.composite(canvas,Image.new("RGB",(W,H),(210,196,172)),noise.point(lambda p:255 if p>150 else 0).convert("L"))
    d=ImageDraw.Draw(canvas)
    for i in range(26):
        x=random.randint(0,W); y=random.randint(0,H); l=random.randint(20,90)
        d.line([(x,y),(x+l,y+random.randint(-6,6))],fill=(120,105,85),width=1)
    d.rectangle([0,0,W-1,H-1],outline=BLACK,width=18)
    d.rectangle([26,26,W-27,H-27],outline=(120,105,85),width=2)

    def panel(img,x,y,w,h,rot=0,border=12,mat=6):
        p=Image.new("RGBA",(w+2*(border+mat),h+2*(border+mat)),(0,0,0,0))
        pd=ImageDraw.Draw(p)
        pd.rectangle([0,0,p.width-1,p.height-1],fill=BLACK)
        pd.rectangle([border,border,p.width-1-border,p.height-1-border],fill=CREAM)
        p.paste(img,(border+mat,border+mat))
        p=p.rotate(rot,expand=True,resample=Image.BICUBIC)
        canvas.paste(p,(x,y),p)

    def brush(x,y,w,h,color,seed=3):
        rnd=random.Random(seed); im=Image.new("RGBA",(w,h),(0,0,0,0)); dd=ImageDraw.Draw(im)
        for i in range(int(w/18)+1):
            cx=i*18; cy=h//2+rnd.randint(-h//6,h//6); r=h//2-rnd.randint(0,h//5)
            dd.ellipse([cx-r,cy-r,cx+r,cy+r],fill=color+(255,))
        im=im.filter(ImageFilter.GaussianBlur(1.2))
        canvas.paste(im,(x,y),im)

    def text_rot(xy,s,font,fill,stroke=0,rot=0,stroke_fill=BLACK):
        ts=Image.new("RGBA",(W*2,H*2),(0,0,0,0)); td=ImageDraw.Draw(ts)
        td.text((W,H),s,font=font,fill=fill,stroke_width=stroke,stroke_fill=stroke_fill,anchor="mm")
        ts=ts.rotate(rot,expand=True,resample=Image.BICUBIC)
        bb=ts.getbbox()
        if bb: ts=ts.crop(bb)
        canvas.paste(ts,(xy[0]-ts.width//2,xy[1]-ts.height//2),ts)

    lx,ly=1230,48
    d.ellipse([lx,ly,lx+92,ly+92],fill=PINK)
    for i in range(10):
        a=math.radians(i*36); d.ellipse([lx+46+int(44*math.cos(a))-6,ly+46+int(44*math.sin(a))-6,lx+46+int(44*math.cos(a))+6,ly+46+int(44*math.sin(a))+6],fill=PINK)
    d.text((lx+46,ly+48),"E",font=russo(54),fill=WHITE,anchor="mm")
    d.text((lx+108,ly+30),"EVOLVE",font=russo(40),fill=BLACK)
    d.text((lx+110,ly+76),"ROLE PLAY",font=narrow(24),fill=(60,50,40))
    text_rot((320,110),cfg["top"],script(104),PINK,rot=-4)

    hero=Image.open(IMG+cfg["hero"]).convert("RGB")
    pan=Image.open(IMG+cfg["panel"]).convert("RGB")
    panel(fit(hero,1480,680),60,200,1480,680,rot=-1.2)
    text_rot((W//2,965),cfg["title"],russo(cfg["tsize"]),WHITE,stroke=14,rot=-2)
    brush(470,1040,660,80,accent,seed=5)
    text_rot((W//2,1080),cfg["sub"],script(72),WHITE,rot=-2)

    panel(fit(pan,760,400),60,1160,760,400,rot=1.4)
    panel(fit(cropf(hero,cfg["cropA"]),690,190),850,1160,690,190,rot=-1.6)
    panel(fit(cropf(pan,cfg["cropB"]),690,190),850,1370,690,190,rot=1.2)

    ix,iy,iw,ih=60,1590,760,240
    d.rectangle([ix,iy,ix+iw,iy+ih],fill=BLACK)
    d.rectangle([ix+8,iy+8,ix+iw-8,iy+ih-8],outline=accent,width=3)
    for i,(txt,icn) in enumerate(cfg["items"]):
        yy=iy+42+i*56
        ICONS[icn](d,ix+66,yy,19,accent2 if i%2 else accent)
        d.text((ix+112,yy),txt,font=narrow(32),fill=WHITE,anchor="lm")

    sx,sy,sw,sh=850,1590,690,240
    d.rectangle([sx,sy,sx+sw,sy+sh],fill=BLACK)
    text_rot((sx+sw//2,sy+90),cfg["slo1"],script(64),accent,rot=-2)
    text_rot((sx+sw//2,sy+162),cfg["slo2"],script(64),accent,rot=-2)

    gy=1860
    d.rectangle([26,gy,W-27,H-27],fill=BLACK)
    d.ellipse([70,gy+26,108,gy+64],fill=accent); d.polygon([(89,gy+88),(74,gy+58),(104,gy+58)],fill=accent)
    d.text((136,gy+45),cfg["geo"],font=narrow(38),fill=WHITE,anchor="lm")
    text_rot((1210,gy+45),cfg["cta"],script(52),accent,rot=-2)

    canvas.save("flyers/"+cfg["out"])
    print("saved",cfg["out"])

CONFIGS=[
 dict(seed=11,accent=PINK,accent2=YELLOW,out="burger-shot-los-santos.png",hero="burger_ext.png",panel="burger_food.png",
   cropA=(0.30,0.02,0.90,0.45),cropB=(0.15,0.30,0.85,0.95),top="Los Santos",title="BURGER SHOT",tsize=170,
   sub="Los Santos · закусочная",
   items=[("СОЧНЫЕ БУРГЕРЫ С ОГОНЬКА","burger"),("ХРУСТЯЩАЯ КАРТОШКА ФРИ","fries"),("ПРОХЛАДНЫЕ НАПИТКИ И ШЕЙКИ","cup"),("ОТКРЫТО КРУГЛЫЕ СУТКИ","clock")],
   slo1="«Один укус —",slo2="и ты дома!»",geo="ЖДЁМ ВАС В BURGER SHOT!",cta="Заезжай на бургер!"),
 dict(seed=22,accent=ORANGE,accent2=YELLOW,out="ammu-nation-los-santos.png",hero="ammu_ext.png",panel="ammu_int.png",
   cropA=(0.25,0.05,0.85,0.50),cropB=(0.10,0.35,0.80,0.95),top="Los Santos",title="AMMU-NATION",tsize=150,
   sub="Los Santos · оружейный",
   items=[("ОРУЖИЕ И СНАРЯЖЕНИЕ","target"),("БОЕПРИПАСЫ И АКСЕССУАРЫ","bullet"),("ПОМОЩЬ С ЛИЦЕНЗИЕЙ","shield"),("СПОРТ И ОХОТА","card")],
   slo1="«Всё для спокойствия —",slo2="и ничего лишнего!»",geo="AMMU-NATION ЖДЁТ ВАС!",cta="Всё строго по лицензии!"),
 dict(seed=33,accent=RED,accent2=YELLOW,out="cluckin-bell-san-fierro.png",hero="cluck_ext.png",panel="cluck_ext.png",
   cropA=(0.35,0.00,0.95,0.45),cropB=(0.05,0.40,0.70,1.0),top="San Fierro",title="CLUCKIN' BELL",tsize=150,
   sub="San Fierro · закусочная",
   items=[("КУРИНЫЕ БУРГЕРЫ С ОГНЯ","drumstick"),("КРЫЛЬЯ ПО СЕКРЕТНОМУ РЕЦЕПТУ","wings"),("СЕМЕЙНЫЕ НАБОРЫ","box"),("ДЕТСКОЕ МЕНЮ И ШЕЙКИ","cup")],
   slo1="«Курочка, к которой",slo2="возвращаются!»",geo="ЖДЁМ ВАС В CLUCKIN' BELL!",cta="Приходи голодным!"),
 dict(seed=44,accent=GREEN,accent2=SKY,out="mount-chiliad-tour.png",hero="chiliad_top.png",panel="chiliad_para.png",
   cropA=(0.20,0.10,0.85,0.55),cropB=(0.10,0.25,0.85,0.90),top="San Andreas",title="MOUNT CHILIAD",tsize=160,
   sub="San Andreas · экскурсия",
   items=[("КАНАТНАЯ ДОРОГА НА ВЕРШИНУ","cabin"),("ПАРАПЛАН И ВЕЛОСПУСК","para"),("ВИД НА ВЕСЬ ШТАТ","mountain"),("МАРШРУТЫ С ПРОВОДНИКОМ","flag")],
   slo1="«Выше всех",slo2="твоих проблем!»",geo="ВСТРЕЧА У ПОДНОЖИЯ CHILIAD!",cta="Подъём начинается здесь!"),
]
for c in CONFIGS: make(c)
