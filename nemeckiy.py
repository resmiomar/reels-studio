#!/usr/bin/env python3
"""
Немецкий год: дописываем недостающие сценарии.

У немецкого было 2 сценария из 156, поэтому собирать было нечего. Структуру
(недели, слоты, аудитория, задания для кадров) берём из английского года: она
уже выверена и рассчитана на западный рынок. Пишем заново только то, что
слышно и читается - озвучку и описание.

Заголовок оставляем русским НАМЕРЕННО, как в английском годе: владелец не знает
немецкого, и по самому ролику рынок он не определит. Заголовок нужен ему, а не
зрителю: зритель видит только видео и описание.

Озвучка написана сразу в коротком виде, под 25 секунд: боль, потом ibook как
решение, потом предложение с цифрой. Короткий сборщик берёт из текста именно
эти три куска, поэтому фраза с числом обязательна, иначе предложение выпадет.

    python nemeckiy.py            дописать и проверить
"""
import os, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scenarii")

# Озвучка и описание. Ключ - неделя со слотом.
TEKST = {
"36A": ("Der Sommer ist vorbei und plötzlich wollen alle in dieser Woche einen Termin. "
        "Entweder füllt dieser Ansturm deinen Kalender oder er begräbt dich unter verpassten Anrufen. "
        "In ibook buchen deine Kundinnen selbst, Tag und Nacht, und dein Kalender füllt sich, während du arbeitest. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Nach den Ferien wollen alle gleichzeitig einen Termin. Lass deine Kundinnen selbst buchen, "
        "rund um die Uhr, statt Anrufe zu verpassen. Profil in ibook anlegen, Arbeiten und Preise zeigen, "
        "der Kalender füllt sich von allein. 30 Tage kostenlos testen, jederzeit kündbar."),

"36B": ("Sonne, Salzwasser und Chlor hatten den ganzen Sommer Zeit für deine Haare. "
        "Jetzt willst du zurück zu der Einen, die genau weiß, was dir steht. "
        "In ibook findest du sie in Sekunden, siehst ihre freien Termine und buchst direkt vom Handy. "
        "Kein Anruf, keine Warteschleife, 24 Stunden am Tag buchbar.",
        "Der Sommer war hart zu deinen Haaren. Zeit für die Person, die dich kennt. "
        "In ibook findest du sie in Sekunden, siehst freie Termine und buchst direkt vom Handy. "
        "Echte Arbeiten, echte Preise, echte Bewertungen. 24 Stunden am Tag."),

"36C": ("Der Herbst ist da und deine Preise sind gestiegen. Du musst das nicht jeder einzeln erzählen. "
        "In ibook öffnest du deine Leistungen, tippst auf eine, trägst den neuen Preis ein und speicherst. "
        "Ab diesem Moment zeigen dein Profil und jede Buchung den richtigen Preis. "
        "2 Minuten Arbeit, keine peinlichen Gespräche mehr am Ende des Termins.",
        "Preise ändern sich im Herbst. In ibook änderst du sie einmal und alle sehen sofort den richtigen Preis, "
        "im Profil, im Link und bei jeder Buchung. Keine Erklärungen mehr am Ende des Termins. "
        "30 Tage kostenlos testen."),

"37A": ("Du hast es doppelt eingetragen. Jetzt stehen zwei Kundinnen zur selben Stunde vor dir, "
        "und eine geht enttäuscht wieder. Das ist kein voller Tag, das ist ein schlechter. "
        "In ibook sperrt der Kalender den Termin in der Sekunde, in der er vergeben wird. "
        "Keine Doppelbuchung, 0 Streit, jederzeit kündbar.",
        "Doppelt eingetragen und plötzlich stehen zwei Kundinnen zur selben Zeit da. "
        "In ibook sperrt der Kalender den Slot sofort, wenn er vergeben ist. Keine Doppelbuchungen, "
        "keine unangenehmen Gespräche. 30 Tage kostenlos testen, jederzeit kündbar."),

"37B": ("Das Telefon klingelt, jemand will heute noch einen Termin, und du läufst durch den Salon und fragst, "
        "wer frei ist. Währenddessen steht ein Stuhl leer. "
        "In ibook liegt das ganze Team auf einem Bildschirm, jede Lücke und jede Buchung, live. "
        "1 Blick genügt, und der Termin ist vergeben.",
        "Ein Stuhl steht leer, während du durch den Salon läufst und fragst, wer Zeit hat. "
        "In ibook siehst du das ganze Team auf einem Bildschirm, jede Lücke live. "
        "Termin vergeben in Sekunden, ohne Zettel und Rückfragen. 30 Tage kostenlos."),

"37C": ("Doppelbuchungen entstehen fast immer so: zwei Personen tragen an zwei verschiedenen Stellen ein. "
        "Die Lösung ist ein gemeinsamer Plan. "
        "In ibook hat jede im Team eigene Zeiten und Leistungen, und der Kalender sperrt den Slot sofort. "
        "1 Plan für alle, 0 Überschneidungen.",
        "Zwei Listen führen zu doppelten Terminen. Ein gemeinsamer Plan löst das. "
        "In ibook hat jede eigene Zeiten und Leistungen, der Kalender sperrt vergebene Slots automatisch. "
        "30 Tage kostenlos testen, jederzeit kündbar."),

"38A": ("Eine Kundin schreibt dir hier, die nächste dort, die dritte irgendwo, wo du heute nicht nachgesehen hast. "
        "Am Abend fehlt eine Antwort und damit eine Buchung. "
        "In ibook liegen alle Nachrichten an einer Stelle, direkt neben dem Termin, um den es geht. "
        "1 Ort statt 3 Messenger.",
        "Nachrichten in drei Messengern, und abends fehlt eine Antwort und damit eine Buchung. "
        "In ibook liegt jeder Chat an einer Stelle, direkt neben dem passenden Termin. "
        "Du antwortest einmal und vergisst nichts. 30 Tage kostenlos."),

"38B": ("Du willst nur kurz fragen, ob sie Samstag Zeit hat, oder ihr ein Foto von der Frisur schicken. "
        "Also suchst du die Nummer, dann das Profil, dann den alten Chat. "
        "In ibook öffnest du ihre Seite und schreibst. Gleiche Stelle, an der du auch buchst. "
        "24 Stunden am Tag erreichbar.",
        "Nummer suchen, Profil suchen, alten Chat suchen. Oder einfach ihre Seite in ibook öffnen und schreiben. "
        "Fragen, Foto schicken, Termin buchen, alles an einer Stelle. Rund um die Uhr."),

"38C": ("Du kannst dir nicht jedes Detail merken, und das musst du auch nicht. "
        "Schreib nach dem Termin eine Zeile in die Kundenkarte: die Mischung, die Länge, das Getränk. "
        "In ibook steht beim nächsten Mal alles da, bevor sie sitzt. "
        "1 Zeile pro Termin, und du wirkst wie jemand, der sich alles merkt.",
        "Niemand merkt sich alles. Schreib nach dem Termin eine Zeile in die Kundenkarte. "
        "In ibook steht beim nächsten Besuch alles bereit: Farbe, Länge, Vorlieben. "
        "Deine Kundin fühlt sich erkannt. 30 Tage kostenlos testen."),

"39A": ("Sie kommt herein und dir fällt der Name nicht ein. Das Gesicht kennst du, den Rest nicht mehr. "
        "In ibook hat jede Kundin eine Karte: Name, Telefon, jeder Besuch, jede Leistung, jede Notiz. "
        "1 Tipp, bevor sie sitzt, und du weißt wieder alles. "
        "30 Tage kostenlos, jederzeit kündbar.",
        "Gesicht bekannt, Name weg. In ibook hat jede Kundin eine Karte mit allen Besuchen, "
        "Leistungen und Notizen. Ein Tipp vor dem Termin und du weißt wieder alles. "
        "30 Tage kostenlos testen."),

"39B": ("Sie setzt sich und sagt: das Gleiche wie letztes Mal. Das Gleiche wie was? "
        "Du rätst bei einer Farbe, die du vor Wochen gemischt hast. "
        "In ibook steht der letzte Besuch direkt da: was du gemacht hast, wie lange es dauerte, was es kostete. "
        "0 Raten, 0 Entschuldigungen.",
        "Das Gleiche wie letztes Mal, nur welches Gleiche? In ibook steht der letzte Besuch mit Leistung, "
        "Dauer, Preis und deinen Notizen. Du triffst die Farbe beim ersten Versuch. "
        "30 Tage kostenlos testen."),

"39C": ("Der letzte Termin war gut? Dann such niemanden neu. "
        "Öffne deine Buchungen in ibook, tippe auf die Person, bei der du warst, und wähle den nächsten freien Termin. "
        "3 Berührungen und es steht. Gleiche Person, gleiche Leistung, und die Erinnerung kommt von allein.",
        "Wieder zur selben Person? Buchungen öffnen, antippen, freien Termin wählen. "
        "Drei Berührungen in ibook und der Termin steht. Erinnerung kommt automatisch, damit du ihn nicht vergisst."),

"40A": ("Du hast jeden Tag gearbeitet und kannst trotzdem nicht sagen, welche Leistung sich wirklich gelohnt hat. "
        "Beschäftigt sein ist nicht dasselbe wie Bescheid wissen. "
        "In ibook öffnest du die Auswertung und siehst es schwarz auf weiß: volle Tage, leere Stunden, gefragte Leistungen. "
        "1 Blick pro Monat verändert dein Jahr.",
        "Voller Terminkalender heißt nicht automatisch gutes Geld. In ibook zeigt die Auswertung, "
        "welche Leistungen laufen, welche Tage voll sind und welche leer bleiben. "
        "Ein Blick pro Monat. 30 Tage kostenlos testen."),

"40B": ("Eine Mitarbeiterin ist ausgebucht und im Stress. Die andere scrollt zwischen zwei Kundinnen am Handy. "
        "Du spürst es, aber beweisen kannst du es nicht, also ändert sich nichts. "
        "In ibook stellt die Salon-Auswertung alle nebeneinander: wer ausgelastet ist, wer frei ist, wer was bringt. "
        "1 Bildschirm, und die Diskussion ist vorbei.",
        "Die eine im Stress, die andere am Handy. In ibook zeigt die Salon-Auswertung alle nebeneinander: "
        "Auslastung, Umsatz, freie Zeiten. Entscheidungen nach Zahlen statt nach Gefühl. 30 Tage kostenlos."),

"40C": ("Monatsende ist der richtige Moment für deine Zahlen. "
        "Öffne die Auswertung in ibook und schau auf drei Dinge: welche Leistungen wirklich gebucht werden, "
        "welche Tage voll sind und welche leer bleiben. "
        "Dann mach aus den leeren Stunden ein Angebot. 3 Zahlen, 1 Entscheidung.",
        "Setz dich zum Monatsende hin und schau auf drei Zahlen: gefragte Leistungen, volle Tage, leere Stunden. "
        "In ibook steht alles auf einem Bildschirm. Aus leeren Stunden machst du ein Angebot. 30 Tage kostenlos."),

"41A": ("Deine Vormittage sind leer, deine Abende voll. Das ist Geld, das du nie wiedersiehst. "
        "In ibook machst du aus jeder leeren Stunde ein Angebot, und Kundinnen, die rund um die Uhr buchen, "
        "greifen zu, bevor dein Kaffee kalt wird. "
        "0 Provision auf deine Leistungen, 30 Tage kostenlos.",
        "Leere Vormittage sind verlorenes Geld. In ibook machst du aus einer stillen Stunde ein Angebot, "
        "sichtbar für alle, die gerade suchen. Keine Provision auf deine Leistungen. 30 Tage kostenlos testen."),

"41B": ("Ein freier Vormittag und nichts geplant? Dann ruf nicht überall an und warte auf einen Rückruf. "
        "Öffne ibook, sieh, wer in deiner Nähe gerade einen Termin frei hat, und buche in wenigen Berührungen. "
        "Echte Profile, echte Preise, echte Bewertungen. 1 freier Vormittag, gut genutzt.",
        "Spontan Zeit? In ibook siehst du, wer in deiner Nähe jetzt frei ist, mit Arbeiten, Preisen und Bewertungen. "
        "Buchen in wenigen Berührungen, ohne Anruf und Warteschleife."),

"41C": ("Öffne den Salon-Kalender in ibook und wechsle zur Teamansicht. Jeder Platz nebeneinander. "
        "Die Lücken springen dir sofort ins Auge, und du siehst, wer ausgebucht ist und wer einen leeren Nachmittag hat. "
        "Tippe auf eine freie Stunde und mach ein Angebot daraus. 30 Sekunden Arbeit.",
        "Teamansicht öffnen und die Lücken sehen. In ibook erkennst du in 30 Sekunden, wer ausgelastet ist "
        "und wer leer läuft. Freie Stunde antippen, Angebot daraus machen. 30 Tage kostenlos testen."),

"42A": ("Klar rufen deine Kundinnen gern an. Aber deine Hände sind beschäftigt und das Telefon klingelt weiter. "
        "Ein verpasster Anruf und sie bucht woanders. "
        "Schick einmal deinen persönlichen ibook Link, und sie sucht sich selbst eine Zeit, Tag oder Nacht. "
        "1 Link statt 20 Rückrufe.",
        "Deine Hände sind beschäftigt, das Telefon klingelt weiter, und ein verpasster Anruf bucht woanders. "
        "Schick einmal deinen ibook Link und sie wählt selbst eine Zeit, rund um die Uhr. 30 Tage kostenlos."),

"42B": ("Wenige Kundinnen sind genau der Grund, hier zu sein. "
        "Menschen in deiner Nähe suchen gerade jetzt und finden dich einfach nicht. "
        "Leg ein Profil in ibook an, mit deinen Arbeiten, Preisen und Bewertungen, und zeig dich in der Suche "
        "und auf der Karte. 30 Tage kostenlos, jederzeit kündbar.",
        "Wenige Kundinnen heißt oft nur: dich findet niemand. In ibook zeigst du Arbeiten, Preise und Bewertungen "
        "und erscheinst in der Suche und auf der Karte deiner Stadt. 30 Tage kostenlos testen."),

"42C": ("Jetzt zum Geld, und das sind nur zwei Schritte. "
        "Leistung in ibook öffnen, Preis eintragen. Fertig. "
        "Ab sofort sieht jede Kundin den Preis vor der Buchung, und das unangenehme Gespräch am Ende fällt weg. "
        "0 Provision auf deine Leistungen, für immer.",
        "Zwei Schritte: Leistung öffnen, Preis eintragen. Ab dann sieht jede Kundin den Preis vor der Buchung. "
        "Keine Provision auf deine Leistungen. 30 Tage kostenlos testen, jederzeit kündbar."),

"43A": ("Arbeitest du allein? Dann ist der Master Tarif deiner: dein Profil, dein Link, dein Kalender. "
        "Führst du ein Team? Der Salon Tarif gibt dir einen gemeinsamen Plan, alle an einer Stelle "
        "und eine Auswertung, wer was bringt. "
        "Gleiche App ibook, 0 Provision auf Leistungen, 30 Tage kostenlos.",
        "Allein oder im Team? Master Tarif für dein eigenes Profil und deinen Kalender, Salon Tarif für "
        "gemeinsamen Plan und Auswertung. Gleiche App, keine Provision auf Leistungen. 30 Tage kostenlos."),

"43B": ("Warum durch die halbe Stadt fahren, wenn zwei Straßen weiter jemand Gutes sitzt? "
        "Öffne die Karte in ibook und sieh die Profis um dich herum, mit Arbeiten, Preisen und Bewertungen. "
        "Wähl eine Zeit, die dir passt, buche sie, und die Erinnerung kommt vor dem Termin. "
        "2 Straßen statt 2 Stunden Fahrt.",
        "Gute Leute gibt es oft zwei Straßen weiter. Öffne die Karte in ibook, sieh Arbeiten, Preise und "
        "Bewertungen in deiner Nähe und buche eine Zeit, die passt. Erinnerung kommt automatisch."),

"43C": ("Termin gebucht? Zwei Berührungen und du vergisst ihn nicht mehr. "
        "Erstens: tippe auf Erlauben, wenn die App nach Mitteilungen fragt. "
        "Zweitens: lass die Buchung in deiner Liste stehen. "
        "ibook erinnert dich rechtzeitig vorher, und du kommst entspannt und pünktlich. 2 Berührungen, 0 vergessene Termine.",
        "Mitteilungen erlauben und die Buchung in der Liste lassen. Mehr braucht es nicht. "
        "ibook erinnert dich vor dem Termin, damit du entspannt und pünktlich ankommst."),
}


