#!/usr/bin/env python3
"""
stock_reel.py — авто-агент: тема -> 9:16 Reels из бесплатного стока (Pexels).
Живое видео + верхний заголовок-хук + авто-субтитры (Montserrat, средний размер,
синхрон по речи) + мягкая фоновая музыка. Версии KZ+RU, РАЗНЫЕ кадры.
Бренд-слова произносятся по-местному (PHON), написание не меняется.
env: PEXELS_KEY. Бесплатно. Кредит Pexels — в описании поста.
"""
import urllib.request, urllib.parse, json, os, subprocess, random, time

_HERE=os.path.dirname(os.path.abspath(__file__))
FONT=os.environ.get("FONT") or os.path.join(_HERE,"assets","Montserrat.ttf")  # вложен в репо: без сети
# запасные системные шрифты, если вложенного нет и скачать не вышло
FONT_FALLBACKS=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc"]
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
KEY=os.environ.get("PEXELS_KEY","")  # ленивая проверка: нужен при вызове api(), не при импорте
W,H=1080,1920
WORK=os.environ.get("WORK","/tmp/stock_reel_v4"); os.makedirs(WORK,exist_ok=True)
MUSIC=os.environ.get("MUSIC","")  # свой mp3; если пусто — берём bundled reel_music.mp3 рядом; иначе генерим
if not MUSIC:
    _b=os.path.join(os.path.dirname(os.path.abspath(__file__)),"reel_music.mp3")
    if os.path.exists(_b): MUSIC=_b

# Произношение брендов: только для ОЗВУЧКИ, написание на экране не трогаем.
# Бренд НИКОГДА не читается по-английски ("eye-book"). В каждом языке своя запись,
# подобранная так, чтобы местный синтезатор произнёс "АЙ-БУК".
_BRAND_SOUND={
 "kk":"Айбук","ru":"Айбук","uk":"Айбук",   # кириллица читается напрямую
 "zh":"爱布克",                              # ài bù kè, по канону кит. брендов (爱奇艺)
 "de":"Aibuk","it":"Aibuk","es":"Áibuk",   # ai=[ai], u=[u]; исп. ударение иначе съедет на конец
 "tr":"Aybuk","uz":"Aybuk",                # тюркская латиница фонетична
 "fr":"Aïbouk",                            # трема рвёт франц. ai=[ɛ], ou=[u]
}
# казахские бренды пользователя — точное қазақша написание в KZ и RU роликах
_KZ_BRANDS={"Telegram":"Телеграм","Qujat":"Құжат","Qyran":"Қыран","Qalqan":"Қалқан",
            "Sabaq":"Сабақ","Galamtor":"Ғаламтор","Jel":"Жел"}
PHON={l:{**(_KZ_BRANDS if l in ("kk","ru") else {}),"Ibook":b,"ibook":b}
      for l,b in _BRAND_SOUND.items()}
def phon(t,lang):
    for a,b in PHON.get(lang,{}).items(): t=t.replace(a,b)
    return t

# несколько голосов на язык — агент чередует их (разнообразие между постами).
# можно зафиксировать через env VOICE_KK / VOICE_RU.
# несколько БЕСПЛАТНЫХ платформ+голосов на язык -> чередуются для разнообразия.
# формат (engine, id). engine: edge | gtts | mms. env override: VOICE_KK="mms:facebook/mms-tts-kaz"
VOICES={
 # ПЛАТНО (ElevenLabs) — только там, где качество критично и слышно владельцу:
 # клоны его собственного голоса, живой казах БЕЗ акцента. Laura + Bala чередуются.
 "kk":[("eleven","xKWShjEXraJurmIX5TZM"),("eleven","M4jzBCMPD6005WAnM0H9")],
 "ru":[("eleven","xKWShjEXraJurmIX5TZM"),("eleven","M4jzBCMPD6005WAnM0H9")],
 # БЕСПЛАТНО (Edge neural) — остальные языки. Носителю звучит естественно,
 # платить за них ElevenLabs смысла нет. Две озвучки на язык: М+Ж, чередуются.
 "zh":[("edge","zh-CN-XiaoxiaoNeural"),("edge","zh-CN-YunxiNeural")],
 "de":[("edge","de-DE-SeraphinaMultilingualNeural"),("edge","de-DE-ConradNeural")],
 "it":[("edge","it-IT-ElsaNeural"),("edge","it-IT-DiegoNeural")],
 "tr":[("edge","tr-TR-EmelNeural"),("edge","tr-TR-AhmetNeural")],
 "uk":[("edge","uk-UA-PolinaNeural"),("edge","uk-UA-OstapNeural")],
 "es":[("edge","es-ES-ElviraNeural"),("edge","es-ES-AlvaroNeural")],
 "fr":[("edge","fr-FR-DeniseNeural"),("edge","fr-FR-RemyMultilingualNeural")],
 "uz":[("edge","uz-UZ-MadinaNeural"),("edge","uz-UZ-SardorNeural")],
}
LANG_CODE={"kk":"KZ","ru":"RU","zh":"ZH","de":"DE","it":"IT",
           "tr":"TR","uk":"UK","es":"ES","fr":"FR","uz":"UZ"}
