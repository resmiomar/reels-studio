#!/usr/bin/env python3
"""
Немецкий год, остальные 130 сценариев.

Структура берётся из английского года, пишется только то, что слышно и
читается: озвучка и описание. Заголовок остаётся русским намеренно - он для
владельца, зритель его не видит.

Каждая озвучка построена под 25 секунд: боль, ibook как решение, предложение
с цифрой. Фраза с числом обязательна, иначе короткий сборщик выбросит
предложение и ролик станет просто жалобой.

    python nemeckiy2.py
"""
import os, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scenarii")

TEKST = {
"1B": ("Nach den Feiertagen willst du endlich wieder gut aussehen, aber deine Stylistin "
       "meldet sich nicht und die Nummer von der Kollegin hast du auch nicht mehr. "
       "In ibook siehst du, wer in deiner Nähe frei ist, mit Arbeiten, Preisen und Bewertungen. "
       "Termin in 3 Berührungen, ohne einen einzigen Anruf.",
       "Januar, du willst einen Termin und niemand geht ans Telefon. In ibook siehst du freie "
       "Zeiten in deiner Nähe, mit echten Arbeiten und Preisen, und buchst direkt vom Handy."),
"1C": ("Du willst online buchbar sein, aber es klingt nach einem ganzen Abend Arbeit. "
       "Ist es nicht. In ibook legst du Foto, Leistungen und Preise an, und dein Profil steht. "
       "10 Minuten, und ab dann buchen deine Kundinnen selbst, Tag und Nacht. "
       "30 Tage kostenlos, jederzeit kündbar.",
       "Profil anlegen dauert keinen Abend, sondern zehn Minuten: Foto, Leistungen, Preise. "
       "Danach buchen deine Kundinnen in ibook selbst, rund um die Uhr. 30 Tage kostenlos."),
"2A": ("Sie schreibt dir um halb zwölf nachts, du liest es morgens um neun. "
       "In diesen neun Stunden hat sie längst jemand anderen gefunden. "
       "In ibook braucht sie dich dafür nicht: sie sieht deine freien Zeiten und bucht selbst, "
       "auch nachts. Du schläfst, der Kalender arbeitet. 30 Tage kostenlos.",
       "Nachts geschrieben, morgens gelesen, Kundin weg. In ibook bucht sie selbst, wann immer "
       "sie will, ohne auf deine Antwort zu warten. 30 Tage kostenlos testen."),
"2B": ("Deine Hände sind in fremden Haaren, das Telefon klingelt, und du kannst nicht rangehen. "
       "Ein verpasster Anruf ist eine verpasste Kundin, jedes Mal. "
       "Mit deinem ibook Link sucht sie sich selbst eine Zeit, ohne dich zu stören. "
       "0 verpasste Anrufe, 30 Tage kostenlos.",
       "Ein verpasster Anruf ist eine verpasste Kundin. Schick ihr einmal deinen ibook Link, "
       "und sie wählt selbst eine freie Zeit, während du in Ruhe arbeitest."),
"2C": ("Im Salon führt jede ihren eigenen Kalender, und am Ende weiß niemand, wer wann frei ist. "
       "Zwei Schritte lösen das: Salon in ibook anlegen, Team dazuholen. "
       "Danach liegt der ganze Plan auf einem Bildschirm, live. "
       "1 Kalender für alle, 30 Tage kostenlos.",
       "Jede führt ihren eigenen Kalender, keiner hat den Überblick. Salon in ibook anlegen, "
       "Team dazuholen, fertig: ein Plan für alle. 30 Tage kostenlos testen."),
"3A": ("Du fragst dich mitten im Tag, wer gerade frei ist, und musst durch den Salon laufen, "
       "um es herauszufinden. In ibook liegt der ganze Plan auf einem Bildschirm: "
       "jeder Platz, jede Lücke, jede Buchung, in Echtzeit. "
       "1 Blick statt 5 Fragen. 30 Tage kostenlos.",
       "Der ganze Salonplan auf einem Bildschirm: jeder Platz, jede Lücke, jede Buchung live. "
       "Kein Herumfragen mehr. 30 Tage kostenlos testen, jederzeit kündbar."),
"3B": ("Anrufen, warten, wieder anrufen, dann Rückruf abwarten. So verlierst du eine halbe Stunde "
       "für einen Termin. In ibook wählst du eine freie Zeit und buchst sie, fertig. "
       "Keine Warteschleife, kein Rückruf. 24 Stunden am Tag, auch sonntags.",
       "Anrufen, warten, nochmal anrufen. Oder in ibook einfach eine freie Zeit antippen und "
       "buchen. Rund um die Uhr, auch am Wochenende."),
"3C": ("Deine Preise stehen in deinem Kopf, in Notizen und irgendwo im Chat, und jede Kundin "
       "fragt trotzdem nach. Trag sie einmal in ibook ein: Leistung, Dauer, Preis. "
       "5 Minuten Arbeit, und danach sieht jede alles vor der Buchung. "
       "Keine Preisfragen mehr, 30 Tage kostenlos.",
       "Leistungen und Preise einmal eintragen, fünf Minuten. Danach sieht jede Kundin alles "
       "vor der Buchung, in ibook. Keine Preisfragen im Chat mehr."),
"4A": ("Du willst es ausprobieren, aber jede App will zuerst deine Kartennummer. "
       "Bei uns nicht. In ibook bekommst du 30 Tage kostenlos, ohne Karte, ohne Vorkasse. "
       "Wenn es nichts für dich ist, hörst du einfach auf. Nichts zu verlieren.",
       "30 Tage kostenlos in ibook, ohne Karte und ohne Vorkasse. Gefällt es nicht, hörst du "
       "einfach auf. Profil anlegen, Leistungen eintragen, buchbar sein."),
"4B": ("Neue App bedeutet meistens einen verlorenen Abend. Hier nicht. "
       "Foto rein, Leistungen und Preise eintragen, Arbeitszeiten setzen, fertig. "
       "10 Minuten in ibook, und du bist rund um die Uhr buchbar. "
       "30 Tage kostenlos, jederzeit kündbar.",
       "Zehn Minuten einrichten: Foto, Leistungen, Preise, Arbeitszeiten. Danach bist du in "
       "ibook rund um die Uhr buchbar. 30 Tage kostenlos testen."),
"4C": ("Du kennst niemanden in der neuen Stadt und weißt nicht, wen du fragen sollst. "
       "Dann such nicht nach einem Namen, sondern nach dem, was du brauchst. "
       "In ibook tippst du deine Leistung ein und siehst, wer sie in deiner Nähe macht, "
       "mit Preisen und Bewertungen. Termin in 3 Berührungen.",
       "Du kennst keinen Namen? Such nach der Leistung. In ibook siehst du, wer sie in deiner "
       "Nähe anbietet, mit Arbeiten, Preisen und Bewertungen."),
"5A": ("Zum Valentinstag wollen alle gleichzeitig einen Termin, und zwar in denselben zwei Tagen. "
       "Wer vorher öffnet, ist voll, wer wartet, verpasst es. "
       "Öffne deine Termine jetzt in ibook, und deine Kundinnen tragen sich selbst ein. "
       "30 Tage kostenlos, jederzeit kündbar.",
       "Zum Valentinstag drängen sich alle in zwei Tage. Öffne deine Termine früh in ibook, "
       "dann tragen sich deine Kundinnen selbst ein, während du arbeitest."),
"5B": ("Zum Valentinstag denkst du an alle, nur nicht an dich. Dieses Jahr andersherum. "
       "Such dir in ibook jemanden in deiner Nähe, sieh dir Arbeiten und Bewertungen an "
       "und buche dir selbst einen Termin. 3 Berührungen und der Tag gehört dir.",
       "Am 14. Februar denkst du an alle, nur nicht an dich. Buch dir in ibook selbst einen "
       "Termin: echte Arbeiten, echte Preise, freie Zeiten sofort sichtbar."),
"5C": ("Du schreibst jeder Kundin am Vorabend eine Erinnerung von Hand, und trotzdem vergisst "
       "eine den Termin. In ibook erinnert die App von selbst, rechtzeitig vorher. "
       "1 Einstellung, und du schreibst diese Nachrichten nie wieder. "
       "30 Tage kostenlos, jederzeit kündbar.",
       "Erinnerungen von Hand kosten dich jeden Abend Zeit. In ibook gehen sie automatisch raus, "
       "rechtzeitig vor dem Termin. Weniger Ausfälle, keine Tipparbeit."),
"6A": ("Zwei Kundinnen, eine Uhrzeit, und eine von beiden geht enttäuscht wieder nach Hause. "
       "Sie kommt nicht zurück, und das weißt du. "
       "In ibook sperrt der Kalender die Zeit in der Sekunde, in der sie vergeben ist. "
       "0 Doppelbuchungen, 30 Tage kostenlos.",
       "Zwei Kundinnen auf eine Uhrzeit, und eine geht enttäuscht. In ibook sperrt der Kalender "
       "die Zeit sofort nach der Buchung. Das kann nicht mehr passieren."),
"6B": ("Zur Stoßzeit klingelt das Telefon, jemand steht an der Theke, und eine Dritte wartet "
       "auf Antwort. Der Empfang ist ein Flaschenhals, jeden Tag. "
       "In ibook buchen deine Kundinnen selbst, auch mitten im Ansturm. "
       "1 Person weniger im Stress, 30 Tage kostenlos.",
       "Zur Stoßzeit ist der Empfang der Flaschenhals. In ibook buchen Kundinnen selbst, ohne "
       "Anruf und ohne Warten an der Theke. 30 Tage kostenlos testen."),
"6C": ("Deine schönsten Arbeiten liegen im Handy, und niemand außer dir sieht sie. "
       "Vor dem Valentinstag ist das teuer. Lad die besten Fotos in dein ibook Profil, "
       "1 Minute Arbeit, und jede, die dich findet, sieht sofort, was du kannst. "
       "30 Tage kostenlos.",
       "Deine besten Arbeiten liegen ungesehen im Handy. Ins ibook Profil laden dauert eine "
       "Minute, und jede Kundin sieht sofort, was du kannst."),
"7A": ("Jeden Abend tippst du Erinnerungen an die Kundinnen von morgen. Das ist eine halbe "
       "Stunde deiner Freizeit, jeden Tag. "
       "In ibook macht das die App: sie erinnert automatisch, rechtzeitig vor dem Termin. "
       "30 Minuten am Tag zurück, 30 Tage kostenlos.",
       "Erinnerungen tippen kostet dich jeden Abend eine halbe Stunde. In ibook gehen sie von "
       "selbst raus. Deine Zeit gehört wieder dir."),
"7B": ("Du hast den Termin gebucht und ihn drei Tage später komplett vergessen. "
       "Passiert jedem, kostet aber Geld und einen unangenehmen Anruf. "
       "In ibook kommt die Erinnerung von selbst aufs Handy, rechtzeitig vorher. "
       "1 Hinweis, und du kommst entspannt und pünktlich.",
       "Termin gebucht und vergessen? In ibook kommt die Erinnerung automatisch aufs Handy, "
       "rechtzeitig vorher. Du kommst entspannt und pünktlich an."),
"7C": ("Am 14. Februar ist eine im Team komplett überrannt und eine andere hat Leerlauf, "
       "und du merkst es erst am Abend an der Kasse. "
       "In ibook siehst du die Auslastung aller live, auf einem Bildschirm. "
       "1 Blick, und du verteilst um, bevor es zu spät ist.",
       "Am Valentinstag ist eine überrannt und eine hat Leerlauf. In ibook siehst du die "
       "Auslastung aller live und verteilst um, bevor der Tag vorbei ist."),
"8A": ("Deine Arbeiten schickst du einzeln im Chat, an jede neue Kundin von Hand. "
       "Das ist Arbeit, die du hundertmal doppelt machst. "
       "Leg sie einmal in dein ibook Profil, und jede sieht sie vor der Buchung. "
       "1 Mal hochladen statt 100 Mal schicken. 30 Tage kostenlos.",
       "Arbeiten einzeln im Chat verschicken ist hundertfache Doppelarbeit. Einmal ins ibook "
       "Profil laden, und jede sieht sie vor der Buchung."),
"8B": ("Am Ende des Termins kommt die Frage nach dem Preis, und es wird kurz unangenehm für "
       "euch beide. Das muss nicht sein. "
       "In ibook steht der Preis an der Leistung, sichtbar vor der Buchung. "
       "0 peinliche Gespräche, 30 Tage kostenlos.",
       "Die Preisfrage am Ende ist für beide unangenehm. In ibook sieht deine Kundin den Preis "
       "vor der Buchung, an jeder Leistung. Kein Gespräch nötig."),
"8C": ("Du gehst zu jemand Neuem und weißt bis zum Schluss nicht, was dich erwartet. "
       "Frag vorher die, die schon da waren. "
       "In ibook stehen Bewertungen nur von Leuten, die wirklich einen Termin hatten, "
       "und du liest sie in 2 Minuten, bevor du buchst.",
       "Bewertungen in ibook schreiben nur Leute, die wirklich da waren. Zwei Minuten lesen, "
       "und du weißt, worauf du dich einlässt."),
"9A": ("Du spürst, dass eine im Team mehr bringt als die andere, aber beweisen kannst du es "
       "nicht, also ändert sich nichts. "
       "In ibook zeigt der Salonbericht jede einzeln: Termine, Auslastung, Umsatz. "
       "1 Bildschirm, und die Diskussion ist beendet. 30 Tage kostenlos.",
       "Gefühl ist kein Beweis. In ibook zeigt der Salonbericht jede Mitarbeiterin einzeln: "
       "Termine, Auslastung, Umsatz. Entscheidungen nach Zahlen."),
"9B": ("Du willst wissen, ob heute noch was frei ist, und musst dafür schreiben und warten. "
       "In ibook siehst du die freien Zeiten sofort, ohne zu fragen: "
       "heute, morgen, nächste Woche, alles auf einen Blick. "
       "Termin in 3 Berührungen, 24 Stunden am Tag.",
       "Freie Zeiten siehst du in ibook sofort, ohne zu fragen: heute, morgen, nächste Woche. "
       "Antippen und buchen, rund um die Uhr."),
"9C": ("Neue Kundinnen schauen zuerst auf die Bewertungen, und bei dir steht noch nichts. "
       "Der Anfang ist der schwerste Teil. "
       "Bitte die Nächste nach dem Termin um eine Bewertung, das dauert bei ihr 30 Sekunden. "
       "In ibook steht sie danach dauerhaft in deinem Profil.",
       "Ohne Bewertungen zögern neue Kundinnen. Bitte nach dem Termin um eine, das dauert "
       "dreißig Sekunden, und sie steht dauerhaft in deinem ibook Profil."),
"10A": ("Zum Muttertag wollen alle einen Termin schenken, und die meisten fragen dich zwei Tage "
        "vorher. Dann ist es zu spät für alle. "
        "Öffne die Tage jetzt in ibook und lass sie sich selbst eintragen. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Muttertag wird zwei Tage vorher angefragt, und dann ist alles voll. Öffne deine Tage "
        "früh in ibook, und deine Kundinnen tragen sich selbst ein."),
"10B": ("Zum Muttertag willst du ihr etwas schenken, das sie sich selbst nie gönnt. "
        "Ein Termin ist genau das. "
        "In ibook findest du jemanden in ihrer Nähe, siehst Arbeiten und Preise "
        "und buchst in 3 Berührungen. Erinnerung kommt automatisch.",
        "Schenk ihr zum Muttertag das, was sie sich selbst nie gönnt. In ibook findest du "
        "jemanden in ihrer Nähe und buchst in drei Berührungen."),
"10C": ("An den Spitzentagen im Jahr entscheidet sich, ob der Monat gut wird. "
        "Und sie sind schneller voll, als du denkst. "
        "Öffne die Termine in ibook und mach aus den Randzeiten ein Angebot. "
        "2 Handgriffe, und der Tag füllt sich von allein. 30 Tage kostenlos.",
        "Spitzentage entscheiden über den Monat. Termine früh öffnen, Randzeiten als Angebot "
        "setzen, und der Tag füllt sich in ibook von allein."),
"11A": ("In den Ferien willst du auch mal frei haben, aber dann fragt doch jemand genau an "
        "diesem Tag. Und du sagst zu, weil du dich schlecht fühlst. "
        "In ibook trägst du deine freien Tage ein, und sie sind gar nicht erst buchbar. "
        "1 Einstellung, und der Tag gehört dir.",
        "Freie Tage in ibook eintragen, und niemand kann sie mehr buchen. Kein schlechtes "
        "Gewissen, keine Absagen. Der Tag gehört dir."),
"11B": ("In den Ferien fällt die halbe Mannschaft weg, und der Plan wird jeden Morgen neu "
        "erfunden. Das kostet Nerven und Termine. "
        "In ibook trägt jede ihre Zeiten selbst ein, und der Plan stimmt automatisch. "
        "1 Kalender für alle, 30 Tage kostenlos.",
        "In den Ferien wird der Plan täglich neu erfunden. In ibook trägt jede ihre Zeiten "
        "selbst ein, und der Salonplan stimmt von allein."),
"11C": ("Du willst dir einen Tag frei nehmen, traust dich aber nicht, weil dann Anfragen kommen. "
        "Trag ihn einfach in ibook als frei ein. "
        "Ab dem Moment sieht niemand mehr freie Zeiten an diesem Tag. "
        "1 Minute Arbeit, und du hast wirklich frei.",
        "Freien Tag in ibook eintragen dauert eine Minute. Danach ist er für niemanden mehr "
        "buchbar, und du musst niemandem absagen."),
"12A": ("Nach Bewertungen zu fragen ist unangenehm, also fragst du nicht, und dein Profil "
        "bleibt leer. Neue Kundinnen sehen das. "
        "In ibook fragt die App nach dem Termin von selbst nach. "
        "0 unangenehme Bitten, und die Bewertungen kommen. 30 Tage kostenlos.",
        "Nach Bewertungen zu fragen ist unangenehm. In ibook fragt die App nach dem Termin von "
        "selbst, und dein Profil füllt sich ohne dein Zutun."),
"12B": ("Im Netz steht viel, und man weiß nie, wer das geschrieben hat und warum. "
        "In ibook geht das nicht: eine Bewertung kann nur schreiben, wer wirklich einen Termin "
        "hatte. Keine gekauften Texte, keine erfundenen Kundinnen. "
        "2 Minuten lesen, und du weißt Bescheid.",
        "Bewertungen in ibook kommen nur von echten Terminen. Keine gekauften Texte, keine "
        "erfundenen Kundinnen. Zwei Minuten lesen reicht."),
"12C": ("Eine Neue fängt an, und der halbe Tag geht dafür drauf, sie überall einzutragen. "
        "In ibook geht das anders: einladen, Leistungen und Zeiten setzen, fertig. "
        "1 Minute, und sie steht im gemeinsamen Plan mit allen anderen. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Neue Mitarbeiterin einrichten dauert in ibook eine Minute: einladen, Leistungen und "
        "Zeiten setzen. Danach steht sie im gemeinsamen Plan."),
"13A": ("Rechne einmal nach. Eine einzige Kundin, die nicht erscheint, kostet dich mehr als "
        "der ganze Monat in der App. "
        "In ibook erinnert die App automatisch, und genau diese Ausfälle werden seltener. "
        "1 verhinderter Ausfall zahlt den Monat. 30 Tage kostenlos.",
        "Ein einziger Ausfall kostet mehr als ein Monat in der App. Automatische Erinnerungen "
        "in ibook machen genau diese Ausfälle seltener."),
"13B": ("Viele Plattformen nehmen bei jeder Buchung einen Anteil, und je besser du arbeitest, "
        "desto mehr zahlst du. Das ist verkehrt herum. "
        "In ibook gibt es 0 Prozent Provision auf deine Leistungen, für immer. "
        "Du zahlst den Monat und behältst alles andere.",
        "Keine Provision auf deine Leistungen, null Prozent, für immer. Du zahlst nur den Monat "
        "und behältst jeden Euro aus deiner Arbeit."),
"13C": ("Vor der Abiballsaison schaut man sich dein Profil genauer an als sonst. "
        "Drei Dinge entscheiden: aktuelle Arbeiten, klare Preise, echte Bewertungen. "
        "Fehlt eines davon, geht sie weiter. "
        "In ibook bringst du alle 3 in 10 Minuten in Ordnung.",
        "Drei Dinge entscheiden vor der Ballsaison: aktuelle Arbeiten, klare Preise, echte "
        "Bewertungen. In ibook bringst du sie in zehn Minuten in Ordnung."),
"14A": ("Hochzeiten werden Monate vorher geplant, und wer erst im Mai öffnet, ist raus. "
        "Die Bräute buchen jetzt. "
        "Öffne die Termine in ibook schon heute, dann tragen sie sich selbst ein. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Hochzeiten werden Monate vorher gebucht. Öffne deine Termine früh in ibook, dann "
        "tragen sich die Bräute selbst ein, während du arbeitest."),
"14B": ("Für den großen Tag willst du die Richtige, und die Guten sind früh ausgebucht. "
        "Wer wartet, nimmt am Ende, was übrig ist. "
        "In ibook siehst du, wer für deinen Termin noch frei ist, mit Arbeiten und Bewertungen. "
        "3 Berührungen, und der Tag ist gesichert.",
        "Die Guten sind früh ausgebucht. In ibook siehst du, wer an deinem Datum noch frei ist, "
        "mit Arbeiten und Bewertungen, und buchst sofort."),
"14C": ("Deine Kundinnen sind alle da, nur verstreut über drei Messenger und ein Notizbuch. "
        "Such einmal eine Nummer von vor einem Jahr. "
        "Trag sie in ibook ein, und jede hat ihre Karte mit Verlauf und Notizen. "
        "1 Ort statt 4, 30 Tage kostenlos.",
        "Deine Kundinnen liegen über drei Messenger verstreut. In ibook hat jede eine Karte mit "
        "Verlauf, Nummer und Notizen. Ein Ort statt vier."),
"15A": ("Manche Kundinnen waren ein halbes Jahr nicht da, und du hast es gar nicht bemerkt. "
        "Das sind fertige Termine, die einfach liegen bleiben. "
        "In ibook siehst du, wer lange nicht da war, und schreibst sie an. "
        "10 Minuten, und ein Teil kommt zurück. 30 Tage kostenlos.",
        "Wer war ein halbes Jahr nicht da? In ibook siehst du das auf einen Blick und holst "
        "diese Kundinnen mit einer Nachricht zurück."),
"15B": ("Deine Kundin kommt, ihre Stammkraft ist krank, und die Kollegin weiß nichts über sie. "
        "Der Termin wird für alle unangenehm. "
        "In ibook liegt die Kundenkarte für das ganze Team bereit: Verlauf, Farbe, Notizen. "
        "1 Tipp, und die Kollegin ist im Bilde. 30 Tage kostenlos.",
        "Fällt eine aus, weiß die Kollegin nichts über die Kundin. In ibook liegt die Karte für "
        "das ganze Team bereit: Verlauf, Farbe, Notizen."),
"15C": ("Du willst Mittag machen, aber genau dann fragt jemand nach einem Termin. "
        "Und du sagst wieder zu. "
        "In ibook blockst du deine Pause mit 2 Berührungen, und niemand kann sie mehr buchen. "
        "Deine Pause bleibt deine Pause. 30 Tage kostenlos.",
        "Pause in ibook mit zwei Berührungen blocken, und niemand kann sie mehr buchen. Kein "
        "Absagen, kein schlechtes Gewissen."),
"16A": ("Jede neue Kundin fragt dasselbe: was kostet das, wann hast du Zeit, wo bist du. "
        "Du tippst das zum hundertsten Mal. "
        "Schick stattdessen einen ibook Link: dort steht alles, und sie bucht direkt. "
        "1 Link statt 20 Nachrichten. 30 Tage kostenlos.",
        "Immer dieselben Fragen im Chat. Ein ibook Link beantwortet sie alle: Preise, freie "
        "Zeiten, Adresse, Bewertungen. Und sie bucht direkt."),
"16B": ("Du willst nur einen Termin, und es wird ein Gespräch über zehn Nachrichten. "
        "Ein Link reicht. "
        "Antippen, freie Zeit wählen, buchen, fertig. In ibook siehst du dabei Preise, "
        "Arbeiten und Bewertungen. 3 Berührungen statt 10 Nachrichten.",
        "Ein Link statt zehn Nachrichten: antippen, freie Zeit wählen, buchen. Preise und "
        "Bewertungen siehst du in ibook gleich mit."),
"16C": ("Vor dem Abiball sind die guten Zeiten schnell weg, und telefonisch kommst du nirgends "
        "durch. Alle rufen gleichzeitig an. "
        "In ibook siehst du sofort, wer an dem Tag noch frei ist, und buchst selbst. "
        "3 Berührungen, kein einziger Anruf.",
        "Vor dem Ball telefoniert die halbe Stadt. In ibook siehst du freie Zeiten sofort und "
        "buchst selbst, ohne Warteschleife."),
"17A": ("Du bist gut, aber wer dich nicht kennt, findet dich auch nicht. "
        "Und die meisten suchen genau jetzt im Handy, nicht bei Freundinnen. "
        "In ibook erscheinst du in der Suche und auf der Karte deiner Stadt, "
        "mit Arbeiten, Preisen und Bewertungen. 30 Tage kostenlos.",
        "Wer dich nicht kennt, findet dich nicht. In ibook erscheinst du in der Suche und auf "
        "der Karte deiner Stadt, mit Arbeiten und Preisen."),
"17B": ("Deine Kundinnen kommen alle über Empfehlungen, und das heißt: neue kommen kaum dazu. "
        "Der Kreis bleibt derselbe. "
        "In ibook finden dich auch die, die niemanden kennen, über Suche und Karte. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Nur Empfehlungen heißt: immer derselbe Kreis. In ibook finden dich auch Menschen, die "
        "niemanden kennen, über Suche und Karte."),
"17C": ("Zur Ballsaison kommen sie zu zweit und zu dritt, und jede fragt einzeln nach Preis "
        "und Dauer. Das frisst deinen Tag. "
        "Leg in ibook ein fertiges Paket an: Leistungen, Dauer, Preis in einem. "
        "30 Sekunden Arbeit, und sie buchen es selbst.",
        "Fertiges Paket für die Ballsaison in ibook anlegen: Leistungen, Dauer, Preis in einem. "
        "Dreißig Sekunden, und deine Kundinnen buchen es selbst."),
"18A": ("Vor Ostern wollen alle in dieselben drei Tage, und du sagst der Hälfte ab. "
        "Absagen sind verlorenes Geld. "
        "Öffne die Feiertage in ibook früh, dann verteilen sie sich selbst über die Woche. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Vor Ostern drängen sich alle in drei Tage. Öffne die Feiertage früh in ibook, dann "
        "verteilen sich die Termine von selbst."),
"18B": ("Vor Ostern sind die guten Zeiten in ein paar Tagen weg, und dann bleibt nur noch "
        "Montagvormittag. "
        "In ibook siehst du sofort, wer noch frei ist, und buchst in 3 Berührungen. "
        "Erinnerung kommt automatisch, damit du den Termin nicht verpasst.",
        "Vor Ostern sind gute Zeiten schnell weg. In ibook siehst du sofort, wer noch frei ist, "
        "und buchst in drei Berührungen."),
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
