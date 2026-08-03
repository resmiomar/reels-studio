#!/usr/bin/env python3
"""
stock_reel.py — авто-агент: тема -> 9:16 Reels из бесплатного стока (Pexels).
Живое видео + верхний заголовок-хук + авто-субтитры (Montserrat, средний размер,
синхрон по речи) + мягкая фоновая музыка. Версии KZ+RU, РАЗНЫЕ кадры.
Бренд-слова произносятся по-местному (PHON), написание не меняется.
env: PEXELS_KEY. Бесплатно. Кредит Pexels — в описании поста.
"""
import urllib.request, urllib.parse, json, os, subprocess, random, time, re, shutil, glob

_HERE=os.path.dirname(os.path.abspath(__file__))
FONT=os.environ.get("FONT") or os.path.join(_HERE,"assets","Montserrat.ttf")  # вложен в репо: без сети
# запасные системные шрифты, если вложенного нет и скачать не вышло
FONT_FALLBACKS=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc"]
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
KEY=os.environ.get("PEXELS_KEY","")  # ленивая проверка: нужен при вызове api(), не при импорте
W,H=1080,1920
# Кодек строго под Instagram Reels: 1080x1920, 30 fps, H.264 High, yuv420p,
# СТЕРЕО 48 кГц (моно Instagram воспроизводит криво), запас по битрейту -
# площадка всё равно пережмёт, поэтому отдаём с запасом. bt709 чтобы не увело цвет.
REELS_ENC=["-c:v","libx264","-pix_fmt","yuv420p","-profile:v","high","-level","4.0",
           "-preset","medium","-crf","18","-maxrate","8M","-bufsize","12M",
           "-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709",
           "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
           "-movflags","+faststart"]
# Громкость итогового ролика. Telegram проигрывает звук как есть, без выравнивания
# громкости, поэтому тихий ролик приходится слушать на максимуме. -12 LUFS - уровень,
# на котором ролики звучат в ленте наравне с остальными.
# Одного выравнивания мало: упираемся в пики и громче не становится. Сначала
# поджимаем динамику компрессором - тогда средний уровень поднимается, а пики
# остаются на месте. Так делают все, чей звук в ленте слышно без выкручивания.
LOUD=os.environ.get("LOUD","acompressor=threshold=-22dB:ratio=4:attack=5:release=120:makeup=4,"
                           "loudnorm=I=-10:TP=-1.0:LRA=6,volume=3dB,"
                           "alimiter=limit=0.85:level=disabled")
# Скретч по умолчанию на внешний диск, если он подключён: скачанные клипы
# занимают сотни мегабайт, а на встроенном диске места нет.
_T7="/Volumes/T7/ibook/work"
_DEF=_T7 if os.path.isdir("/Volumes/T7/ibook") else "/tmp/stock_reel_v4"
WORK=os.environ.get("WORK",_DEF); os.makedirs(WORK,exist_ok=True)
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
LAURA="xKWShjEXraJurmIX5TZM"; BALA="M4jzBCMPD6005WAnM0H9"
# ВСЕ языки идут на клон-голосе владельца (ElevenLabs v3): бесплатные Edge-голоса
# звучат роботом, особенно узбекский, и слушатель сразу считывает синтез.
# Модель мультиязычная, поэтому один и тот же клон говорит на всех языках -
# бонусом единый голос бренда во всех странах.
# КАКОЙ ДВИЖОК НА КАКОМ ЯЗЫКЕ.
# Цель - уйти от подписки: всё, что умеет локальная модель, считаем на своём Mac
# бесплатно и без лимитов. ElevenLabs оставляем только там, где локальной
# альтернативы нет: казахский (мультиязычная база его не знает).
# Переключатель: ENGINE=eleven вернёт всё на платный, ENGINE=local - всё на локальный.
_FORCE=os.environ.get("ENGINE","")

# Родной диктор на каждый рынок. Раньше все языки читал клон одного голоса -
# китаец слышал иностранца с акцентом, немец тоже. Теперь у каждого языка свой
# носитель. Лицензии проверены поштучно: у голоса, который запрещает коммерцию
# или не объявил лицензию, брать нельзя - приложение продаёт подписки.
#   kk  ISSAI, Назарбаев Университет   CC-BY    4 диктора (2 забракованы владельцем)
#   uk  Тетяна и Микита                MIT      2 диктора
#   zh  Chaowen                        CC0      (два других китайских голоса - нельзя)
#   en  LibriTTS                       CC-BY    (lessac, ryan, hfc - нельзя)
#   de  Thorsten                       CC0
#   fr  Siwis                          CC-BY
#   es  Claude                         Apache
# Турецкому и итальянскому чистого носителя не нашлось: единственные модели
# либо запрещают коммерцию, либо молчат о лицензии. Они остаются на Chatterbox -
# там лицензия MIT и всё чисто, ценой лёгкого акцента.
NATIVE={
 "kk":[f"kk_KZ-issai-high:{n}" for n in (0,1,3,4)],
 "uk":["uk_UA-tetiana-high","uk_UA-mykyta-high"],
 "zh":["zh_CN-chaowen-medium"],
 "en":["en_US-libritts-high:0","en_US-libritts-high:12"],
 "de":["de_DE-thorsten-high"],
 "fr":["fr_FR-siwis-medium"],
 "es":["es_MX-claude-high"],
}
VOICES={}
for _l in ("kk","ru","rf","uk","uz","tr","zh","en","de","it","es","fr"):
    if _FORCE=="eleven":
        VOICES[_l]=[("eleven",LAURA),("eleven",BALA)]
    elif _l in NATIVE and _FORCE!="chatterbox":
        VOICES[_l]=[("piper",v) for v in NATIVE[_l]]
    else:
        # ru и rf сознательно остаются на клон-голосе: это языки владельца,
        # он их слышит и хочет узнаваемый голос бренда.
        VOICES[_l]=[("chatterbox",_l)]

LANG_CODE={"kk":"KZ","ru":"RU","zh":"ZH","de":"DE","it":"IT",
           "tr":"TR","uk":"UK","es":"ES","fr":"FR","uz":"UZ",
           "en":"EN","rf":"RF"}   # en/rf есть только в годовом плане
# Рынок ролика простыми словами - чтобы в Telegram не было путаницы между языками
# Страна и язык по-русски -> идут в ИМЯ ФАЙЛА, чтобы владелец не путался:
# он этих языков не знает и по самому видео рынок не определит.
COUNTRY={"kk":"Казахстан","ru":"Казахстан","rf":"Россия","uk":"Украина","uz":"Узбекистан",
         "tr":"Турция","zh":"Китай","en":"США","de":"Германия","it":"Италия",
         "es":"Испания","fr":"Франция"}
LANGRU={"kk":"казахский","ru":"русский","rf":"русский","uk":"украинский","uz":"узбекский",
        "tr":"турецкий","zh":"китайский","en":"английский","de":"немецкий","it":"итальянский",
        "es":"испанский","fr":"французский"}