LANG_NAME={"kk":"Қазақша","ru":"Русский","zh":"中文","de":"Deutsch","it":"Italiano",
           "tr":"Türkçe","uk":"Українська","es":"Español","fr":"Français","uz":"O‘zbekcha"}
# ПРОЕКТЫ пользователя. Выбор через env PROJECT (по умолч. qujat). Кадры — строго по теме!
PROJECT=os.environ.get("PROJECT","qujat")
# У КАЖДОГО ЯЗЫКА СВОИ ЗАПРОСЫ К СТОКУ — это не избыточность:
#  1) одинаковые кадры соцсети метят как дубликат и режут охват;
#  2) типаж людей должен совпадать с аудиторией языка.
# Бренд в тексте пишем "ibook", озвучку правит PHON (см. выше).
PROJECTS={
 # Qujat — бухгалтерия/налоги. Кадры: документы, налоги, калькулятор, таблицы. НЕ трейдинг-графики!
 "qujat":{"kk":dict(title="САЛЫҚ ЕНДІ ОҢАЙ",scenes=[
   dict(t="Бухгалтерия басыңды ауыртып жүр ме?",q="financial documents paperwork office desk"),
   dict(t="Құжат салық пен есептерді өзі санайды.",q="calculator counting money banknotes finance"),
   dict(t="Есеп-қисап бір минутта дайын болады.",q="accountant signing invoice documents pen desk"),
   dict(t="Телеграмдағы бот та, сайт та дайын.",q="accounting spreadsheet table laptop screen office"),
   dict(t="Қазір тегін бастап көріңіз, Құжатқа жазыңыз!",q="asian business people meeting handshake office"),
  ]),
  "ru":dict(title="НАЛОГИ ЭТО ЛЕГКО",scenes=[
   dict(t="Бухгалтерия отнимает всё твоё время?",q="tired accountant paperwork desk evening"),
   dict(t="Құжат сам считает налоги и отчёты.",q="calculator invoice documents office table"),
   dict(t="Отчёт готов всего за одну минуту.",q="businesswoman signing documents office desk"),
   dict(t="В Телеграме есть и бот, и сайт.",q="person using laptop spreadsheet work"),
   dict(t="Начните бесплатно, напишите в Құжат!",q="business people handshake meeting office"),
  ])},
 # ibook — booking-маркетплейс: бронь услуг и мест. Кадры: телефон, салон, отель, оплата.
 "ibook":{
  "kk":dict(title="БРОНЬДІ ОҢАЙ ЖАСА",scenes=[
   dict(t="Брондау деген қиынға соғып жүр ме?",q="hands using smartphone booking travel app"),
   dict(t="ibook, бәрін бір қосымшада брондайсың.",q="modern hotel room interior travel"),
   dict(t="Қонақүй, қызмет, орынды бірнеше түртумен таңдайсың.",q="asian woman booking appointment smartphone online"),
   dict(t="Онлайн төле, растауды бірден ал.",q="online payment smartphone mobile checkout"),
   dict(t="Қазір ibookты жүктеп алыңыз!",q="asian traveler happy using phone city street"),
  ]),
  "ru":dict(title="БРОНИРУЙ ЛЕГКО",scenes=[
   dict(t="Бронировать долго и неудобно?",q="person frustrated waiting phone call"),
   dict(t="ibook, бронируй всё в одном приложении.",q="woman using booking app smartphone home"),
   dict(t="Отель, услугу, место, в пару касаний.",q="beauty salon manicure client hands"),
   dict(t="Оплати онлайн, получи подтверждение сразу.",q="contactless payment smartphone terminal"),
   dict(t="Скачайте ibook прямо сейчас!",q="happy woman smiling walking city street"),
  ]),
  "zh":dict(title="预约就该这么轻松",scenes=[
   dict(t="还在打电话预约，等半天没回复？",q="asian woman frustrated phone call"),
   dict(t="ibook，所有预约一个应用搞定。",q="asian woman using smartphone app"),
   dict(t="酒店、美容、按摩，动动手指就搞定。",q="asian woman beauty salon appointment"),
   dict(t="线上付款，马上收到确认通知。",q="asian woman mobile payment smartphone"),
   dict(t="现在就下载ibook，约起来！",q="happy asian woman smiling smartphone"),
  ]),
  "de":dict(title="EINFACH BUCHEN",scenes=[
   dict(t="Buchen dauert ewig und nervt dich jedes Mal?",q="frustrated woman waiting phone cafe"),
   dict(t="Mit ibook buchst du alles in einer App.",q="young woman using smartphone city"),
   dict(t="Hotel, Termin oder Salon, mit wenigen Klicks gebucht.",q="hair salon stylist happy client"),
   dict(t="Bezahl online, deine Bestätigung kommt sofort.",q="online payment smartphone card hands"),
   dict(t="Hol dir ibook jetzt in deinem App Store.",q="smiling woman smartphone european street"),
  ]),
  "it":dict(title="PRENOTA FACILE",scenes=[
   dict(t="Prenotare ti sembra sempre una perdita di tempo?",q="woman annoyed waiting phone call"),
   dict(t="Con ibook prenoti tutto in un'unica app.",q="woman using booking app smartphone"),
   dict(t="Hotel, parrucchiere o ristorante, bastano pochi tocchi.",q="boutique hotel reception check in"),
   dict(t="Paghi online e ricevi subito la conferma.",q="online payment credit card smartphone"),
   dict(t="Scarica ibook adesso, la prima prenotazione ti aspetta.",q="happy young woman smiling smartphone city"),
  ]),
  "tr":dict(title="KOLAY REZERVASYON",scenes=[
   dict(t="Rezervasyon yapmak neden bu kadar zor?",q="young turkish woman frustrated with phone"),
   dict(t="ibook ile her şeyi tek uygulamadan ayırt.",q="turkish woman using smartphone app cafe"),
   dict(t="Otel, salon, randevu, birkaç dokunuşla hazır.",q="istanbul boutique hotel reception guest checkin"),
   dict(t="Online öde, onayını saniyeler içinde al.",q="woman paying online with phone shop"),
   dict(t="ibook'u hemen indir, sıra sende!",q="happy turkish woman smiling holding phone"),
  ]),
  "uk":dict(title="БРОНЮЙ ЛЕГКО",scenes=[
   dict(t="Набридло дзвонити, чекати й бронювати годинами?",q="young woman annoyed waiting phone call"),
   dict(t="ibook, бронюй усе в одному застосунку.",q="woman using booking app smartphone home"),
   dict(t="Готель, послуга, місце, усе за кілька дотиків.",q="modern hair salon interior hotel reception"),
   dict(t="Оплати онлайн і одразу отримай підтвердження.",q="woman paying online card smartphone cafe"),
   dict(t="Завантажуй ibook вже зараз і бронюй легко!",q="happy european woman smiling holding smartphone"),
  ]),
  "es":dict(title="RESERVA FÁCIL",scenes=[
   dict(t="¿Sigues perdiendo el tiempo llamando para reservar una cita?",q="stressed woman phone call home"),
   dict(t="Con ibook lo reservas todo desde una sola app.",q="young european woman smartphone app"),
   dict(t="Hotel, peluquería o spa, todo en un par de toques.",q="hair salon appointment client mediterranean"),
   dict(t="Paga online y recibe tu confirmación al instante.",q="woman online payment card phone"),
   dict(t="Descarga ibook ahora y reserva sin complicarte la vida.",q="happy woman smiling smartphone city"),
  ]),
  "fr":dict(title="RÉSERVE FACILEMENT",scenes=[
   dict(t="Tu galères encore à réserver un rendez-vous ?",q="frustrated woman waiting phone call"),
   dict(t="Avec ibook, tu réserves tout dans une seule appli.",q="young woman using smartphone app"),
   dict(t="Un hôtel, un salon, une table, en deux clics.",q="hair salon client hotel reception"),
   dict(t="Paie en ligne, ta confirmation arrive tout de suite.",q="woman paying online with phone"),
   dict(t="Télécharge ibook maintenant, ta prochaine réservation t'attend.",q="happy woman smiling phone street"),
  ]),
  "uz":dict(title="OSON BAND QIL",scenes=[
   dict(t="Band qilish uchun yana qo‘ng‘iroq qilyapsanmi?",q="asian woman frustrated phone call"),
   dict(t="ibook, hammasini bitta ilovada band qil.",q="asian woman using smartphone app"),
   dict(t="Mehmonxona, salon, xizmat, bir necha bosishda tayyor.",q="asian woman hotel reception checkin"),
   dict(t="Onlayn to‘lov qil, tasdiqni darhol ol.",q="asian customer paying phone contactless"),
   dict(t="ibookni hoziroq telefoningga yuklab ol!",q="happy asian woman smiling smartphone"),
  ]),
 },
}
P=PROJECTS[PROJECT]
OUTDIR=os.environ.get("OUT_DIR",os.path.expanduser("~/Downloads"))
os.makedirs(OUTDIR,exist_ok=True)
LANGS={l:dict(rate="-4%" if l=="kk" else "+0%", title=P[l]["title"], scenes=P[l]["scenes"],
              out=f"{OUTDIR}/{PROJECT}-STOCK-{LANG_CODE[l]}.mp4")
       for l in LANG_CODE if l in P}
