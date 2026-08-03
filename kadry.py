#!/usr/bin/env python3
"""
Кадровая база ibook - свой склад видео вместо поиска по стоку на каждый ролик.

Почему так. Раньше движок на каждый кадр лез в сток с запросом, слепленным из
описания сцены. Запрос получался общий, сток отдавал что попало, и кадр не
совпадал со сценарием. Теперь мы один раз собираем СВОЮ базу под мир ibook -
мастера, салоны, клиенты, запись в телефоне - размечаем её по сценам и типажам,
а при сборке ролика подбираем кадр по смыслу сцены из своего склада.

    python kadry.py собрать              скачать базу (один раз, долго)
    python kadry.py собрать barber        добрать одну сцену
    python kadry.py склад                 что уже лежит
    python kadry.py подбор "описание" ru  проверить, какой кадр подберётся
    python kadry.py добавить <папка> <сцена>   свои съёмки и записи экрана ibook

База лежит на внешнем диске и заново не качается. Интернет нужен только на сбор.
"""
import os, sys, json, re, random, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PROJECT", "ibook")

BASE = os.environ.get("KADRY", "/Volumes/T7/ibook/kadry")
INDEX = os.path.join(BASE, "index.json")

# ── Типажи. У каждого рынка своё лицо в кадре: ролик для Казахстана с
# европейской моделью читается как чужая реклама и не продаёт.
CASTING = {
    "aziat":   ("kk", "ru", "uz", "tr"),
    "slavyan": ("rf", "uk"),
    "kitaec":  ("zh",),
    "evropa":  ("en", "de", "it", "es", "fr"),
}
LANG_CAST = {l: c for c, ls in CASTING.items() for l in ls}
FACE = {"aziat": "asian", "slavyan": "", "kitaec": "chinese", "evropa": ""}

# ── Сцены мира ibook.
#   queries - чем добывать со стока
#   slova   - СИЛЬНЫЕ слова: встретилось - почти наверняка эта сцена
#   fon     - слабые слова: встречаются во многих описаниях, только уточняют
#
# Разделение обязательно. Слова «salon», «studio», «interior» стоят почти в каждом
# описании кадра, и без веса сцена «стойка салона» перетягивала на себя две трети
# всех кадров - именно из-за этого ролики и не совпадали со сценарием.
SCENES = {
 "barber": dict(
   queries=["barber cutting mens hair","barbershop haircut client","mens haircut clippers"],
   slova="barber barbershop clipper clippers fade beard shave",
   fon="haircut mens cutting hair chair"),
 "parikmaher": dict(
   queries=["hairdresser styling long hair salon","hair stylist blow dry client","hair coloring salon"],
   slova="hairdresser stylist blow curling coloring highlights",
   fon="hair styling salon client chair"),
 "nogti": dict(
   queries=["nail artist manicure closeup","manicure salon hands","nail technician working"],
   slova="nail nails manicure pedicure polish",
   fon="technician artist hands"),
 "brovi": dict(
   queries=["eyebrow artist shaping brows","lash extension technician","brow lamination studio"],
   slova="brow brows eyebrow eyebrows lash lashes lamination",
   fon="extension artist"),
 "kosmetolog": dict(
   queries=["facial treatment beautician","skincare cosmetologist client","face massage spa"],
   slova="facial cosmetologist beautician skincare esthetician peel",
   fon="treatment face cream"),
 "makiyazh": dict(
   queries=["makeup artist working on client","makeup brush closeup face","bridal makeup studio"],
   slova="makeup lipstick foundation bridal",
   fon="brush artist face"),
 "massazh": dict(
   queries=["massage therapist treatment room","back massage spa","therapist hands massage"],
   slova="massage masseuse therapist",
   fon="spa treatment relax back oil"),
 "vrach": dict(
   queries=["doctor talking to patient clinic","dentist working with patient","medical consultation office"],
   slova="doctor dentist clinic patient medical nurse",
   fon="consultation office appointment"),
 "salon_priem": dict(
   queries=["salon reception desk","beauty salon interior bright","spa front desk welcome"],
   slova="reception receptionist counter",
   fon="desk salon studio interior welcome"),
 "telefon_zapis": dict(
   queries=["woman booking appointment on phone","person scrolling phone smiling","tapping smartphone screen closeup"],
   slova="taps tapping booking books scrolling swipes",
   fon="phone smartphone screen app finger thumb"),
 "telefon_ustal": dict(
   queries=["tired woman texting phone at night","exhausted person phone evening","stressed typing messages"],
   slova="tired exhausted stressed sighs overwhelmed",
   fon="night evening messages typing replies late phone bed"),
 "telefon_zvonok": dict(
   queries=["woman making phone call worried","missed call phone screen","person calling no answer"],
   slova="calls calling ringing buzzing rings unanswered",
   fon="call phone answer waits"),
 "kalendar_plan": dict(
   queries=["planner calendar schedule desk","writing appointments notebook","weekly planner closeup"],
   slova="calendar planner schedule diary",
   fon="notebook appointments week writing pen"),
 "bumagi": dict(
   queries=["messy desk paper notes","counting receipts calculator","handwritten notes closeup"],
   slova="receipts calculator paper notes cluttered scattered",
   fon="table desk pen sorting pile"),
 "klient_dovolen": dict(
   queries=["happy client mirror after haircut","satisfied woman smiling salon","client looking mirror smiling"],
   slova="mirror satisfied delighted proud",
   fon="happy smiles smiling result client"),
 "master_portret": dict(
   queries=["confident beauty master portrait studio","professional stylist portrait","small business owner portrait"],
   slova="portrait owner entrepreneur",
   fon="confident master professional stands camera"),
 "pustoe_kreslo": dict(
   queries=["empty barber chair salon","empty salon interior quiet","empty waiting chairs"],
   slova="empty nobody unused vacant",
   fon="quiet alone waiting chair gap slot free"),
 "dengi": dict(
   queries=["card payment terminal closeup","counting money small business","contactless payment phone"],
   slova="money cash payment terminal banknotes wallet",
   fon="card pay price income earn"),
 "gorod": dict(
   queries=["city street walking day","woman walking street city","busy city sidewalk"],
   slova="street sidewalk crowd traffic",
   fon="city walking outside town"),
 "otdyh": dict(
   queries=["woman relaxing beach towel","vacation sun lounger phone","weekend park rest"],
   slova="beach vacation holiday lounger towel sunscreen",
   fon="rest weekend sun park"),
 "komanda": dict(
   queries=["salon team working together","beauty studio staff busy","coworkers salon talking"],
   slova="team staff coworkers colleagues",
   fon="together several masters talking"),
 "otzyv": dict(
   queries=["reading reviews on phone","five star rating phone screen","phone notification closeup"],
   slova="review reviews rating stars notification reminder",
   fon="phone message alert screen"),
}