MARKET={"kk":"для Казахстана · казахский","ru":"для Казахстана · русский",
        "rf":"для России · русский","uk":"для Украины · украинский",
        "uz":"для Узбекистана · узбекский","tr":"для Турции · турецкий",
        "zh":"для Китая · китайский","en":"для США и мира · английский",
        "de":"для Германии · немецкий","it":"для Италии · итальянский",
        "es":"для Испании · испанский","fr":"для Франции · французский"}
LANG_NAME={"kk":"Қазақша","ru":"Русский","zh":"中文","de":"Deutsch","it":"Italiano",
           "tr":"Türkçe","uk":"Українська","es":"Español","fr":"Français","uz":"O‘zbekcha",
           "en":"English","rf":"Русский · РФ"}
# ===== РЕЖИМ ГОДОВОГО ПЛАНА =====
# SOURCE=year WEEK=1 SLOT=A -> берём готовый 30-секундный сценарий из ~/ibook-video/videos_<lang>.json
# (5 кадров с таймингами 0-4/4-11/11-19/19-26/26-30, озвучка 62-76 слов) и рендерим его стоком.
# Сценарии ищем сначала рядом с кодом - так они уезжают на сервер вместе с ним.
# Первый серверный прогон собрал ноль роликов именно потому, что папка со
# сценариями осталась на Mac владельца.
_SC=os.path.join(_HERE,"scenarii")
YEAR_DIR=os.environ.get("YEAR_DIR", _SC if os.path.isdir(_SC)
                        else os.path.expanduser("~/ibook-video"))
SOURCE=os.environ.get("SOURCE","")
WEEK=int(os.environ.get("WEEK","1")); SLOT=os.environ.get("SLOT","A")
NUM=(WEEK-1)*3+{"A":1,"B":2,"C":3}.get(SLOT,1)   # сквозной номер: 1..156
# Никаких субтитров и надписей на кадре: видео чистое, призыв звучит голосом
# и уходит в подпись поста. Вернуть плашку: CTA_CARD=1
CTA_CARD=os.environ.get("CTA_CARD","")=="1"
# Финальный призыв: где скачать. Дописывается в конец озвучки и печатается на последнем кадре.
# Финальный призыв зависит от АУДИТОРИИ ролика: мастеру и салону нужно открыть
# запись, клиенту - записаться. Тексты лежат в cta_lines.json, правятся руками.
# Про «карту не нужна» не говорим: оплата идёт внутри приложения (Apple/Google Pay).
_CTA_FILE=os.path.join(_HERE,"cta_lines.json")
STORE_LINE=json.load(open(_CTA_FILE,encoding="utf-8")) if os.path.exists(_CTA_FILE) else {}
def cta_line(lang,aud):
    d=STORE_LINE.get(lang) or STORE_LINE.get("en") or {}
    return d.get("client" if aud=="client" else "pro","")
STORE_CARD={"ru":"СКАЧАЙ ibook","kk":"ibook ЖҮКТЕП АЛ","rf":"СКАЧАЙ ibook","uk":"ЗАВАНТАЖ ibook",
            "uz":"ibook YUKLAB OL","tr":"ibook İNDİR","en":"GET ibook","zh":"下载 ibook"}
def year_card(lang):
    """Сценарий недели из годового плана. Языки плана шире, чем у стокового движка."""
    p=os.path.join(YEAR_DIR,f"videos_{lang}.json")
    if not os.path.exists(p): raise RuntimeError(f"нет годового плана: {p}")
    for v in json.load(open(p,encoding='utf-8')):
        if v["week"]==WEEK and v["slot"]==SLOT: return v
    raise RuntimeError(f"{lang}: нет ролика {WEEK}{SLOT}")
# Типаж людей на кадре под аудиторию языка. БЕЗ этого сток отдаёт кого попало:
# в сценарии типаж указан только в первом кадре ("Central Asian barber"), а обрезка
# запроса его теряла - и в ролик для Казахстана попадали неподходящие лица.
PEOPLE={"kk":"asian","ru":"asian","uz":"asian","zh":"asian",
        "tr":"turkish","uk":"european","rf":"european","en":"european",
        "de":"european","it":"european","es":"european","fr":"european"}
# Без этих слов сток отдаёт тесные, тёмные и неопрятные съёмки. Просим премиальную картинку.
LOOK="modern bright clean"
# Кадр подбираем ПО ТЕКСТУ СЦЕНАРИЯ владельца, а не своими общими запросами:
# ролик обязан совпадать с его историей. Но промпт написан под ИИ-генерацию,
# поэтому чистим его от того, что ломает поиск по стоку:
#  - "barber" тянет старые тесные парикмахерские -> hairdresser / hair salon;
#  - названия городов и операторский жаргон на стоке бесполезны;
#  - без якорей качества выдача уходит в тёмное и неопрятное.
# Instagram - не телевизор: первый кадр должен цеплять. Крупный живой план.
HOOK_Q=["woman surprised shocked face close up",
        "woman talking to camera close up bright",
        "woman face close up beauty makeup bright"]
SWAP={"barber":"hairdresser","barbershop":"hair salon","barbers":"hairdressers",
      "stylist":"hairdresser","hairstylist":"hairdresser"}
JUNK={"a","an","the","of","in","on","at","with","and","or","his","her","their","its","he","she",
      "same","very","then","while","behind","next","into","from","for","as","is","are",
      "slow","soft","warm","cool","golden","natural","shallow","depth","field","tones","light",
      "camera","shot","close","up","wide","push","pull","dolly","gimbal","handheld","orbit",
      "drifts","drifting","moves","pulls","pushes","tilts","arc","angle","frame","cut","cuts",
      "no","text","logos","logo","watermark","seconds","second","sec",
      "almaty","astana","kazakhstan","istanbul","paris","berlin","milan","madrid","shanghai",
      "moscow","kyiv","tashkent","modern","bright","clean"}
def shot_query(prompt,lang=""):
    t=re.sub(r"[^A-Za-z ]"," ",prompt.lower())
    ws=[]
    for w in t.split():
        w=SWAP.get(w,w)
        if w in JUNK or len(w)<3: continue
        if w not in ws: ws.append(w)
    people=PEOPLE.get(lang,"")
    # типаж уже может стоять в самом сценарии («European hairdresser») - не дублируем
    if people and people in ws[:5]: people=""
    # 5 значимых слов сценария + типаж + якоря качества
    return " ".join([x for x in [people]+ws[:5]+["bright","modern"] if x])
def shot_queries(card,lang=""):
    return [shot_query(sh["prompt"],lang) for sh in card["shots"]]

