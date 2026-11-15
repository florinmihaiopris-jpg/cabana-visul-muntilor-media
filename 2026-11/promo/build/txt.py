import sys
from PIL import Image,ImageDraw,ImageFont
X="/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"; B="/usr/share/fonts/opentype/inter/Inter-Bold.otf"
def caption(path,lines,y=1500):
    im=Image.new("RGBA",(1080,1920),(0,0,0,0));d=ImageDraw.Draw(im)
    for t,s,c in lines:
        f=ImageFont.truetype(X if s<60 else B,s); w=d.textlength(t,font=f)
        d.text(((1080-w)/2,y),t,font=f,fill=c,stroke_width=3,stroke_fill=(0,0,0,170)); y+=int(s*1.35)
    im.save(path)
def tag(path,t):
    im=Image.new("RGBA",(1080,1920),(0,0,0,0));d=ImageDraw.Draw(im);f=ImageFont.truetype(B,34)
    w=d.textlength(t,font=f);d.rounded_rectangle((540-w/2-24,140,540+w/2+24,200),radius=12,fill=(247,183,49,235));d.text((540-w/2,148),t,font=f,fill=(20,20,20));im.save(path)
W=(255,255,255);Y=(247,215,140)
caption("c_noapte.png",[("Noaptea, din plasa de deasupra șemineului",44,W)],1560)
caption("c_cascada.png",[("Cascada Vălul Miresei",58,W),("în apropiere",40,Y)],1480)
caption("c_pietre.png",[("Pietrele Albe",64,W),("în apropiere",40,Y)],1480)
caption("c_end.png",[("Cabana Visul Munților",72,W),("Beliș · Munții Apuseni",44,Y),("Cabană întreagă pentru 14 persoane",42,W),("Scrie-ne pe WhatsApp",48,Y)],1180)
for n,t in [("t1","GAZDA AI: la șemineu"),("t2","GAZDA AI: urcă pe plasă, se uită în sus"),("t3","GAZDA AI: se trezește pe plasă"),("t4","GAZDA AI: uimită la cascadă"),("t5","GAZDA AI: la Pietrele Albe"),("t6","GAZDA AI: se întoarce la cabană")]: tag(n+".png",t)