# LANGS_ONLY="kk" или список "kk,ru,de" — иначе рендерим все языки проекта
_only=[x.strip() for x in os.environ.get("LANGS_ONLY","").split(",") if x.strip()]
if _only: LANGS={l:LANGS[l] for l in _only if l in LANGS}

def api(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"Authorization":KEY,"User-Agent":UA}),timeout=20))
def find_clip(q,used):
    for orient in ("portrait","landscape"):
        d=api(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=15&orientation={orient}")
        for v in d.get("videos",[]):
            if v["id"] in used: continue
            fs=[f for f in v["video_files"] if f.get("height")]
            # берём САМЫЙ ЛЁГКИЙ файл, которого хватает на выход 1080x1920:
            # тянуть UHD 2560x1440 бессмысленно — это втрое больше байт при том же результате
            ok=[f for f in fs if (f["height"] or 0)>=1080]
            cand=sorted(ok,key=lambda f:f["height"]) or sorted(fs,key=lambda f:-(f["height"] or 0))
            if cand: used.add(v["id"]); return v["id"],cand[0]["link"]
    return None,None
def download(u,p,tries=3):
    """Качаем во временный файл с ретраями. Pexels регулярно рвёт соединение на середине
    (IncompleteRead) — без этого одна оборванная загрузка роняла весь ролик."""
    last=None
    for a in range(tries):
        try:
            req=urllib.request.Request(u,headers={"User-Agent":UA})
            with urllib.request.urlopen(req,timeout=120) as r: data=r.read()
            if len(data)<10000: raise RuntimeError(f"подозрительно мало данных: {len(data)} б")
            tmp=p+".part"
            with open(tmp,"wb") as f: f.write(data)
            os.replace(tmp,p)          # частичный файл никогда не станет "готовым" клипом
            return True
        except Exception as e:
            last=e; print(f"   ! попытка {a+1}/{tries}: {e}",flush=True); time.sleep(2*(a+1))
    print(f"   ! сцена пропущена: {last}",flush=True)
    return False
def dur(p):
    r=subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","json",p],capture_output=True,text=True)
    try: return float(json.loads(r.stdout)["format"]["duration"])
    except: return 0.0
def ff(args):
    r=subprocess.run(["ffmpeg","-y",*args],capture_output=True,text=True)
    if r.returncode: raise RuntimeError(r.stderr[-1500:])

def make_music(total,path):
    """Мягкий тёплый эмбиент-бэд (аккорд C, приглушённый + реверб). Бесплатно, без копирайта."""
    notes=[130.81,196.00,261.63,329.63]  # C3 G3 C4 E4
    ins=[];
    for n in notes: ins+=["-f","lavfi","-i",f"sine=frequency={n}:duration={total:.2f}"]
    fc=("".join(f"[{i}]" for i in range(len(notes)))+
        f"amix=inputs={len(notes)}:normalize=1,"
        "tremolo=f=0.12:d=0.35,lowpass=f=520,highpass=f=90,"
        "aecho=0.8:0.9:70|130:0.4|0.25,"
        f"afade=t=in:st=0:d=1.5,afade=t=out:st={max(0,total-1.5):.2f}:d=1.5[a]")
    ff([*ins,"-filter_complex",fc,"-map","[a]","-t",f"{total:.2f}",path])

def main():
    from PIL import Image, ImageDraw, ImageFont
    import asyncio
    async def edge_synth(text,voice,rate,mp3):
        import edge_tts  # ленивый импорт: нужен только для движка edge
        c=edge_tts.Communicate(text,voice,rate=rate); s=[None,None]
        with open(mp3,"wb") as f:
            async for ch in c.stream():
                if ch["type"]=="audio": f.write(ch["data"])
                elif ch["type"] in ("SentenceBoundary","WordBoundary"):
                    a=ch["offset"]/1e7; b=(ch["offset"]+ch["duration"])/1e7
                    if s[0] is None: s[0]=a
                    s[1]=b
        return s
    _mms={}
    def gen_voice(engine,vid,text,rate,mp3):
        if engine=="edge":
            return asyncio.run(edge_synth(text,vid,rate,mp3))
        if engine=="gtts":
            subprocess.run(["uvx","--from","gtts","gtts-cli",text,"-l",vid,"-o",mp3],
                           check=True,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
            return [None,None]
        if engine=="mms":
            import torch, numpy as np, wave as _w
            from transformers import VitsModel, AutoTokenizer
            if vid not in _mms:
                _mms[vid]=(VitsModel.from_pretrained(vid),AutoTokenizer.from_pretrained(vid))
            m,tk=_mms[vid]; inp=tk(text,return_tensors="pt")
            with torch.no_grad(): w=m(**inp).waveform[0].numpy()
            sr=m.config.sampling_rate; pcm=(np.clip(w,-1,1)*32767).astype(np.int16)
            wv=mp3+".wav"
            with _w.open(wv,"wb") as f:
                f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr); f.writeframes(pcm.tobytes())
            ff(["-i",wv,"-q:a","4",mp3])
            return [None,None]
        if engine=="eleven":  # ElevenLabs (человеческий голос, вкл. казахский) — нужен env EL_KEY
            key=os.environ["EL_KEY"]
            model=os.environ.get("EL_MODEL","eleven_v3")
            body=json.dumps({"text":text,"model_id":model,
                "voice_settings":{"stability":0.5,"similarity_boost":0.8,"speed":1.0}}).encode()
            req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
                data=body,headers={"xi-api-key":key,"Content-Type":"application/json","Accept":"audio/mpeg"})
            with urllib.request.urlopen(req,timeout=90) as r, open(mp3,"wb") as f: f.write(r.read())
            return [None,None]
        return [None,None]
    def _download_font():
        """Качаем во временный файл и переименовываем только целое — иначе пустышка
        навсегда отравляет кэш (os.path.exists() потом считает шрифт готовым)."""
        try:
            url="https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf"
            req=urllib.request.Request(url,headers={"User-Agent":UA})
            with urllib.request.urlopen(req,timeout=60) as r: data=r.read()
            if len(data)<50000: return False           # HTML-ошибка вместо шрифта
            os.makedirs(os.path.dirname(FONT) or ".",exist_ok=True)
            tmp=FONT+".part"
            with open(tmp,"wb") as f: f.write(data)
            os.replace(tmp,FONT)
            return True
        except Exception: return False
    def _font_path():
        if os.path.exists(FONT) and os.path.getsize(FONT)>50000: return FONT
        if _download_font(): return FONT
        for p in FONT_FALLBACKS:
            if os.path.exists(p): return p
        raise RuntimeError("нет ни одного пригодного шрифта: "+FONT)
    def font(sz):
        f=ImageFont.truetype(_font_path(),sz)
        try: f.set_variation_by_axes([700])
        except Exception: pass
        return f
    FS=font(56); TF=font(46)
    def wrap(d,text,f,mw):
        out=[]; cur=""
        for w in text.split():
            t=(cur+" "+w).strip()
            if d.textlength(t,font=f)<=mw: cur=t
            else: out.append(cur); cur=w
        if cur: out.append(cur)
        return out
    def sub_png(text,path):
        img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
        lines=wrap(d,text.upper(),FS,880); lh=72; y0=1280-lh*len(lines)//2
        for i,ln in enumerate(lines):
            w=d.textlength(ln,font=FS); d.text(((W-w)//2,y0+i*lh),ln,font=FS,
                fill=(255,255,255,255),stroke_width=7,stroke_fill=(0,0,0,255))
        img.save(path)
    def title_png(text,path):
        img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
        tw=d.textlength(text,font=TF); pad=42; y0=150; hh=104
        d.rounded_rectangle([(W-tw)//2-pad,y0,(W+tw)//2+pad,y0+hh],radius=52,fill=(88,16,232,235))
        d.text(((W-tw)//2,y0+26),text,font=TF,fill=(255,255,255,255))
        img.save(path)
    def phrases(text,st,en,maxw=3):
        ws=text.split(); ch=[" ".join(ws[i:i+maxw]) for i in range(0,len(ws),maxw)]
        L=[max(1,len(c)) for c in ch]; tot=sum(L); out=[]; t=st; span=max(0.3,en-st)
        for c,l in zip(ch,L): dt=span*l/tot; out.append((c,t,t+dt)); t+=dt
        return out

    used=set()
    for lang,cfg in LANGS.items():
        ov=os.environ.get(f"VOICE_{lang.upper()}")
        if ov and ":" in ov: engine,vid=ov.split(":",1)
        else: engine,vid=random.choice(VOICES[lang])
        print(f"=== {lang}: движок {engine} голос {vid} ===",flush=True)
        clips=[]; D=[]; spans=[]; voices=[]
        for i,s in enumerate(cfg["scenes"]):
            print(f"[{lang} {i}] '{s['q']}'",flush=True)
            cid,link=find_clip(s["q"],used)
            if not link: print("   ! нет клипа"); continue
            cp=f"{WORK}/{lang}_c{i}.mp4"
            if not download(link,cp): continue
            mp3=f"{WORK}/{lang}_l{i}.mp3"
            sp=gen_voice(engine,vid,phon(s["t"],lang),cfg["rate"],mp3)
            clips.append(cp); D.append(dur(mp3)); spans.append(sp); voices.append(mp3)
            print(f"   clip={cid} {round(D[-1],2)}s",flush=True)
        N=len(clips)
        if N<2: raise RuntimeError(f"{lang}: собрано сцен {N} — нечего монтировать (нет клипов/сети)")
        D[-1]+=0.5
        # список строим по реально скачанным сценам: при пропуске нумерация файлов рвётся
        with open(f"{WORK}/{lang}_vl.txt","w") as f:
            for mp3 in voices: f.write(f"file '{mp3}'\n")
        ff(["-f","concat","-safe","0","-i",f"{WORK}/{lang}_vl.txt","-c","copy",f"{WORK}/{lang}_v.mp3"])
        ff(["-i",f"{WORK}/{lang}_v.mp3","-af","apad=pad_dur=0.5","-q:a","4",f"{WORK}/{lang}_vp.mp3"])
        TOTAL=sum(D)
        # музыка + микс под голос
        if MUSIC and os.path.exists(MUSIC): mus=MUSIC
        else: mus=f"{WORK}/{lang}_mus.wav"; make_music(TOTAL,mus)
        ff(["-i",f"{WORK}/{lang}_vp.mp3","-i",mus,"-filter_complex",
            "[1]volume=0.10[m];[0][m]amix=inputs=2:normalize=0:duration=first[a]",
            "-map","[a]","-t",f"{TOTAL:.2f}",f"{WORK}/{lang}_aud.m4a"])
        # монтаж: ТОЛЬКО видео + аудио (без субтитров и заголовка)
        inputs=[]
        for cp in clips: inputs+=["-i",cp]
        inputs+=["-i",f"{WORK}/{lang}_aud.m4a"]; AI=N; fd=0.28; parts=[]
        for i in range(N):
            st=0.4; Di=D[i]
            parts.append(f"[{i}:v]trim={st}:{st+Di:.3f},setpts=PTS-STARTPTS,"
                f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p,"
                f"fade=t=in:st=0:d={fd},fade=t=out:st={max(0,Di-fd):.3f}:d={fd}[v{i}]")
        parts.append("".join(f"[v{i}]" for i in range(N))+f"concat=n={N}:v=1:a=0[v]")
        open(f"{WORK}/{lang}_fg.txt","w").write(";".join(parts))
        try:
            ff([*inputs,"-filter_complex_script",f"{WORK}/{lang}_fg.txt","-map","[v]","-map",f"{AI}:a",
                "-r","30","-t",f"{TOTAL:.2f}","-c:v","libx264","-pix_fmt","yuv420p","-preset","medium","-crf","20",
                "-c:a","aac","-b:a","160k","-movflags","+faststart",cfg["out"]])
            print(f"DONE [{lang}] {cfg['out']} dur {round(TOTAL,2)} (video+voice+music)",flush=True)
        except RuntimeError as e:
            print(f"ERR {lang}\n{e}")

if __name__=="__main__": main()