def main():
    en = json.load(open(os.path.join(SC, "videos_en.json"), encoding="utf-8"))
    de = json.load(open(os.path.join(SC, "videos_de.json"), encoding="utf-8"))
    gotovo = {f"{v['week']}{v['slot']}": v for v in de}
    dobavleno = 0
    for v in en:
        k = f"{v['week']}{v['slot']}"
        if k not in TEKST:
            continue
        vo, cap = TEKST[k]
        # Переписываем и уже существующие: правки текста должны доезжать,
        # а не молча пропускаться, потому что запись когда-то создали.
        nov = gotovo.get(k) or dict(v)     # структура и задания для кадров те же
        if k not in gotovo:
            de.append(nov); dobavleno += 1
        nov["vo"] = " ".join(vo.split())
        nov["caption"] = " ".join(cap.split())
        nov["hook"] = nov["vo"].split(".")[0].strip() + "."
    # Два самых первых немецких сценария писались словами: «Dreißig Tage».
    # Короткий сборщик ищет предложение по ЦИФРЕ, поэтому оно выпадало.
    for v in de:
        v["vo"] = v["vo"].replace("Dreißig Tage", "30 Tage").replace("dreißig Tage", "30 Tage")
        v["caption"] = v.get("caption", "").replace("Dreißig Tage", "30 Tage")
    de.sort(key=lambda v: (v["week"], v["slot"]))
    json.dump(de, open(os.path.join(SC, "videos_de.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"добавлено сценариев: {dobavleno}, всего немецких: {len(de)}")

    # Проверка: короткий сборщик должен найти в тексте боль, ibook и цифру,
    # иначе из ролика выпадет предложение и он станет просто жалобой.
    bez = [f"{v['week']}{v['slot']}" for v in de
           if "ibook" not in v["vo"] or not any(c.isdigit() for c in v["vo"])]
    print("без ibook или без цифры:", bez if bez else "нет, все в порядке")
    print("осталось написать:", 156 - len(de))


if __name__ == "__main__":
    main()