def fit_durations(weight,cap,need):
    """Раздаёт need секунд между кадрами пропорционально весу сценария, но НИКОГДА
    не просит у клипа больше, чем в нём реально есть. Раньше этого не было: движок
    брал длительность из сценария, а сток отдавал клип короче - видео обрывалось
    и последний кадр висел замерший, пока доигрывал голос."""
    n=len(weight); out=[0.0]*n; free=set(range(n)); rest=need
    for _ in range(n+2):
        tw=sum(weight[i] for i in free) or 1.0
        over=[i for i in free if rest*weight[i]/tw>cap[i]]
        if not over: break
        for i in over:
            out[i]=cap[i]; rest-=cap[i]; free.discard(i)
        if not free: break
    tw=sum(weight[i] for i in free) or 1.0
    for i in free: out[i]=max(0.6,rest*weight[i]/tw)
    return out

def spans_of(card):
    """Тайминги кадров -> длительности. Потом масштабируем под реальную длину озвучки."""
    out=[]
    for sh in card["shots"]:
        a,b=sh["sec"].split("-"); out.append(max(0.6,float(b)-float(a)))
    return out

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
 # ibook - маркетплейс БРОНИ УСЛУГ: мастер, врач, барбер, косметолог, салон.
 # ОТЕЛЕЙ И ПУТЕШЕСТВИЙ В ПРОДУКТЕ НЕТ - не рекламируем то, чего не умеем.
 "ibook":{
  "kk":dict(title="ЖАЗЫЛУ ЕНДІ ОҢАЙ",scenes=[
   dict(t="Жазылу үшін қоңырау шалып жүрсің бе?",q="woman calling phone appointment waiting"),
   dict(t="ibook, бәрін бір қосымшадан жазыласың.",q="asian hairdresser client salon chair"),
   dict(t="Шаштараз, дәрігер, косметолог, бәрі бірнеше түртумен.",q="asian woman booking appointment smartphone online"),
   dict(t="Онлайн төле, растауды бірден ал.",q="online payment smartphone mobile checkout"),
   dict(t="Қазір ibookты жүктеп алыңыз!",q="happy asian woman smiling after haircut"),
  ]),
  "ru":dict(title="ЗАПИСЫВАЙСЯ ЛЕГКО",scenes=[
   dict(t="Записаться можно только через звонок?",q="person frustrated waiting phone call"),
   dict(t="ibook, записывайся ко всем в одном приложении.",q="woman using booking app smartphone home"),
   dict(t="Мастер, врач, барбер, всё в пару касаний.",q="beauty salon manicure client hands"),
   dict(t="Оплати онлайн, получи подтверждение сразу.",q="contactless payment smartphone terminal"),
   dict(t="Скачайте ibook прямо сейчас!",q="happy woman smiling walking city street"),
  ]),
  "zh":dict(title="预约就该这么轻松",scenes=[
   dict(t="还在打电话预约，等半天没回复？",q="asian woman frustrated phone call"),
   dict(t="ibook，所有预约一个应用搞定。",q="asian woman using smartphone app"),
   dict(t="理发、医生、美甲，动动手指就搞定。",q="asian woman beauty salon appointment"),
   dict(t="线上付款，马上收到确认通知。",q="asian woman mobile payment smartphone"),
   dict(t="现在就下载ibook，约起来！",q="happy asian woman smiling smartphone"),
  ]),
  "de":dict(title="EINFACH BUCHEN",scenes=[
   dict(t="Für jeden Termin erst mal anrufen und warten?",q="frustrated woman waiting phone cafe"),
   dict(t="Mit ibook buchst du alles in einer App.",q="young woman using smartphone city"),
   dict(t="Friseur, Arzt oder Kosmetik, mit wenigen Klicks gebucht.",q="hair salon stylist happy client"),
   dict(t="Bezahl online, deine Bestätigung kommt sofort.",q="online payment smartphone card hands"),
   dict(t="Hol dir ibook jetzt in deinem App Store.",q="smiling woman smartphone european street"),
  ]),
  "it":dict(title="PRENOTA FACILE",scenes=[
   dict(t="Per ogni appuntamento devi sempre telefonare?",q="woman annoyed waiting phone call"),
   dict(t="Con ibook prenoti tutto in un'unica app.",q="woman using booking app smartphone"),
   dict(t="Parrucchiere, medico o estetista, bastano pochi tocchi.",q="hairdresser working client salon"),
   dict(t="Paghi online e ricevi subito la conferma.",q="online payment credit card smartphone"),
   dict(t="Scarica ibook adesso, il primo appuntamento ti aspetta.",q="happy young woman smiling smartphone city"),
  ]),
  "tr":dict(title="KOLAY RANDEVU",scenes=[
   dict(t="Randevu almak neden hep telefonla oluyor?",q="young turkish woman frustrated with phone"),
   dict(t="ibook ile her randevunu tek uygulamadan al.",q="turkish woman using smartphone app cafe"),
   dict(t="Kuaför, doktor, güzellik uzmanı, birkaç dokunuşla hazır.",q="turkish barber shop client haircut"),
   dict(t="Online öde, onayını saniyeler içinde al.",q="woman paying online with phone shop"),
   dict(t="ibook'u hemen indir, sıra sende!",q="happy turkish woman smiling holding phone"),
  ]),
  "uk":dict(title="ЗАПИСУЙСЯ ЛЕГКО",scenes=[
   dict(t="Набридло дзвонити й чекати відповіді годинами?",q="young woman annoyed waiting phone call"),
   dict(t="ibook, записуйся до всіх в одному застосунку.",q="woman using booking app smartphone home"),
   dict(t="Майстер, лікар, барбер, усе за кілька дотиків.",q="modern hair salon interior stylist"),
   dict(t="Оплати онлайн і одразу отримай підтвердження.",q="woman paying online card smartphone cafe"),
   dict(t="Завантажуй ibook вже зараз і записуйся легко!",q="happy european woman smiling holding smartphone"),
  ]),
  "es":dict(title="RESERVA FÁCIL",scenes=[
   dict(t="¿Sigues llamando para pedir cita y esperando?",q="stressed woman phone call home"),
   dict(t="Con ibook lo reservas todo desde una sola app.",q="young european woman smartphone app"),
   dict(t="Peluquería, médico o estética, en un par de toques.",q="hair salon appointment client mediterranean"),
   dict(t="Paga online y recibe tu confirmación al instante.",q="woman online payment card phone"),
   dict(t="Descarga ibook ahora y reserva sin complicarte la vida.",q="happy woman smiling smartphone city"),
  ]),
  "fr":dict(title="RÉSERVE FACILEMENT",scenes=[
   dict(t="Tu galères encore à réserver un rendez-vous ?",q="frustrated woman waiting phone call"),
   dict(t="Avec ibook, tu réserves tout dans une seule appli.",q="young woman using smartphone app"),
   dict(t="Un coiffeur, un médecin, une esthéticienne, en deux clics.",q="hair salon client stylist working"),
   dict(t="Paie en ligne, ta confirmation arrive tout de suite.",q="woman paying online with phone"),
   dict(t="Télécharge ibook maintenant, ton prochain rendez-vous t'attend.",q="happy woman smiling phone street"),
  ]),
  "uz":dict(title="OSON YOZIL",scenes=[
   dict(t="Yozilish uchun yana qoʻngʻiroq qilyapsanmi?",q="asian woman frustrated phone call"),
   dict(t="ibook, hammasiga bitta ilovadan yozil.",q="asian woman using smartphone app"),
   dict(t="Sartarosh, shifokor, kosmetolog, bir necha bosishda.",q="asian barber shop client haircut"),
   dict(t="Onlayn toʻlov qil, tasdiqni darhol ol.",q="asian customer paying phone contactless"),
   dict(t="ibookni hoziroq telefoningga yuklab ol!",q="happy asian woman smiling smartphone"),
  ]),
 },
}
P=PROJECTS[PROJECT]
OUTDIR=os.environ.get("OUT_DIR",os.path.expanduser("~/Downloads"))
os.makedirs(OUTDIR,exist_ok=True)
if SOURCE=="year":
    LANGS={l:dict(rate="-4%" if l=="kk" else "+0%", title="", scenes=[],
                  out=f"{OUTDIR}/{NUM:03d}-{COUNTRY.get(l,l)}-{LANGRU.get(l,l)}.mp4")
           for l in LANG_CODE
           if os.path.exists(os.path.join(YEAR_DIR,f"videos_{l}.json"))}
