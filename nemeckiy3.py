#!/usr/bin/env python3
"""Немецкий год, вторая партия: лето и осень. Правила те же, что в nemeckiy2."""
import os, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scenarii")
sys.path.insert(0, HERE)

TEKST = {
"18C": ("Hochzeitssaison heißt: lange Termine, viele Rückfragen, und dein Kalender platzt. "
        "Zwei Handgriffe machen es ruhig. "
        "Leg in ibook ein Hochzeitspaket mit fester Dauer an und öffne die Termine früh. "
        "2 Schritte, und die Saison plant sich selbst. 30 Tage kostenlos.",
        "Hochzeitspaket mit fester Dauer anlegen und Termine früh öffnen. Zwei Schritte in "
        "ibook, und die Saison plant sich von allein."),
"19A": ("An Feiertagen weiß im Salon keiner genau, wer arbeitet, und die Kundinnen rufen "
        "trotzdem an. Am Ende steht jemand vor verschlossener Tür. "
        "In ibook trägt jede ihre Feiertage selbst ein, und buchbar ist nur, wer da ist. "
        "1 Plan für alle, 30 Tage kostenlos.",
        "An Feiertagen weiß keiner, wer arbeitet. In ibook trägt jede ihre Tage selbst ein, "
        "und buchbar ist nur, wer wirklich da ist."),
"19B": ("Die besten Buchungen kommen nachts, wenn deine Kundin im Bett liegt und ans Wochenende "
        "denkt. Nur bist du dann nicht erreichbar. "
        "In ibook braucht sie dich nicht: sie sieht freie Zeiten und bucht selbst. "
        "Du schläfst, der Kalender füllt sich. 30 Tage kostenlos.",
        "Die meisten Buchungen kommen abends und nachts. In ibook bucht deine Kundin selbst, "
        "auch um Mitternacht. Du schläfst, der Kalender arbeitet."),
"19C": ("Den Schichtplan machst du jede Woche neu, im Chat, mit zehn Rückfragen. "
        "Das kostet einen halben Abend. "
        "In ibook trägt jede ihre Zeiten selbst ein, und der Plan entsteht von allein. "
        "1 Minute statt 1 Abend. 30 Tage kostenlos.",
        "Schichtplan im Chat kostet jede Woche einen halben Abend. In ibook trägt jede ihre "
        "Zeiten selbst ein, und der Plan steht von allein."),
"20A": ("Hochzeiten werden Monate vorher entschieden, und wer im Mai noch nicht offen ist, "
        "kommt gar nicht erst in die Auswahl. "
        "Öffne in ibook die Termine für den ganzen Sommer, und die Bräute tragen sich selbst ein. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Bräute entscheiden Monate vorher. Öffne in ibook die Sommertermine jetzt, dann tragen "
        "sie sich selbst ein, ohne einen einzigen Anruf."),
"20B": ("Am Hochzeitstag willst du keine Überraschungen, also braucht es einen Probetermin. "
        "Nur denkt man daran meistens zu spät. "
        "In ibook buchst du Probe und Hochzeitstag gleich zusammen, in 3 Berührungen. "
        "Erinnerungen kommen automatisch, an beide Termine.",
        "Probetermin und Hochzeitstag in ibook gleich zusammen buchen. Drei Berührungen, und "
        "die Erinnerungen kommen automatisch."),
"20C": ("Wenn die Dauer nicht stimmt, verschiebt sich der ganze Tag, und die Letzte wartet "
        "eine Stunde. Das merkt sie sich. "
        "Trag in ibook einmal die echte Dauer jeder Leistung ein. "
        "1 Mal einstellen, und der Kalender rechnet für dich. 30 Tage kostenlos.",
        "Stimmt die Dauer nicht, verschiebt sich der ganze Tag. Einmal die echte Dauer je "
        "Leistung in ibook eintragen, und der Kalender rechnet selbst."),
"21A": ("Teuer ist relativ, also rechne es auf den Tag herunter. "
        "Ein Monat in ibook kostet weniger als ein Kaffee pro Arbeitstag. "
        "Dafür bekommst du Kalender, Profil, Erinnerungen und 0 Provision auf deine Leistungen. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Rechne auf den Tag herunter: ein Monat in ibook kostet weniger als ein Kaffee pro "
        "Arbeitstag. Kalender, Profil, Erinnerungen, keine Provision."),
"21B": ("Viele Systeme rechnen pro Mitarbeiterin ab, und je größer dein Team, desto härter "
        "trifft dich die Rechnung. Wachstum wird bestraft. "
        "In ibook zahlt der Salon 1 Preis, egal wie viele im Team sind. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Ein Preis für den ganzen Salon, egal wie viele im Team sind. Wachstum kostet dich in "
        "ibook nicht extra. 30 Tage kostenlos testen."),
"21C": ("Du buchst, und erst am Ende erfährst du, was es kostet. Das mag niemand. "
        "In ibook steht der Preis an jeder Leistung, bevor du auf Buchen tippst. "
        "Keine Überraschungen, keine Nachfragen. 3 Berührungen, und du weißt genau, "
        "was dich erwartet.",
        "In ibook siehst du den Preis vor der Buchung, an jeder Leistung. Keine Überraschung "
        "am Ende, keine unangenehme Nachfrage."),
"22A": ("Rechnen wir ehrlich. Beim Jahrestarif zahlst du 10 Monate und bekommst 12. "
        "Zwei Monate geschenkt, ohne Kleingedrucktes. "
        "Alles andere bleibt gleich: Kalender, Profil, Erinnerungen und 0 Provision in ibook. "
        "Vorher 30 Tage kostenlos testen.",
        "Jahrestarif: zehn Monate zahlen, zwölf nutzen. Zwei Monate geschenkt, alles andere "
        "bleibt gleich. Vorher 30 Tage kostenlos testen."),
"22B": ("Manche fragen, was die App für Kundinnen kostet. Die Antwort ist kurz: nichts. "
        "In ibook suchst, buchst und bewertest du 0 Euro, für immer. "
        "Bezahlt wird nur der Termin selbst, direkt bei der Person, zu der du gehst.",
        "Für Kundinnen ist ibook kostenlos: suchen, buchen, bewerten, alles null Euro. Bezahlt "
        "wird nur der Termin, direkt vor Ort."),
"22C": ("Vor einer Jahreszahlung will man genau wissen, worauf man sich einlässt. Zu Recht. "
        "In ibook zahlst du 10 Monate für 12, kündbar bleibt es trotzdem, "
        "und Provision auf deine Leistungen gibt es nicht. "
        "Erst 30 Tage kostenlos, dann entscheiden.",
        "Jahrestarif ohne Kleingedrucktes: zehn zahlen, zwölf nutzen, keine Provision. Erst "
        "dreißig Tage kostenlos testen, dann entscheiden."),
"23A": ("Die Ballsaison kommt nicht gleichmäßig, sondern in Wellen, und in der Welle verpasst "
        "du die Hälfte der Anfragen. "
        "In ibook buchen sie selbst, auch alle gleichzeitig, und der Kalender sortiert es. "
        "0 verpasste Anfragen, 30 Tage kostenlos.",
        "Die Ballsaison kommt in Wellen. In ibook buchen alle selbst, gleichzeitig, und der "
        "Kalender sortiert die Termine von allein."),
"23B": ("Zum Abiball wollen alle am selben Tag zur selben Zeit, und wer spät dran ist, "
        "bekommt gar nichts mehr. "
        "In ibook siehst du sofort, wo noch etwas frei ist, und buchst in 3 Berührungen. "
        "Erinnerung kommt automatisch, damit der große Tag sitzt.",
        "Zum Abiball wollen alle gleichzeitig. In ibook siehst du sofort freie Zeiten und "
        "buchst in drei Berührungen, ohne Anruf."),
"23C": ("Ein voller Hochzeitstag geht schief, wenn eine Kundin fünfzehn Minuten überzieht. "
        "Dann kippt der ganze Plan. "
        "Trag in ibook echte Dauer und Puffer ein, und der Kalender lässt gar nicht zu, "
        "dass es zu eng wird. 1 Einstellung, ruhiger Tag.",
        "Ein voller Tag kippt an fünfzehn Minuten. Echte Dauer und Puffer in ibook eintragen, "
        "und der Kalender lässt es gar nicht erst zu eng werden."),
"24A": ("Du fährst in den Urlaub und hast Angst, dass die Kundinnen in der Zeit jemand anderen "
        "finden. Meistens passiert genau das. "
        "Trag deine Urlaubstage in ibook ein und öffne die Zeit danach. "
        "So buchen sie dich schon für nach dem Urlaub. 30 Tage kostenlos.",
        "Urlaubstage in ibook eintragen und die Zeit danach öffnen. Dann buchen deine "
        "Kundinnen dich für nach dem Urlaub, statt jemand anderen zu suchen."),
"24B": ("Im Sommer ist immer jemand weg, und der Salonplan wird zum Ratespiel. "
        "Am Ende steht eine Kundin vor der Tür einer Mitarbeiterin, die am Meer liegt. "
        "In ibook trägt jede ihren Urlaub selbst ein, und buchbar ist nur, wer da ist. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Im Sommer ist immer jemand weg. In ibook trägt jede ihren Urlaub selbst ein, und "
        "gebucht werden kann nur, wer wirklich da ist."),
"24C": ("Zwei Wochen Urlaub bedeuten oft vier Wochen leerer Kalender danach, "
        "weil niemand wusste, wann du zurück bist. "
        "Öffne in ibook die Termine nach deinem Urlaub, bevor du fährst. "
        "2 Minuten Arbeit, und die erste Woche zurück ist schon voll.",
        "Öffne die Termine nach dem Urlaub, bevor du fährst. Zwei Minuten in ibook, und die "
        "erste Woche zurück ist bereits gebucht."),
"25A": ("Im Sommer sind deine Abende voll und die Vormittage leer, und das jeden Tag. "
        "Diese Stunden kommen nicht wieder. "
        "Mach in ibook aus einer stillen Stunde ein Angebot, sichtbar für alle in der Nähe. "
        "0 Provision auf deine Leistungen, 30 Tage kostenlos.",
        "Leere Vormittage sind verlorenes Geld. Mach in ibook aus einer stillen Stunde ein "
        "Angebot, sichtbar für alle, die gerade suchen."),
"25B": ("Du hast heute plötzlich Zeit und willst nicht die halbe Stadt abtelefonieren. "
        "Das musst du auch nicht. "
        "In ibook siehst du, wer in deiner Nähe heute noch frei ist, mit Preisen und Bewertungen. "
        "3 Berührungen, und der Termin steht.",
        "Spontan Zeit? In ibook siehst du, wer heute noch frei ist, mit Preisen und "
        "Bewertungen. Drei Berührungen, und der Termin steht."),
"25C": ("Mittags stehen im Salon zwei Plätze leer, und abends kommen alle gleichzeitig. "
        "So verlierst du jeden Tag Geld. "
        "In ibook siehst du die Lücken in der Teamansicht und machst daraus ein Mittagsangebot. "
        "30 Sekunden, und die Stunde füllt sich.",
        "Mittags leer, abends überfüllt. In der ibook Teamansicht siehst du die Lücken und "
        "machst in dreißig Sekunden ein Angebot daraus."),
"26A": ("Frag dich einmal: wie viele Termine hattest du letzten Monat wirklich? "
        "Die meisten schätzen, und die meisten schätzen falsch. "
        "In ibook steht die Zahl schwarz auf weiß, mit Tagen, Leistungen und Auslastung. "
        "1 Blick pro Monat verändert dein Jahr. 30 Tage kostenlos.",
        "Wie viele Termine hattest du letzten Monat? In ibook steht die Zahl schwarz auf weiß, "
        "mit Tagen, Leistungen und Auslastung."),
"26B": ("Am Monatsende rechnest du im Kopf zusammen, was hereingekommen ist, und liegst daneben. "
        "Das ist keine Buchhaltung, das ist Raten. "
        "In ibook zählt die App jeden Termin mit und rechnet automatisch. "
        "0 Zettel, 0 Kopfrechnen. 30 Tage kostenlos.",
        "Im Kopf zusammenrechnen ist Raten. In ibook zählt die App jeden Termin mit und rechnet "
        "automatisch, ohne Zettel und Taschenrechner."),
"26C": ("Zahlen anzuschauen klingt nach Arbeit, ist aber ein Knopfdruck. "
        "Öffne in ibook die Auswertung und sieh drei Dinge: volle Tage, leere Stunden, "
        "gefragte Leistungen. 2 Berührungen, und du weißt, was du im nächsten Monat änderst. "
        "30 Tage kostenlos.",
        "Zwei Berührungen in ibook: volle Tage, leere Stunden, gefragte Leistungen. Danach "
        "weißt du genau, was du im nächsten Monat änderst."),
"27A": ("Im Hochsommer sind die halben Kundinnen verreist, und dein Tag hat plötzlich Löcher. "
        "Warten hilft da nicht. "
        "Mach in ibook aus den leeren Stunden ein Sommerangebot, und die, die dageblieben sind, "
        "greifen zu. 30 Tage kostenlos, jederzeit kündbar.",
        "Im Sommer sind viele weg und der Tag hat Löcher. Mach in ibook ein Sommerangebot "
        "daraus, für alle, die dageblieben sind."),
"27B": ("Du bist verreist und brauchst trotzdem einen Termin, kennst aber vor Ort niemanden. "
        "Fragen bringt nichts, du kennst ja auch keinen, den du fragen könntest. "
        "In ibook siehst du auf der Karte, wer in der fremden Stadt frei ist, "
        "mit Arbeiten und Bewertungen. 3 Berührungen.",
        "In einer fremden Stadt kennst du niemanden. In ibook siehst du auf der Karte, wer dort "
        "frei ist, mit Arbeiten, Preisen und Bewertungen."),
"27C": ("Ein leeres Fenster heute Nachmittag ist Geld, das in zwei Stunden verfallen ist. "
        "Verschenk es nicht. "
        "Tipp die Stunde in ibook an und mach ein Angebot daraus, sichtbar für alle in der Nähe. "
        "30 Sekunden Arbeit, und sie ist weg.",
        "Ein leeres Fenster verfällt in zwei Stunden. Antippen, Angebot daraus machen, dreißig "
        "Sekunden in ibook, und jemand greift zu."),
"28A": ("Dienstag und Mittwoch sind bei fast allen tot, und man gewöhnt sich daran. "
        "Dabei sind das zwei Arbeitstage pro Woche. "
        "Setz in ibook eine Aktion genau auf diese Tage, und sie füllen sich. "
        "2 tote Tage weniger im Monat sind acht. 30 Tage kostenlos.",
        "Dienstag und Mittwoch sind fast überall tot. Setz in ibook eine Aktion genau auf diese "
        "Tage, und sie füllen sich von allein."),
"28B": ("Im Sommer schwankt die Auslastung im Salon von Tag zu Tag, und du steuerst nach Gefühl. "
        "Gefühl ist im Sommer besonders unzuverlässig. "
        "In ibook zeigt der Bericht, welche Tage laufen und welche einbrechen. "
        "1 Blick pro Woche, 30 Tage kostenlos.",
        "Im Sommer schwankt alles. In ibook zeigt der Bericht, welche Tage laufen und welche "
        "einbrechen, und du steuerst nach Zahlen statt nach Gefühl."),
"28C": ("Du bist im Urlaub und willst trotzdem gut aussehen, kennst dort aber niemanden. "
        "Und im Hotel empfiehlt man dir irgendwas. "
        "In ibook siehst du auf der Karte, wer in deiner Urlaubsstadt frei ist, "
        "mit echten Arbeiten und Bewertungen. Termin in 3 Berührungen.",
        "Im Urlaub kennst du niemanden. In ibook siehst du auf der Karte, wer vor Ort frei ist, "
        "mit echten Arbeiten und Bewertungen."),
"29A": ("Du liegst am Strand, und dein Kalender füllt sich trotzdem weiter. "
        "Das ist kein Wunsch, das ist eine Einstellung. "
        "In ibook buchen deine Kundinnen selbst, egal wo du gerade bist. "
        "Du kommst zurück und hast eine volle Woche. 30 Tage kostenlos.",
        "Am Strand liegen, während der Kalender sich füllt. In ibook buchen deine Kundinnen "
        "selbst, egal wo du gerade bist."),
"29B": ("Dir fällt um halb zwölf nachts ein, dass du einen Termin brauchst, "
        "und schreiben willst du um die Zeit niemandem. "
        "In ibook musst du das auch nicht: freie Zeiten ansehen und buchen, ganz still. "
        "24 Stunden am Tag, ohne jemanden zu wecken.",
        "Nachts einen Termin buchen, ohne jemanden zu wecken. In ibook siehst du freie Zeiten "
        "und buchst still, rund um die Uhr."),
"29C": ("Im Chat verlierst du Kundinnen an drei Stellen: zu spät geantwortet, Frage übersehen, "
        "Preis nicht genannt. Drei Regeln reichen. "
        "Antworte an einem Ort, halte Preise im Profil aktuell, lass ibook den Termin bestätigen. "
        "3 Regeln, 30 Tage kostenlos.",
        "Drei Regeln gegen verlorene Kundinnen: an einem Ort antworten, Preise im Profil "
        "aktuell halten, Bestätigung ibook überlassen."),
"30A": ("Die beste Kundin ist die, die von selbst wiederkommt. "
        "Nur erinnert sie sich nicht immer daran, wann sie das letzte Mal da war. "
        "In ibook sieht sie ihren Verlauf und bucht dieselbe Leistung in 3 Berührungen. "
        "Erinnerung kommt automatisch. 30 Tage kostenlos.",
        "Die beste Kundin kommt von selbst wieder. In ibook sieht sie ihren Verlauf und bucht "
        "dieselbe Leistung in drei Berührungen."),
"30B": ("Beim zweiten Mal soll niemand wieder suchen, schreiben und warten müssen. "
        "Sonst kommt das zweite Mal gar nicht. "
        "In ibook tippt deine Kundin auf ihre letzte Buchung und wählt eine neue Zeit. "
        "1 Berührung, und sie ist wieder bei dir.",
        "Beim zweiten Mal soll niemand suchen müssen. In ibook tippt deine Kundin ihre letzte "
        "Buchung an und wählt eine neue Zeit. Eine Berührung."),
"30C": ("Kundinnen, die vier Monate nicht da waren, kommen selten von allein zurück. "
        "Aber sie kommen, wenn man sie erinnert. "
        "Sieh in ibook, wer lange nicht da war, und schick ein Angebot. "
        "2 Handgriffe, und ein Teil ist wieder da. 30 Tage kostenlos.",
        "Wer vier Monate weg war, kommt selten allein zurück. In ibook siehst du, wer das ist, "
        "und holst sie mit einem Angebot zurück."),
"31B": ("Vor dem Schulstart wollen alle Kinder gleichzeitig einen Haarschnitt, "
        "und in der letzten Woche bekommst du nirgends mehr einen Termin. "
        "In ibook siehst du jetzt, wer noch frei ist, und buchst in 3 Berührungen. "
        "Erinnerung kommt automatisch, damit der Schultag sitzt.",
        "Vor dem Schulstart wollen alle gleichzeitig. In ibook siehst du sofort, wer noch frei "
        "ist, und buchst in drei Berührungen."),
"31C": ("Der Schulanfang ist die zweite Hochsaison im Jahr, und viele verpassen sie, "
        "weil ihr Profil nicht bereit ist. "
        "Drei Schritte in ibook: aktuelle Arbeiten hochladen, Preise prüfen, Termine öffnen. "
        "10 Minuten, und die Welle arbeitet für dich. 30 Tage kostenlos.",
        "Schulanfang ist die zweite Hochsaison. Drei Schritte in ibook: Arbeiten hochladen, "
        "Preise prüfen, Termine öffnen. Zehn Minuten."),
"32A": ("Im Herbst kommen alle zurück, und wer jetzt nicht buchbar ist, verpasst die ganze "
        "Welle. Sie dauert nur ein paar Wochen. "
        "Öffne in ibook deine Termine für den ganzen Herbst, heute Abend. "
        "10 Minuten Arbeit, und der Kalender füllt sich selbst. 30 Tage kostenlos.",
        "Im Herbst kommen alle zurück. Öffne deine Termine in ibook jetzt, dann füllt sich der "
        "Kalender, während du arbeitest."),
"32B": ("Du suchst Verstärkung, und die Guten fragen als Erstes: wie voll ist es bei euch "
        "und wie wird abgerechnet. Ohne Antwort kommen sie nicht. "
        "In ibook zeigst du Auslastung und Bedingungen schwarz auf weiß. "
        "1 Bildschirm statt langer Erklärungen. 30 Tage kostenlos.",
        "Gute Leute fragen nach Auslastung und Bedingungen. In ibook zeigst du beides schwarz "
        "auf weiß, statt es lange zu erklären."),
"32C": ("Dein Salon hat fünf gute Leute, und nach außen sieht man davon nichts. "
        "Die Kundin sucht eine Person, nicht eine Adresse. "
        "In ibook steht das ganze Team in einem Profil, jede mit Arbeiten und Preisen. "
        "1 Profil, 5 Gründe zu buchen. 30 Tage kostenlos.",
        "Die Kundin sucht eine Person, nicht eine Adresse. In ibook steht das ganze Team in "
        "einem Profil, jede mit eigenen Arbeiten und Preisen."),
"33A": ("Du hast das Buch zu Hause vergessen, und der ganze Tag ist ein Blindflug. "
        "Wer kommt, wann, zu was, alles weg. "
        "In ibook liegt dein Kalender im Handy, und das hast du immer dabei. "
        "0 vergessene Tage, 30 Tage kostenlos.",
        "Buch zu Hause vergessen und der Tag ist ein Blindflug. In ibook liegt dein Kalender "
        "im Handy, das du immer dabei hast."),
"33B": ("Ein verlorenes Buch ist nicht nur Papier, das sind alle deine Kundinnen auf einmal. "
        "Nummern, Termine, Notizen, weg. "
        "In ibook liegt alles auf dem Server und geht nicht verloren, auch wenn das Handy weg ist. "
        "1 Vorfall reicht, um das zu bereuen.",
        "Ein verlorenes Buch heißt: alle Kundinnen weg. In ibook liegt alles sicher auf dem "
        "Server, unabhängig von Zettel und Handy."),
"33C": ("Vom Papier auf die App umzuziehen klingt nach Wochenendarbeit. Ist es nicht. "
        "Trag in ibook zuerst die Stammkundinnen ein, den Rest beim nächsten Termin. "
        "1 Abend für die Wichtigsten, und das Buch braucht keiner mehr. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Umzug vom Papier: zuerst die Stammkundinnen eintragen, den Rest beim nächsten Termin. "
        "Ein Abend, und das Buch ist überflüssig."),
"34A": ("Abends ist der Empfang zu, und genau dann entscheiden sich die meisten für einen Termin. "
        "Diese Buchungen gehen komplett verloren. "
        "In ibook läuft die Buchung weiter, auch wenn der Salon längst geschlossen ist. "
        "24 Stunden buchbar, 30 Tage kostenlos.",
        "Abends ist der Empfang zu, und genau dann wollen die meisten buchen. In ibook läuft "
        "die Buchung rund um die Uhr weiter."),
"34B": ("Du willst niemanden stören und schiebst den Termin deshalb vor dir her. "
        "Am Ende gehst du gar nicht. "
        "In ibook störst du niemanden: freie Zeit ansehen, antippen, gebucht. "
        "3 Berührungen, kein Gespräch, keine Wartezeit.",
        "Du willst niemanden stören und gehst deshalb gar nicht. In ibook buchst du still: "
        "freie Zeit ansehen, antippen, fertig."),
"34C": ("Vor dem Schulstart soll das Kind zum Friseur, und du kommst telefonisch nicht durch. "
        "Alle Eltern rufen in denselben Tagen an. "
        "In ibook siehst du die freien Zeiten sofort und buchst in 2 Berührungen. "
        "Erinnerung kommt automatisch, damit der Termin nicht untergeht.",
        "Vor dem Schulstart telefonieren alle Eltern gleichzeitig. In ibook siehst du freie "
        "Zeiten sofort und buchst in zwei Berührungen."),
"35A": ("Du willst es probieren, aber nicht vorher zahlen. Verständlich. "
        "Der erste Monat in ibook ist kostenlos, ohne Karte und ohne Vorkasse. "
        "Gefällt es nicht, hörst du auf und hast nichts verloren. "
        "30 Tage, um es an deinen echten Kundinnen zu sehen.",
        "Erster Monat in ibook kostenlos, ohne Karte. Gefällt es nicht, hörst du auf. Dreißig "
        "Tage, um es an echten Kundinnen zu testen."),
"35B": ("Manche fragen, wo man die App überhaupt bekommt. Kurze Antwort: dort, wo alle anderen "
        "auch liegen. "
        "ibook gibt es im App Store und bei Google Play, und für Kundinnen kostet sie 0 Euro. "
        "Herunterladen, suchen, buchen, fertig.",
        "ibook gibt es im App Store und bei Google Play. Für Kundinnen kostenlos: herunterladen, "
        "suchen, buchen."),
"35C": ("Dein Profil ist fertig, aber es kommt nichts. Meistens fehlen drei Dinge. "
        "Prüf in ibook: sind die Arbeiten aktuell, stehen alle Preise, sind die Termine offen. "
        "3 Punkte, 10 Minuten, und die Buchungen fangen an. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Profil fertig, aber keine Buchungen? Drei Punkte prüfen: aktuelle Arbeiten, "
        "vollständige Preise, offene Termine. Zehn Minuten in ibook."),
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