STOP = set("""with the and her his into over from that this near then they slow shot close
hands hand looking while phone screen text logos frame camera down back next warm daylight
light bright soft slowly behind calm handheld mood sits face push through looks same
holding clean table young around room small static smooth wide medium shallow both
gentle quiet blurred accent tones purple violet central""".split())
# Слово, которое мы сами объявили значимым для какой-то сцены, из стоп-листа
# убираем: иначе «chair» или «phone» вычёркиваются раньше, чем успеют помочь.
STOP -= {w for d in SCENES.values() for w in (d["slova"] + " " + d.get("fon", "")).split()}


def load_index():
    return json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else {}


def save_index(ix):
    os.makedirs(BASE, exist_ok=True)
    tmp = INDEX + ".part"
    json.dump(ix, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, INDEX)


def cmd_sklad():
    ix = load_index()
    if not ix:
        print("склад пуст. Собрать:  python kadry.py собрать"); return
    print(f"{'сцена':16}" + "".join(f"{c:10}" for c in CASTING) + "  всего")
    print("-" * 62)
    tot = 0
    for s in SCENES:
        row, n = "", 0
        for c in CASTING:
            k = len([1 for v in ix.values() if v["scene"] == s and v["cast"] == c])
            row += f"{k:<10}"; n += k
        tot += n
        print(f"{s:16}{row}  {n}")
    gb = sum(v.get("bytes", 0) for v in ix.values()) / 1e9
    print("-" * 62)
    print(f"{'ИТОГО':16}{'':40}  {tot} клипов, {gb:.1f} ГБ")


def score(prompt, scene):
    """Насколько кадр этой сцены подходит под описание из сценария.

    Сильное слово весит втрое: «barber» решает сцену сам по себе, а «chair»
    или «studio» стоят в половине описаний и могут только уточнить.
    """
    words = {w for w in re.findall(r"[a-z]+", prompt.lower()) if len(w) > 2 and w not in STOP}
    d = SCENES[scene]
    return 3 * len(words & set(d["slova"].split())) + len(words & set(d.get("fon", "").split()))


def pick_scene(prompt):
    """Сцену считаем опознанной только если сработало сильное слово: совпадение
    по одному фону значит, что мы просто угадываем, и лучше уйти в живой сток."""
    best = max(SCENES, key=lambda s: (score(prompt, s), s))
    return best if score(prompt, best) >= 3 else None


def cmd_podbor(prompt, lang="ru"):
    cast = LANG_CAST.get(lang, "evropa")
    s = pick_scene(prompt)
    if not s:
        print("сцена не опознана - движок уйдёт в сток"); return
    ix = load_index()
    have = [v for v in ix.values() if v["scene"] == s and v["cast"] == cast]
    print(f"сцена: {s}  (совпало слов: {score(prompt,s)})")
    print(f"типаж: {cast}   на складе: {len(have)} клипов")
    if have: print("например:", os.path.basename(random.choice(have)["path"]))