else:
    LANGS={l:dict(rate="-4%" if l=="kk" else "+0%", title=P[l]["title"], scenes=P[l]["scenes"],
                  out=f"{OUTDIR}/{PROJECT}-STOCK-{LANG_CODE[l]}.mp4")
           for l in LANG_CODE if l in P}
# LANGS_ONLY="kk" или список "kk,ru,de" — иначе рендерим все языки проекта
_only=[x.strip() for x in os.environ.get("LANGS_ONLY","").split(",") if x.strip()]
if _only: LANGS={l:LANGS[l] for l in _only if l in LANGS}

def api(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"Authorization":KEY,"User-Agent":UA}),timeout=20))
# ПАМЯТЬ ИСПОЛЬЗОВАННЫХ КЛИПОВ МЕЖДУ ЗАПУСКАМИ.
# Каждый ролик рендерится отдельным процессом, поэтому множество used обнулялось,
# и на один и тот же запрос сток отдавал ТОТ ЖЕ первый клип. Из 8 роликов выходило
# всего 3 разных начала - Instagram метит такое как дубликат и режет охват.
USED_DB=os.environ.get("USED_DB",os.path.expanduser("~/.ibook_used_clips.json"))
def load_used():
    try: return set(json.load(open(USED_DB)))
    except Exception: return set()
def save_used(used):
    try: json.dump(sorted(used),open(USED_DB,"w"))
    except Exception: pass

