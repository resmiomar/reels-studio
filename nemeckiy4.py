#!/usr/bin/env python3
"""Немецкий год, последняя партия: ноябрь и декабрь. Правила те же."""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scenarii")

TEKST = {
"44A": ("Wer im Dezember voll sein will, öffnet im November. Im Dezember ist es zu spät, "
        "da suchen die Kundinnen schon bei anderen. "
        "Öffne deine Feiertagstermine jetzt in ibook, und sie tragen sich selbst ein. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Wer im Dezember voll sein will, öffnet im November. Feiertagstermine früh in ibook "
        "öffnen, und deine Kundinnen tragen sich selbst ein."),
"44B": ("Die Termine vor den Feiertagen sind früher weg, als du denkst, oft schon im November. "
        "Wer im Dezember sucht, nimmt Reste. "
        "In ibook siehst du jetzt, wer an deinem Wunschtag noch frei ist, "
        "und buchst in 3 Berührungen. Erinnerung kommt automatisch.",
        "Feiertagstermine sind schon im November weg. In ibook siehst du sofort, wer an deinem "
        "Tag noch frei ist, und buchst in drei Berührungen."),
"44C": ("Feiertage zu öffnen klingt nach Planung, dauert aber eine halbe Minute. "
        "Geh in ibook in den Kalender, markier die Tage vor den Feiertagen als arbeitsfrei "
        "oder buchbar, fertig. 30 Sekunden, und der Dezember beginnt sich zu füllen. "
        "30 Tage kostenlos.",
        "Feiertage öffnen dauert dreißig Sekunden: Kalender auf, Tage markieren, fertig. Danach "
        "füllt sich der Dezember in ibook von selbst."),
"45A": ("Der Dezember entscheidet sich im November, und wer erst am ersten öffnet, hat die "
        "besten Kundinnen schon verloren. "
        "Öffne in ibook jetzt die Dezembertermine, alle auf einmal. "
        "10 Minuten Arbeit, und der stärkste Monat des Jahres füllt sich von allein.",
        "Der Dezember entscheidet sich im November. Dezembertermine jetzt in ibook öffnen, und "
        "der stärkste Monat füllt sich von allein."),
"45B": ("Im Dezember arbeitet der Salon am Limit, und wenn der Plan erst am ersten steht, "
        "wird der ganze Monat zum Chaos. "
        "Setzt den Dezemberplan in ibook jetzt: Zeiten, Schichten, Feiertage. "
        "1 Abend Planung spart euch 4 Wochen Stress. 30 Tage kostenlos.",
        "Im Dezember arbeitet der Salon am Limit. Setzt den Plan jetzt in ibook: Zeiten, "
        "Schichten, Feiertage. Ein Abend spart vier Wochen Stress."),
"45C": ("Zum Black Friday machen alle irgendeine Aktion, und im Salon weiß trotzdem niemand, "
        "wer was anbietet. Die Kundin merkt das sofort. "
        "Legt die Aktion in ibook einmal an, für das ganze Team. "
        "1 Angebot, alle Plätze, 30 Tage kostenlos.",
        "Zum Black Friday soll das ganze Team dasselbe anbieten. Aktion in ibook einmal anlegen, "
        "und sie gilt für alle Plätze im Salon."),
"46A": ("Einmal im Jahr lohnt es sich, weiter als bis zum nächsten Monat zu rechnen. "
        "Zum Black Friday bekommst du in ibook das Jahr für den Preis von 10 Monaten. "
        "2 Monate geschenkt, alles andere bleibt gleich: kein Aufpreis, keine Provision. "
        "Vorher 30 Tage kostenlos testen.",
        "Zum Black Friday: das Jahr zum Preis von zehn Monaten, zwei geschenkt. Keine "
        "Provision, kein Aufpreis. Vorher dreißig Tage kostenlos."),
"46B": ("Rechnen wir es einmal durch, ohne Kleingedrucktes. "
        "Monatlich zahlst du zwölfmal, im Jahrestarif zehnmal für dieselben zwölf Monate. "
        "In ibook ändert sich sonst nichts: gleicher Kalender, gleiches Profil, 0 Provision. "
        "Erst 30 Tage kostenlos, dann entscheiden.",
        "Zwölf Monate für den Preis von zehn. Sonst ändert sich nichts: gleicher Kalender, "
        "gleiches Profil, keine Provision auf deine Leistungen."),
"46C": ("Zwei Monate geschenkt klingt nach Haken, ist aber einfach der Jahrestarif. "
        "Du zahlst 10 Monate und nutzt ibook 12, mit allem, was drin ist: "
        "Kalender, Profil, Erinnerungen, Auswertung. "
        "Ausprobieren kannst du es vorher 30 Tage kostenlos.",
        "Jahrestarif ohne Haken: zehn Monate zahlen, zwölf nutzen, mit Kalender, Profil, "
        "Erinnerungen und Auswertung. Vorher kostenlos testen."),
"47A": ("Eine Kundin, die im Dezember nicht erscheint, kostet dich mehr als im Juli. "
        "Im vollsten Monat ist jede Stunde vergeben, und die Lücke füllst du nicht mehr. "
        "In ibook erinnert die App automatisch, rechtzeitig vorher. "
        "1 verhinderter Ausfall zahlt den ganzen Monat.",
        "Ein Ausfall im Dezember ist teurer als im Juli. Automatische Erinnerungen in ibook "
        "machen genau diese Ausfälle seltener."),
"47B": ("Im Dezember hat man zehn Termine im Kopf und vergisst genau den einen. "
        "Das passiert den Besten. "
        "In ibook kommt die Erinnerung von selbst aufs Handy, rechtzeitig vor dem Termin. "
        "2 Berührungen beim Buchen, und du vergisst ihn nicht mehr.",
        "Im Dezember vergisst man leicht einen Termin. In ibook kommt die Erinnerung "
        "automatisch aufs Handy, rechtzeitig vorher."),
"47C": ("Im Vorweihnachtsansturm sind Ausfälle am teuersten, und genau dann passieren sie "
        "am häufigsten. Alle haben zu viel im Kopf. "
        "Stell in ibook die automatische Erinnerung ein und lass die App bestätigen. "
        "1 Einstellung, spürbar weniger Ausfälle. 30 Tage kostenlos.",
        "Vor Weihnachten sind Ausfälle am teuersten. Automatische Erinnerung und Bestätigung "
        "in ibook einstellen, und sie werden spürbar seltener."),
"48A": ("Im Dezember arbeitet das ganze Team am Anschlag, und trotzdem hat eine Leerlauf, "
        "während die andere nicht hinterherkommt. "
        "In ibook siehst du die Auslastung aller live und verteilst um, solange es noch geht. "
        "1 Bildschirm, 30 Tage kostenlos.",
        "Im Dezember hat eine Leerlauf, während die andere überrannt wird. In ibook siehst du "
        "die Auslastung aller live und verteilst um."),
"48B": ("Deine Freundin sucht seit Wochen jemanden und du hast längst deine Person gefunden. "
        "Schick ihr einfach den Link. "
        "In ibook sieht sie die Arbeiten, die Preise und die freien Zeiten und bucht selbst. "
        "3 Berührungen, und ihr geht zusammen hin.",
        "Schick deiner Freundin den Link zu deiner Person. In ibook sieht sie Arbeiten, Preise "
        "und freie Zeiten und bucht in drei Berührungen."),
"48C": ("Im Dezembertrubel scheint alles ausgebucht, aber Lücken gibt es immer, "
        "nur findet man sie nicht per Telefon. "
        "In ibook siehst du alle freien Zeiten auf einmal, auch die frühen und späten. "
        "3 Berührungen, und du hast deinen Termin.",
        "Im Dezember scheint alles voll, aber Lücken gibt es immer. In ibook siehst du sie alle "
        "auf einmal, auch früh und spät."),
"49A": ("Der Dezember ist der dichteste Monat des Jahres, und genau dann bricht das Chaos aus: "
        "Anrufe, Nachrichten, Verschiebungen. "
        "In ibook läuft das ohne dich: Kundinnen buchen selbst, verschieben selbst, "
        "und die App erinnert sie. 30 Tage kostenlos, jederzeit kündbar.",
        "Der Dezember ist der dichteste Monat. In ibook buchen und verschieben deine Kundinnen "
        "selbst, und die App erinnert sie rechtzeitig."),
"49B": ("Die letzten Termine vor den Feiertagen sind in ein paar Tagen weg, "
        "und danach bleibt nur der 27. um acht Uhr morgens. "
        "In ibook siehst du sofort, wo noch etwas frei ist, und buchst in 3 Berührungen. "
        "Erinnerung kommt automatisch.",
        "Die letzten Termine vor den Feiertagen sind schnell weg. In ibook siehst du sofort, "
        "wo noch etwas frei ist, und buchst in drei Berührungen."),
"49C": ("Ein ruhiger Dezember ist kein Glück, sondern drei Einstellungen. "
        "Termine früh öffnen, echte Dauer je Leistung eintragen, automatische Erinnerung an. "
        "3 Einstellungen in ibook, 10 Minuten Arbeit, und der Monat läuft ohne Chaos. "
        "30 Tage kostenlos.",
        "Ruhiger Dezember in drei Einstellungen: Termine früh öffnen, echte Dauer eintragen, "
        "Erinnerungen anschalten. Zehn Minuten in ibook."),
"50A": ("In der Weihnachtsfeiersaison wollen alle abends, und zwar spät. "
        "Wenn deine Abendzeiten nicht offen sind, gehen diese Kundinnen woanders hin. "
        "Öffne in ibook ein paar späte Termine, sie sind in Stunden vergeben. "
        "2 Handgriffe, 30 Tage kostenlos.",
        "In der Feiersaison wollen alle spät abends. Öffne ein paar späte Termine in ibook, "
        "sie sind in Stunden vergeben."),
"50B": ("Zwischen den Feiertagen arbeitet der Salon am Limit, und ein Fehler im Plan kostet "
        "sofort einen ganzen Abend. "
        "In ibook liegt der Plan des ganzen Teams auf einem Bildschirm, live, mit jeder Lücke. "
        "1 Blick statt 5 Anrufe. 30 Tage kostenlos.",
        "Zwischen den Feiertagen kostet jeder Planfehler einen Abend. In ibook liegt der Plan "
        "des ganzen Teams live auf einem Bildschirm."),
"50C": ("Der Abendstrom vor den Feiertagen ist die beste Zeit des Jahres, "
        "und die meisten Salons verschenken sie, weil abends niemand ans Telefon geht. "
        "In ibook buchen die Kundinnen selbst, auch um zehn Uhr abends. "
        "24 Stunden buchbar, 30 Tage kostenlos.",
        "Der Abendstrom vor den Feiertagen ist die beste Zeit des Jahres. In ibook buchen "
        "Kundinnen selbst, auch spät abends."),
"51A": ("Am Jahresende weiß kaum jemand, wie viele Termine er eigentlich hatte. "
        "Und ohne Zahl kann man nichts besser machen. "
        "In ibook steht das ganze Jahr auf einem Bildschirm: Termine, Auslastung, Leistungen. "
        "1 Blick, und du weißt, wo dein nächstes Jahr wächst.",
        "Am Jahresende zeigt ibook das ganze Jahr auf einem Bildschirm: Termine, Auslastung, "
        "gefragte Leistungen. Ohne Zahlen kein Wachstum."),
"51B": ("Das neue Jahr fängt man am besten mit etwas an, das nichts kostet, "
        "solange man noch nicht weiß, ob es passt. "
        "Leg dein Profil in ibook jetzt an und starte im Januar mit 30 kostenlosen Tagen. "
        "Passt es nicht, hörst du auf und hast nichts verloren.",
        "Ins neue Jahr mit dreißig kostenlosen Tagen starten. Profil jetzt in ibook anlegen, "
        "im Januar loslegen, ohne Karte und ohne Risiko."),
"51C": ("Wenn das Jahr im Notizbuch steht, gibt es keine Bilanz, nur ein Gefühl. "
        "Und Gefühl täuscht fast immer. "
        "In ibook rechnet die App das Jahr selbst zusammen: Termine, Monate, Leistungen. "
        "2 Berührungen, und du siehst dein Jahr wirklich. 30 Tage kostenlos.",
        "Im Notizbuch gibt es keine Bilanz, nur ein Gefühl. In ibook rechnet die App das Jahr "
        "selbst zusammen: Termine, Monate, Leistungen."),
"52A": ("Für die Feiertage willst du gut aussehen, und heute ist der letzte Moment, "
        "an dem überhaupt noch etwas frei ist. "
        "In ibook siehst du sofort, wer heute und morgen noch Zeit hat, "
        "mit Arbeiten und Bewertungen. 3 Berührungen, und der Abend ist gerettet.",
        "Heute ist der letzte Moment für einen Feiertagstermin. In ibook siehst du sofort, wer "
        "noch Zeit hat, und buchst in drei Berührungen."),
"52B": ("Neues Jahr, neuer Kalender, und diesmal ohne Notizbuch. "
        "Leg dein Profil in ibook an, trag Leistungen und Preise ein und öffne den Januar. "
        "30 Tage kostenlos, ohne Karte, jederzeit kündbar. "
        "Wenn es nicht passt, hörst du einfach auf.",
        "Neues Jahr, neuer Kalender, ohne Notizbuch. Profil anlegen, Leistungen eintragen, "
        "Januar öffnen. Dreißig Tage kostenlos, ohne Karte."),
"52C": ("Im Januar sind die guten Zeiten in der ersten Woche weg, "
        "und dann wartest du bis Februar. "
        "Sichere dir deinen Januartermin jetzt: in ibook freie Zeit ansehen und buchen. "
        "2 Berührungen, und das neue Jahr fängt richtig an.",
        "Im Januar sind gute Zeiten in der ersten Woche weg. Sichere dir den Termin jetzt in "
        "ibook: freie Zeit ansehen, antippen, gebucht."),
}


def main():
    en = json.load(open(os.path.join(SC, "videos_en.json"), encoding="utf-8"))
    de = json.load(open(os.path.join(SC, "videos_de.json"), encoding="utf-8"))
    gotovo = {f"{v['week']}{v['slot']}": v for v in de}
    novyh = 0
    for v in en:
        k = f"{v['week']}{v['slot']}"
        if k not in TEKST:
            continue
        vo, cap = TEKST[k]
        nov = gotovo.get(k) or dict(v)
        if k not in gotovo:
            de.append(nov); novyh += 1
        nov["vo"] = " ".join(vo.split())
        nov["caption"] = " ".join(cap.split())
        nov["hook"] = nov["vo"].split(".")[0].strip() + "."
    de.sort(key=lambda v: (v["week"], v["slot"]))
    json.dump(de, open(os.path.join(SC, "videos_de.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"добавлено: {novyh}, всего немецких: {len(de)}, осталось: {156 - len(de)}")
    bez = [f"{v['week']}{v['slot']}" for v in de
           if "ibook" not in v["vo"] or not any(c.isdigit() for c in v["vo"])]
    print("без ibook или цифры:", bez if bez else "нет, все в порядке")


if __name__ == "__main__":
    main()
