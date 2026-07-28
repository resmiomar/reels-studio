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

# произношение для ОЗВУЧКИ (не для субтитров): латиница/англ -> кириллица
# Произношение брендов. ОДИНАКОВО в казахском И русском видео — нақ қазақша написание.
# (Прим.: русский голос физически не выговаривает Ғ/Қ/ұ и прочтёт их как г/к/у;
#  чтобы бренд ЗВУЧАЛ по-настоящему по-казахски в рус.видео — озвучивать бренд-слова
#  казахским голосом, см. заметку в конце файла.)
_BRANDS={"Telegram":"Телеграм","Qujat":"Құжат","Qyran":"Қыран","Qalqan":"Қалқан",
         "Sabaq":"Сабақ","Galamtor":"Ғаламтор","Jel":"Жел","Ibook":"Айбук","ibook":"Айбук"}
PHON={"kk":_BRANDS,"ru":_BRANDS}
def phon(t,lang):
    for a,b in PHON.get(lang,{}).items(): t=t.replace(a,b)
    return t

# несколько голосов на язык — агент чередует их (разнообразие между постами).
# можно зафиксировать через env VOICE_KK / VOICE_RU.
# несколько БЕСПЛАТНЫХ платформ+голосов на язык -> чередуются для разнообразия.
# формат (engine, id). engine: edge | gtts | mms. env override: VOICE_KK="mms:facebook/mms-tts-kaz"
VOICES={
 # клоны голоса пользователя (ElevenLabs v3) — казах БЕЗ акцента + человеческий.
 # Laura + Bala чередуются (разнообразие). Форсить: VOICE_KK="eleven:xKWShjEXraJurmIX5TZM"
 # Laura=xKWShjEXraJurmIX5TZM, Bala=M4jzBCMPD6005WAnM0H9
 "kk":[("eleven","xKWShjEXraJurmIX5TZM"),("eleven","M4jzBCMPD6005WAnM0H9")],
 "ru":[("eleven","xKWShjEXraJurmIX5TZM"),("eleven","M4jzBCMPD6005WAnM0H9")],
}
# ПРОЕКТЫ пользователя. Выбор через env PROJECT (по умолч. qujat). Кадры — строго по теме!
PROJECT=os.environ.get("PROJECT","qujat")
PROJECTS={
 # Qujat — бухгалтерия/налоги. Кадры: документы, налоги, калькулятор, таблицы. НЕ трейдинг-графики!
 "qujat":dict(title={"kk":"САЛЫҚ ЕНДІ — ОҢАЙ","ru":"НАЛОГИ — ЭТО ЛЕГКО"}, scenes=[
   dict(q="financial documents paperwork office desk",
        kk="Бухгалтерия басыңды ауыртып жүр ме?", ru="Бухгалтерия отнимает всё твоё время?"),
   dict(q="calculator counting money banknotes finance",
        kk="Құжат салық пен есептерді өзі санайды.", ru="Құжат сам считает налоги и отчёты."),
   dict(q="accountant signing invoice documents pen desk",
        kk="Есеп-қисап бір минутта дайын болады.", ru="Отчёт готов всего за одну минуту."),
   dict(q="accounting spreadsheet table laptop screen office",
        kk="Телеграмдағы бот та, сайт та дайын.", ru="В Телеграме есть и бот, и сайт."),
   dict(q="asian business people meeting handshake office",
        kk="Қазір тегін бастап көріңіз, Құжатқа жазыңыз!", ru="Начните бесплатно, напишите в Құжат!"),
 ]),
 # ibook (Айбук) — брондау/booking маркетплейс. Кадры: телефон-қосымша, қонақүй, төлем, саяхат.
 "ibook":dict(title={"kk":"БРОНЬДІ ОҢАЙ ЖАСА","ru":"БРОНИРУЙ ЛЕГКО"}, scenes=[
   dict(q="hands using smartphone booking travel app",
        kk="Брондау деген қиынға соғып жүр ме?", ru="Бронировать долго и неудобно?"),
   dict(q="modern hotel room interior travel",
        kk="Айбук — бәрін бір қосымшада брондайсың.", ru="Айбук — бронируй всё в одном приложении."),
   dict(q="asian woman booking appointment smartphone online",
        kk="Қонақүй, қызмет, орынды бірнеше түртумен таңдайсың.", ru="Отель, услугу, место — в пару касаний."),
   dict(q="online payment smartphone mobile checkout",
        kk="Онлайн төле, растауды бірден ал.", ru="Оплати онлайн, получи подтверждение сразу."),
   dict(q="asian traveler happy using phone city street",
        kk="Қазір Айбукты жүктеп алыңыз!", ru="Скачайте Айбук прямо сейчас!"),
 ]),
}
P=PROJECTS[PROJECT]; SCENES=P["scenes"]
OUTDIR=os.environ.get("OUT_DIR",os.path.expanduser("~/Downloads"))
os.makedirs(OUTDIR,exist_ok=True)
# язык(и) можно ограничить через env LANGS_ONLY="kk" или "ru"
_only=os.environ.get("LANGS_ONLY","")
LANGS={
 "kk": dict(rate="-4%", title=P["title"]["kk"], out=f"{OUTDIR}/{PROJECT}-STOCK-KZ.mp4"),
 "ru": dict(rate="+0%", title=P["title"]["ru"], out=f"{OUTDIR}/{PROJECT}-STOCK-RU.mp4"),
}
if _only in ("kk","ru"): LANGS={_only:LANGS[_only]}

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
        for i,s in enumerate(SCENES):
            print(f"[{lang} {i}] '{s['q']}'",flush=True)
            cid,link=find_clip(s["q"],used)
            if not link: print("   ! нет клипа"); continue
            cp=f"{WORK}/{lang}_c{i}.mp4"
            if not download(link,cp): continue
            mp3=f"{WORK}/{lang}_l{i}.mp3"
            sp=gen_voice(engine,vid,phon(s[lang],lang),cfg["rate"],mp3)
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