def find_clip(q,used):
    for orient in ("portrait","landscape"):
        # берём широкий пул и ПЕРЕМЕШИВАЕМ: иначе всегда достаётся первый результат
        d=api(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=40&orientation={orient}")
        vids=list(d.get("videos",[])); random.shuffle(vids)
        for v in vids:
            if v["id"] in used: continue
            fs=[f for f in v["video_files"] if f.get("height")]
            # берём САМЫЙ ЛЁГКИЙ файл, которого хватает на выход 1080x1920:
            # тянуть UHD 2560x1440 бессмысленно — это втрое больше байт при том же результате
            ok=[f for f in fs if (f["height"] or 0)>=1080]
            cand=sorted(ok,key=lambda f:f["height"]) or sorted(fs,key=lambda f:-(f["height"] or 0))
            if cand:
                used.add(v["id"]); save_used(used)
                return v["id"],cand[0]["link"]
    return None,None
# ── Свой склад кадров. Ищем сцену по описанию из сценария, а не по слепленному
# запросу: именно из-за запроса кадры и не совпадали с текстом. Склад лежит
# локально, поэтому кадр берётся мгновенно и без интернета. Чего на складе нет -
# добираем живым поиском, как раньше.
try:
    import kadry as KADRY
except Exception:
    KADRY=None

def from_sklad(prompt,lang,used,dest):
    """Кадр со склада под эту сцену. Возвращает путь или None."""
    if not (KADRY and prompt): return None
    sc=KADRY.pick_scene(prompt)
    if not sc: return None
    cast=KADRY.LANG_CAST.get(lang,"evropa")
    ix=KADRY.load_index()
    # сначала свой типаж, и только если склад по нему пуст - любой другой:
    # лучше правильная сцена с чужим лицом, чем правильное лицо не в той сцене
    for c in (cast,None):
        # Клипы, помеченные как «грязные» (тёмные, блёклые, статичные), в ролик
        # не пускаем: владелец справедливо сказал, что от дешёвой картинки тошнит.
        pool=[(k,v) for k,v in ix.items()
              if v["scene"]==sc and (c is None or v["cast"]==c)
              and not v.get("grjaz") and k not in used and os.path.exists(v["path"])]
        if not pool: continue
        # свои съёмки вперёд стока: настоящий экран ibook в кадре про запись
        # убедительнее любого стокового клипа
        svoi=[x for x in pool if x[1].get("svoi")]
        k,v=random.choice(svoi or pool)
        # помечаем обеими записями: склад хранит id строкой, живой поиск - числом,
        # иначе один и тот же клип мог прийти дважды из разных источников
        used.add(k)
        try: used.add(int(k))
        except ValueError: pass
        save_used(used)
        shutil.copyfile(v["path"],dest)
        print(f"      склад: {sc}/{v['cast']} {v['sec']}s",flush=True)
        return dest
    return None

# Рисованный кадр. Включается через RISUNKI=1. Рисуется строго по описанию из
# сценария, поэтому совпадает точно - в отличие от стока, который даёт «похожее».
# Считается полторы минуты за кадр, поэтому уже нарисованное берётся мгновенно,
# а рисовать весь год лучше отдельным прогоном заранее.
try:
    import risunok as RIS
except Exception:
    RIS=None

def from_kadra(i,lang,dest,sec):
    """Готовая картинка кадра, нарисованная и утверждённая заранее.

    Файл называется "<неделя><слот>-<номер>-<типаж>.png" в папке KADRY.
    Картинке задаётся движение камеры - наезд, отъезд или проезд, - и из
    неподвижного кадра получается план на несколько секунд.
    """
    d=os.environ.get("KADRY","")
    if not d or not os.path.isdir(d): return None
    cast="az" if lang in ("kk","ru","uz","tr") else ("zh" if lang=="zh" else
          ("slav" if lang in ("rf","uk") else "eu"))
    if not RIS: return None
    # Все свои кадры этого ролика. Если планов в ролике больше, чем картинок,
    # берём картинки по кругу, но КАЖДЫЙ раз другой крупностью и другим движением.
    # Иначе движок добирал недостающее живым стоком - и половина ролика уходила
    # в чужие клипы не по теме, ровно та беда, от которой мы и уходим.
    pool=[]
    for c in (cast,"az","eu"):
        pool=sorted(glob.glob(os.path.join(d,f"{WEEK}{SLOT}-*-{c}.png")))
        if pool: break
    if not pool: return None
    PLAN=["wide","medium","close"]
    MOVE=["in","out","left","right"]
    p=pool[i%len(pool)]
    out=RIS.ozhivit(p,dest,max(2.0,sec+0.6),
                    move=MOVE[i%len(MOVE)],plan=PLAN[(i//len(pool))%len(PLAN)])
    if out:
        print(f"      кадр: {os.path.basename(p)} · {PLAN[(i//len(pool))%len(PLAN)]}",flush=True)
        return out
    return None

def rastyanut(src,dst,nado):
    """Растягиваем короткий клип на нужную длину «туда-обратно».

    Купленный клип идёт 4 секунды, а сцена в сценарии держится до десяти.
    Замедлять втрое нельзя - видно рывки. Поэтому склеиваем клип с ним же
    задом наперёд: движение уходит и возвращается, шва не видно, и так можно
    закрыть любую длину.
    """
    d=dur(src)
    if d<=0: return None
    if d>=nado-0.05:
        ff(["-i",src,"-t",f"{nado:.2f}","-c","copy",dst]); return dst
    n=int(nado/d)+2
    ff(["-i",src,"-filter_complex",
        f"[0:v]split=2[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[v];"
        f"[v]loop=loop={n}:size=32767:start=0,setpts=N/FRAME_RATE/TB,trim=0:{nado:.2f}[o]",
        "-map","[o]","-an","-c:v","libx264","-pix_fmt","yuv420p","-crf","18",dst])
    return dst if os.path.exists(dst) else None

def from_gotovyh(i,lang,dest,sec=None):
    """Готовый клип живого видео, посчитанный заранее на серверной карте.

    Имя файла - "<неделя><слот>-<номер кадра>-<типаж>.mp4", ровно как в описаниях
    кадров. Такой клип идёт первым: в нём человек реально двигается, а не камера
    ползёт по фотографии.
    """
    d=os.environ.get("KLIPY","")
    if not d or not os.path.isdir(d): return None
    cast="az" if lang in ("kk","ru","uz","tr") else ("zh" if lang=="zh" else
          ("slav" if lang in ("rf","uk") else "eu"))
    for c in (cast,"az","eu"):
        p=os.path.join(d,f"{WEEK}{SLOT}-{i}-{c}.mp4")
        if os.path.exists(p):
            if sec and dur(p) < sec-0.05:
                if not rastyanut(p,dest,sec+0.4): shutil.copyfile(p,dest)
            else:
                shutil.copyfile(p,dest)
            print(f"      живое видео: {os.path.basename(p)}",flush=True)
            return dest
    return None

def from_risunok(prompt,lang,dest,sec):
    if not (RIS and prompt and os.environ.get("RISUNKI")=="1"): return None
    try:
        png=RIS.draw(prompt,lang)
        if not png: return None
        # статичную картинку ведём движением камеры: наезд, отъезд или проезд
        out=RIS.ozhivit(png,dest,max(2.0,sec+0.6))
        if out: print(f"      рисунок: {os.path.basename(png)}",flush=True)
        return out
    except Exception as e:
        print(f"      рисунок не вышел: {str(e)[:60]}",flush=True); return None

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
        if engine=="piper":
            # Piper: отдельные модели под язык. Украинского и казахского в
            # мультиязычной базе нет вовсе, а здесь они читают по-настоящему,
            # своей фонетикой. Считает почти мгновенно - секунды против десяти минут.
            # vid = "<файл модели>:<номер диктора>", номер необязателен.
            py=os.environ.get("UK_PY",os.path.expanduser("~/uk-tts/.venv/bin/python"))
            name,_,spk=vid.partition(":")
            mdl=os.path.expanduser(f"~/uk-tts/{name}.onnx")
            if not os.path.exists(mdl): raise RuntimeError(f"нет голоса: {mdl}")
            wav=mp3+".piper.wav"
            # Подача. length-scale чуть ниже единицы - живее, но без спешки:
            # тараторящий голос слушать неудобно и он сразу выдаёт синтез.
            # sentence-silence - вдох между предложениями, без него речь идёт
            # сплошным потоком и звучит механически.
            # Пауза после предложения - 0.12, а не 0.35. В сценарии двенадцать
            # коротких фраз, и по трети секунды на каждую давали почти пять секунд
            # мёртвого воздуха: ролик слушался рвано.
            # noise-w и noise-scale - разброс длительности звуков и тембра. По
            # умолчанию они на «ровно», из-за чего голос читал как диктор новостей.
            # ОДИН проход на весь текст. Раньше резали на фразы и склеивали -
            # так задумывалась живая интонация, но на склейках речь стала звучать
            # с запинками: каждый стык слышен. Модель сама держит связь между
            # предложениями, если дать ей текст целиком.
            cmd=[py,"-m","piper","-m",mdl,"-f",wav,
                 "--length-scale",os.environ.get("TTS_RATE","0.96"),
                 "--noise-scale",os.environ.get("TTS_NOISE","0.667"),
                 "--noise-w-scale",os.environ.get("TTS_NOISEW","0.8"),
                 "--sentence-silence",os.environ.get("TTS_PAUSE","0.14")]
            if spk: cmd+=["--speaker",spk]
            r=subprocess.run(cmd,input=text,capture_output=True,text=True)
            if not os.path.exists(wav):
                raise RuntimeError(f"piper не отдал звук: {(r.stdout+r.stderr)[-300:]}")
            # Обработка только звуковая: свист на «с» вниз, верх чуть вверх,
            # динамику поджать и вывести на громкость ленты.
            ff(["-i",wav,"-ar","44100",
                "-af","deesser=i=0.4:m=0.5:f=0.5,highshelf=g=2.5:f=5500,"
                      "acompressor=threshold=-24dB:ratio=5:attack=5:release=120:makeup=5,"
                      "loudnorm=I=-10:TP=-1.0:LRA=6,volume=4dB,"
                      "alimiter=limit=0.85:level=disabled",
                "-q:a","2",mp3])
            return [None,None]
        if engine=="chatterbox":
            # Узбекский: локальная модель (MIT), бесплатно и без лимитов.
            # Живёт в своём venv со своими зависимостями, поэтому зовём подпроцессом.
            # Подача задаётся снаружи: по умолчанию ЭНЕРГИЧНАЯ, ровное чтение
            # в ленте не работает.
            py=os.environ.get("UZ_PY",os.path.expanduser("~/uz-tts/.venv/bin/python"))
            scr=os.environ.get("UZ_SCRIPT",os.path.expanduser("~/uz-tts/uz_tts.py"))
            if not os.path.exists(py): raise RuntimeError(f"нет узбекской модели: {py}")
            wav=mp3+".chb.wav"
            env=dict(os.environ)
            # Продающая подача, а не дикторское чтение: больше эмоции в голосе,
            # свободнее темп. Ровный тон в ленте пролистывают за секунду.
            env.setdefault("EXAG","0.85"); env.setdefault("CFG","0.25"); env.setdefault("TEMP","0.85")
            env.setdefault("TMPDIR","/Volumes/T7/ibook/tmp" if os.path.isdir("/Volumes/T7/ibook") else "/tmp")
            # ГОЛОС ОБЯЗАТЕЛЕН: без образца модель берёт стандартный голос базовой
            # версии, а не узбекского диктора, на котором её обучали. Именно поэтому
            # первые пробы звучали хуже демо-образцов автора.
            # Образец голоса: узбекскому - его обученный диктор, остальным языкам -
            # вырезанный из прошлых роликов голос владельца. Так бренд звучит одинаково.
            # Голос чередуем между роликами, как в других языках: женский и мужской.
            # Один голос на 156 роликов подряд утомляет и звучит как автоответчик.
            _g="/Volumes/T7/ibook/golosa"
            _own=random.choice([f"{_g}/laura-zhenskiy.wav",f"{_g}/bala-muzhskoy.wav"])
            _def=os.path.expanduser("~/uz-tts/reference_voice.wav") if vid=="uz" else _own
            ref=os.environ.get("UZ_REF",_def)
            if not os.path.exists(ref): ref=os.path.expanduser("~/uz-tts/reference_voice.wav")
            cmd=[py,scr,text,wav]+([ref] if os.path.exists(ref) else [])
            # у мультиязычной базы свой код языка; узбекского в ней нет,
            # для него берём турецкий как ближайшую тюркскую фонетику
            _CB={"ru":"ru","rf":"ru","uk":"ru","tr":"tr","zh":"zh","en":"en",
                 "de":"de","it":"it","es":"es","fr":"fr","uz":"tr"}
            env["UZ_LANG_ID"]=_CB.get(vid,"en")
            # Узбекские дообученные веса ставим ТОЛЬКО узбекскому: турецкий идёт
            # с тем же кодом языка, и без этой отметки получал бы чужое произношение.
            # Всем остальным - свежая база v3, там меньше бормотания.
            env["UZ_FINETUNE"]="1" if vid=="uz" else "0"
            env.setdefault("V3","0" if vid=="uz" else "1")
            r=subprocess.run(cmd,env=env,capture_output=True,text=True)
            if not os.path.exists(wav):
                raise RuntimeError(f"chatterbox не отдал звук: {(r.stdout+r.stderr)[-300:]}")
            # Сырой выход модели: 24 кГц и пики в 0 дБ (клиппинг -> хрип на громких слогах).
            # Поднимаем частоту, выравниваем громкость с запасом и слегка добавляем
            # верх - вернуть утраченные выше 12 кГц нельзя, но разборчивость поднимается.
            # Локальная модель читает медленнее платной: сценарий на 30 секунд вышел
            # на 41. Подтягиваем темп прямо при сведении - дешевле переозвучки и
            # заодно даёт ту скорость подачи, без которой ролик в ленте не смотрят.
            _d=dur(wav)
            _t=1.0 if _d<34 else min(1.2,round(_d/32.0,2))   # выше 1.2 речь уже частит
            if _t>1.0: print(f"   локальный голос {round(_d,1)}s -> темп {_t}",flush=True)
            # Порядок фильтров важен: подъём верха ПОСЛЕ выравнивания снова
            # загонял пики под самый ноль - тот же хрип, ради которого всё и делалось.
            # Сначала тембр, потом громкость, и предохранитель последним.
            ff(["-i",wav,"-ar","44100",
                "-af","highshelf=g=3:f=6000,"
                      +(f"atempo={_t}," if _t>1.0 else "")
                      +"loudnorm=I=-11:TP=-1.0:LRA=7,alimiter=limit=0.9",
                "-q:a","2",mp3])
            return [None,None]
        if engine=="eleven":  # ElevenLabs (человеческий голос, вкл. казахский) — нужен env EL_KEY
            key=os.environ["EL_KEY"]
            model=os.environ.get("EL_MODEL","eleven_v3")
            body=json.dumps({"text":text,"model_id":model,
                "voice_settings":{"stability":float(os.environ.get("EL_STAB","0.28")),"similarity_boost":0.85,"speed":float(os.environ.get("EL_SPEED","1.0")),"use_speaker_boost":True}}).encode()
            # Ретраи обязательны: один таймаут ElevenLabs раньше вешал весь ролик
            # (и висел десятками минут, потому что попытка была единственной).
            last=None
            for a in range(3):
                try:
                    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
                        data=body,headers={"xi-api-key":key,"Content-Type":"application/json","Accept":"audio/mpeg"})
                    with urllib.request.urlopen(req,timeout=120) as r: audio=r.read()
                    if len(audio)<2000: raise RuntimeError(f"подозрительно короткий ответ: {len(audio)} б")
                    tmp=mp3+".part"
                    with open(tmp,"wb") as f: f.write(audio)
                    os.replace(tmp,mp3)
                    return [None,None]
                except Exception as e:
                    last=e; print(f"   ! ElevenLabs {a+1}/3: {e}",flush=True); time.sleep(3*(a+1))
            raise RuntimeError(f"ElevenLabs не ответил после 3 попыток: {last}")
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

    def cta_png(text,path):
        """Финишная плашка: где скачать приложение. Печатаем Pillow - ffmpeg здесь без drawtext."""
        img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
        f=font(72); tw=d.textlength(text,font=f); y=1500
        d.rounded_rectangle([(W-tw)//2-56,y-34,(W+tw)//2+56,y+112],radius=60,fill=(88,16,232,238))
        d.text(((W-tw)//2,y),text,font=f,fill=(255,255,255,255))
        f2=font(40); s2="App Store · Google Play"; w2=d.textlength(s2,font=f2)
        d.text(((W-w2)//2,y+130),s2,font=f2,fill=(255,255,255,235),
               stroke_width=5,stroke_fill=(0,0,0,255))
        img.save(path)

    def render_year(lang,cfg):
        """30-секундный ролик по готовому сценарию из годового плана."""
        card=year_card(lang)
        ov=os.environ.get(f"VOICE_{lang.upper()}")
        if ov and ":" in ov: engine,vid=ov.split(":",1)
        else: engine,vid=random.choice(VOICES.get(lang,VOICES["ru"]))
        print(f"=== {lang} {WEEK}{SLOT} '{card['title']}' | {engine} {vid} ===",flush=True)
        # Озвучка ровно как в сценарии. Фразу про App Store и «ссылку в шапке» НЕ дописываем:
        # оплата идёт внутри приложения через Apple Pay / Google Pay, лишний призыв только мешает.
        # Короткая версия по умолчанию: сорок секунд в ленте не досматривают,
        # а алгоритм смотрит именно на досмотр. Строение - боль, во что обходится,
        # решение, предложение. Длинную версию вернуть: KOROTKO=0
        if os.environ.get("KOROTKO","1")=="1":
            import korotko
            text=korotko.korotkiy(card,lang,cta_line(lang,card.get("aud","master")))
            tail=""
        else:
            text=card["vo"].strip()
            tail=cta_line(lang,card.get("aud","master"))
        if tail and "App Store" not in text and "主页" not in text:
            text=f"{text} {tail}"
        hk=(card.get("hook") or "").strip().rstrip(".!?")
        if hk and hk.split()[0].lower() not in text[:70].lower():
            text=f"{hk}! {text}"        # крючок в первые секунды, восклицанием - для напора
        vo=f"{WORK}/{lang}_vo.mp3"
        # Готовая озвучка, если она уже есть. Казахские дорожки вытащены из
        # роликов прошлых месяцев: голос там оплаченный, ElevenLabs, и владельцу
        # он нравится. Платить и считать заново незачем.
        _g=os.environ.get("GOLOS","")
        _gp=os.path.join(_g,f"{NUM:03d}-{lang}.mp3") if _g else ""
        if _gp and os.path.exists(_gp):
            shutil.copyfile(_gp,vo)
            print(f"   готовая озвучка: {os.path.basename(_gp)}",flush=True)
        else:
            gen_voice(engine,vid,phon(text,lang),cfg["rate"],vo)
        VD=dur(vo)
        if VD<3: raise RuntimeError(f"{lang}: озвучка пустая ({VD}s)")
        # Бесплатные голоса читают медленнее платных: турецкий и узбекский вылезали
        # на 38 секунд вместо 30. Ускоряем и переозвучиваем, формат важнее.
        # Голос НЕ разгоняем ради формата: разогнанная речь сразу слышится
        # неестественной. Reels допускает до 90 секунд, так что 35-40 - нормально.
        # Вмешиваемся только если ролик совсем расплылся.
        # У локального движка переозвучка теми же параметрами ничего не меняет -
        # только удваивает и без того долгий счёт. Темп там подтягивается при
        # сведении, внутри gen_voice.
        if VD>60 and engine!="chatterbox":
            if engine=="edge":
                extra=min(40,int((VD/30.0-1)*100)+5)
                print(f"   озвучка {round(VD,1)}s -> ускоряю на +{extra}%",flush=True)
                gen_voice(engine,vid,phon(text,lang),f"+{extra}%",vo)
            else:
                # у ElevenLabs темп задаётся не строкой rate, а полем speed (макс. 1.2).
                # Китайский клон читает медленно и вылезал на 35 секунд.
                sp=min(1.15,round(VD/45.0,2))
                print(f"   озвучка {round(VD,1)}s -> темп {sp}",flush=True)
                os.environ["EL_SPEED"]=str(sp)
                gen_voice(engine,vid,phon(text,lang),cfg["rate"],vo)
                os.environ.pop("EL_SPEED",None)
            VD=dur(vo)
        print(f"   озвучка {round(VD,1)}s ({len(text.split())} слов)",flush=True)
        # кадры: длительности по таймингам сценария, растянутые под реальную озвучку
        qs=shot_queries(card,lang); sp=spans_of(card)
        # Крючок: короткий крупный план в самом начале + быстрая склейка вместо
        # одного долгого открывающего кадра. Так ролик цепляет с первой секунды.
        # Искусственный крючок в начале нужен ТОЛЬКО стоку: там первый кадр
        # случайный, и его надо чем-то перебить. Когда планы свои, первая сцена
        # сценария и ЕСТЬ крючок - она написана под первые секунды.
        # Раньше лишний план сдвигал всю нумерацию, и ролик открывался ПОСЛЕДНИМ
        # кадром - той самой улыбкой в камеру, которая должна быть в финале.
        SVOI=bool(os.environ.get("KLIPY") or os.environ.get("KADRY"))
        pr=[sh.get("prompt","") for sh in card["shots"]]
        if not SVOI:
            hq=(PEOPLE.get(lang,"")+" "+random.choice(HOOK_Q)).strip()
            h=min(2.0,sp[0]*0.55)
            qs=[hq]+qs; sp=[h,max(1.2,sp[0]-h)]+sp[1:]
            pr=[""]+pr
        k=(VD+0.4)/sum(sp); sp=[x*k for x in sp]
        clips=[]; keep=[]; avail=[]
        for i,(q,d_i) in enumerate(zip(qs,sp)):
            print(f"   [{i}] {round(d_i,1)}s '{q}'",flush=True)
            cp=f"{WORK}/{lang}_y{i}.mp4"
            _p=pr[i] if i<len(pr) else ""
            # порядок источников: живое видео -> рисунок -> склад -> живой сток
            j=i if SVOI else i-1        # без крючка нумерация идёт один в один
            # Порядок источников подчинён деньгам владельца: их немного и больше
            # не будет. Сначала всё бесплатное - уже купленные клипы, потом склад
            # живого стока. Платим только за те сцены, которых бесплатно нет.
            if (not from_gotovyh(j,lang,cp,d_i)
                    and not from_sklad(_p,lang,used,cp)
                    and not from_kadra(j,lang,cp,d_i)
                    and not from_risunok(_p,lang,cp,d_i)):
                cid,link=find_clip(q,used)
                if not link: print("      ! нет клипа"); continue
                if not download(link,cp): continue
            real=dur(cp)-0.35            # 0.3 съедает обрезка начала
            if real<0.8: print("      ! клип слишком короткий"); continue
            clips.append(cp); keep.append(d_i); avail.append(real)
            print(f"      материала {round(real,1)}s",flush=True)
        if len(clips)<3: raise RuntimeError(f"{lang}: кадров всего {len(clips)}")
        # длительности пересчитываем на реально скачанные кадры, чтобы видео не оборвалось
        # Переходы: наплыв (xfade), а не затухание в чёрное. Раньше каждый кадр
        # гаснул и появлялся из черноты - между планами мигала чернота, ролик
        # выглядел слайдшоу. Наплыв склеивает планы незаметно, как в живом монтаже.
        XF=0.25
        SLOW=1.6                        # мягкое замедление - предел, дальше видно рывки
        # если материала не хватает на всю озвучку, добираем ещё кадров, а не тянем
        # имеющиеся до бесконечности
        # Если сцены свои, добор не нужен: каждый план уже растянут под свой
        # кусок сценария. Добор дублировал сцены в конце - зритель видел финал
        # дважды, а история ломалась.
        guard=0
        while (not SVOI) and sum(a*SLOW for a in avail) < VD+0.4+(len(clips)-1)*XF and guard<6:
            guard+=1
            cp=f"{WORK}/{lang}_x{guard}.mp4"
            # доборы тоже берём из СВОИХ кадров: раньше они уходили в сток,
            # и в конце ролика вылезала чужая рука на фоне двери
            if (not from_kadra(len(clips),lang,cp,3.2)
                    and not from_sklad(pr[guard%len(pr)],lang,used,cp)):
                cid,link=find_clip(qs[guard%len(qs)],used)
                if not link: break
                if not download(link,cp): continue
            real=dur(cp)-0.35
            if real<0.8: continue
            clips.append(cp); keep.append(sum(keep)/len(keep)); avail.append(real)
            print(f"      + добрал кадр, материала не хватало ({round(real,1)}s)",flush=True)
        # Дробим длинные планы: кадр дольше 3.5 секунд в ленте усыпляет.
        # Берём ещё клипы и режем чаще - ритм важнее, чем длина каждого плана.
        # Если планы у нас СВОИ (куплены или нарисованы), дробить их нельзя:
        # каждый кадр стоит на своём месте по таймингу сценария, и лишние
        # склейки рвут связь картинки с озвучкой - зритель слышит одно, видит
        # другое. Дробление придумано для стока, где кадр случайный.
        MAXSHOT=float(os.environ.get("MAXSHOT","3.5"))
        if os.environ.get("KLIPY") or os.environ.get("KADRY"):
            MAXSHOT=99.0
        want=int((VD+0.4)/MAXSHOT)+1
        guard2=0
        while (not SVOI) and len(clips)<want and guard2<8:
            guard2+=1
            cp=f"{WORK}/{lang}_m{guard2}.mp4"
            # доборы тоже берём из СВОИХ кадров: раньше они уходили в сток,
            # и в конце ролика вылезала чужая рука на фоне двери
            if (not from_kadra(len(clips),lang,cp,3.2)
                    and not from_sklad(pr[guard2%len(pr)],lang,used,cp)):
                cid,link=find_clip(qs[guard2%len(qs)],used)
                if not link: break
                if not download(link,cp): continue
            real=dur(cp)-0.35
            if real<0.8: continue
            clips.append(cp); keep.append(sum(keep)/len(keep)); avail.append(real)
        print(f"   планов в ролике: {len(clips)} (в среднем {round((VD+0.4)/len(clips),1)}s на кадр)",flush=True)
        n=len(clips)
        need=VD+0.4+(n-1)*XF
        keep=fit_durations(keep,[a*SLOW for a in avail],need)
        # где кадр короче отведённого времени - мягко замедляем, а не морозим
        slow=[max(1.0,round(keep[i]/avail[i],3)) if avail[i]>0 else 1.0 for i in range(n)]
        TOTAL=sum(keep)-(n-1)*XF
        mus=MUSIC if (MUSIC and os.path.exists(MUSIC)) else None
        aud=f"{WORK}/{lang}_ya.m4a"
        if mus:
            ff(["-i",vo,"-i",mus,"-filter_complex",
                "[1]volume=0.34[m];[0]asplit=2[v1][v2];"
                "[m][v1]sidechaincompress=threshold=0.05:ratio=8:attack=5:release=250[md];"
                "[v2][md]amix=inputs=2:normalize=0:duration=first,"
                +LOUD+"[a]",
                "-map","[a]","-t",f"{TOTAL:.2f}",aud])
        else:
            ff(["-i",vo,"-af",LOUD,"-t",f"{TOTAL:.2f}",aud])
        inputs=[]
        for cp in clips: inputs+=["-i",cp]
        inputs+=["-i",aud]
        AI=len(clips)
        if CTA_CARD:
            cta=f"{WORK}/{lang}_cta.png"; cta_png(STORE_CARD.get(lang,STORE_CARD["en"]),cta)
            inputs+=["-i",cta]
        CI=AI+1; fd=0.3; parts=[]
        for i,d_i in enumerate(keep):
            src=d_i/slow[i]          # сколько секунд берём из исходника
            st=f"setpts={slow[i]}*PTS," if slow[i]>1.01 else ""
            parts.append(f"[{i}:v]trim=0.3:{0.3+src:.3f},setpts=PTS-STARTPTS,{st}"
                f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,"
                f"format=yuv420p,setsar=1[v{i}]")
        tag="[vc]" if CTA_CARD else "[v]"
        if n==1:
            parts.append(f"[v0]null{tag}")
        else:
            prev="[v0]"; acc=keep[0]
            for i in range(1,n):
                off=acc-XF
                out=f"[x{i}]" if i<n-1 else "[xf]"
                parts.append(f"{prev}[v{i}]xfade=transition=fade:duration={XF}:offset={off:.3f}{out}")
                prev=out; acc=acc+keep[i]-XF
            # мягкий вход и выход всего ролика, внутри - только наплывы
            parts.append(f"[xf]fade=t=in:st=0:d=0.3,fade=t=out:st={max(0,TOTAL-0.4):.2f}:d=0.4{tag}")
        if CTA_CARD:   # плашка «скачай» держится последние 4 секунды
            parts.append(f"[vc][{CI}:v]overlay=0:0:enable='between(t,{max(0,TOTAL-4):.2f},{TOTAL:.2f})'[v]")
        open(f"{WORK}/{lang}_yfg.txt","w").write(";".join(parts))
        ff([*inputs,"-filter_complex_script",f"{WORK}/{lang}_yfg.txt","-map","[v]","-map",f"{AI}:a",
            "-r","30","-t",f"{TOTAL:.2f}",*REELS_ENC,cfg["out"]])
        print(f"DONE [{lang}] {cfg['out']} {round(TOTAL,1)}s",flush=True)

    # своя случайность на каждый ролик + память между запусками
    random.seed(f"{PROJECT}-{WEEK}-{SLOT}-{time.time()}")
    used=load_used()
    print(f"   в памяти уже использовано клипов: {len(used)}",flush=True)
    for lang,cfg in LANGS.items():
        if SOURCE=="year":
            try: render_year(lang,cfg)
            except Exception as e: print(f"ERR {lang}: {e}",flush=True)
            continue
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
            print(f"   {round(D[-1],2)}s",flush=True)
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
            "[1]volume=0.34[m];[0]asplit=2[v1][v2];"
                "[m][v1]sidechaincompress=threshold=0.05:ratio=8:attack=5:release=250[md];"
                "[v2][md]amix=inputs=2:normalize=0:duration=first,"
                +LOUD+"[a]",
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
                "-r","30","-t",f"{TOTAL:.2f}",*REELS_ENC,cfg["out"]])
            print(f"DONE [{lang}] {cfg['out']} dur {round(TOTAL,2)} (video+voice+music)",flush=True)
        except RuntimeError as e:
            print(f"ERR {lang}\n{e}")

if __name__=="__main__": main()