def cmd_dobavit(folder, scene, cast="lyuboy"):
    """Свои съёмки в склад: запись экрана приложения, снятое мастером, что угодно.

    Настоящий экран ibook в кадре «клиент выбирает время» бьёт любой сток, поэтому
    свои клипы помечаются отдельно и при подборе идут первыми.
    """
    if scene not in SCENES:
        print("нет такой сцены:", scene, "\nесть:", " ".join(SCENES)); return
    folder = os.path.expanduser(folder)
    if not os.path.isdir(folder):
        print("нет такой папки:", folder); return
    vid = [f for f in sorted(os.listdir(folder)) if f.lower().endswith((".mp4", ".mov", ".m4v"))]
    if not vid:
        # без этого команда молча отвечала «0» и было непонятно, что делать
        print(f"В папке {folder} нет видео - добавлять нечего.\n"
              f"Запиши экран телефона, скинь файлы сюда и запусти команду снова.\n"
              f"Открыть папку:  open {folder}")
        return
    ix = load_index()
    d = os.path.join(BASE, scene, cast); os.makedirs(d, exist_ok=True)
    n = 0
    for f in vid:
        src = os.path.join(folder, f)
        key = "svoi-" + scene + "-" + os.path.splitext(f)[0]
        if key in ix: continue
        dst = os.path.join(d, key + ".mp4")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                        "-an", dst], check=False)
        if not os.path.exists(dst): print("  не сконвертировался:", f); continue
        r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                            "-of", "csv=p=0", dst], capture_output=True, text=True)
        try: dd = float(r.stdout.strip())
        except ValueError: dd = 0.0
        if dd < 2.0: print(f"  {f}: {dd:.1f}s, коротко"); continue
        ix[key] = {"scene": scene, "cast": cast, "path": dst, "sec": round(dd, 1),
                   "bytes": os.path.getsize(dst), "q": "своя съёмка", "svoi": True}
        n += 1; save_index(ix)
        print(f"  + {f}  {dd:.1f}s", flush=True)
    print(f"добавлено своих клипов: {n} в сцену {scene}")


def cmd_sobrat(only=None, per=int(os.environ.get("PER", "12"))):
    import reel_engine as R
    ix = load_index()
    scenes = [only] if only else list(SCENES)
    for s in scenes:
        if s not in SCENES:
            print("нет такой сцены:", s); continue
        for cast in CASTING:
            d = os.path.join(BASE, s, cast); os.makedirs(d, exist_ok=True)
            have = [1 for v in ix.values() if v["scene"] == s and v["cast"] == cast]
            need = per - len(have)
            if need <= 0:
                print(f"  {s}/{cast}: уже {len(have)}, пропускаю"); continue
            print(f"  {s}/{cast}: нужно ещё {need}", flush=True)
            got = 0
            for q in SCENES[s]["queries"]:
                if got >= need: break
                full = (FACE[cast] + " " + q).strip() + " bright modern"
                for orient in ("portrait", "landscape"):
                    if got >= need: break
                    try:
                        url = ("https://api.pexels.com/videos/search?query="
                               + R.urllib.parse.quote(full) + f"&per_page=40&orientation={orient}")
                        vids = list(R.api(url).get("videos", []))
                    except Exception as e:
                        print(f"    сток не ответил: {str(e)[:60]}", flush=True); continue
                    random.shuffle(vids)
                    for v in vids:
                        if got >= need: break
                        vid = str(v["id"])
                        if vid in ix: continue
                        fs = [f for f in v["video_files"] if f.get("height")]
                        ok = [f for f in fs if (f["height"] or 0) >= 1080]
                        cand = sorted(ok, key=lambda f: f["height"]) or sorted(fs, key=lambda f: -(f["height"] or 0))
                        if not cand: continue
                        p = os.path.join(d, f"{vid}.mp4")
                        if not R.download(cand[0]["link"], p): continue
                        dd = R.dur(p)
                        if dd < 3.0:                     # короче трёх секунд в монтаж не годится
                            print(f"    {vid}: {dd:.1f}s, коротко", flush=True); continue
                        ix[vid] = {"scene": s, "cast": cast, "path": p, "sec": round(dd, 1),
                                   "bytes": os.path.getsize(p), "q": full}
                        got += 1
                        save_index(ix)
                        print(f"    + {vid}  {dd:.1f}s  ({got}/{need})", flush=True)
    cmd_sklad()


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "помощь"): print(__doc__)
    elif a[0] == "склад": cmd_sklad()
    elif a[0] == "собрать": cmd_sobrat(a[1] if len(a) > 1 else None)
    elif a[0] == "подбор": cmd_podbor(a[1], a[2] if len(a) > 2 else "ru")
    elif a[0] == "добавить": cmd_dobavit(a[1], a[2], a[3] if len(a) > 3 else "lyuboy")
    else: print("не знаю команду:", a[0]); print(__doc__)
