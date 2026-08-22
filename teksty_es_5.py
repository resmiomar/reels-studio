#!/usr/bin/env python3
"""
Испанские тексты, партия пятая и последняя: недели 42-52.

Конец года. Декабрь в бьюти - самый плотный месяц, и тексты идут за этим:
предзапись, корпоративы, вечерний поток, неявки, которые в декабре стоят
дороже всего.

Отдельно про две недели:

    Black Friday   в Испании прижился прочно, в бьюти скидки в эти дни
                   ждут. Для нас это повод дать годовой тариф.
    Nochevieja     тридцать первое, вечерний поток до самой ночи. Мастер
                   работает, когда все уже празднуют.

Возражения тоже здесь: «мои клиенты привыкли звонить» и «у меня мало
клиентов, зачем мне приложение». Их не отметаем, а разбираем спокойно -
именно так их снимают в разговоре, а не рекламой.

    python teksty_es_5.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PUT = os.path.join(HERE, "scenarii", "videos_es.json")

TEKSTY = {
 (42, "A"): (
  "Mis clientas están acostumbradas a llamar",
  "Es verdad, y nadie te pide que se lo prohíbas. Sigue cogiendo el teléfono "
  "a quien quiera llamar. Pero pon también el enlace: la mitad prefiere reservar "
  "sin hablar y hoy no puede. En dos meses verás qué camino elige cada una, "
  "y no habrás perdido a nadie.",
  "Añade el enlace, sin quitar nada",
  "Nadie te pide que dejes de coger el teléfono. Solo que exista la otra puerta."),

 (42, "B"): (
  "Tengo pocas clientas, ¿para qué la app?",
  "Justo por eso. Con la agenda llena da igual cómo la lleves, "
  "pero con huecos lo que necesitas es que te encuentren. "
  "Un perfil en el buscador trabaja las horas que tú no estás trabajando. "
  "Y el primer mes no cuesta nada.",
  "Empieza estando vacía",
  "Con la agenda llena da igual el sistema. Con huecos, necesitas que te encuentren."),

 (42, "C"): (
  "Pagar son dos pasos",
  "Sin llamadas, sin comercial, sin firmar nada. "
  "Entras en la app, eliges plan mensual o anual y pagas con la tarjeta. "
  "Dos pasos y sigues trabajando. Cancelar es igual de rápido, "
  "desde el mismo sitio y sin dar explicaciones.",
  "Elige tu plan",
  "Dos pasos para pagar y dos para cancelar. Sin llamadas ni comerciales."),

 (43, "A"): (
  "¿Plan de profesional o de salón?",
  "Si trabajas sola, aunque sea dentro de un local alquilado, el tuyo es el individual. "
  "Si gestionas a otras personas y quieres ver sus agendas y sus números, "
  "el de salón. La diferencia no es el tamaño: "
  "es si mandas solo sobre tu agenda o sobre varias.",
  "Elige tu plan",
  "No es cuestión de tamaño: es si gestionas una agenda o varias."),

 (43, "B"): (
  "Profesionales cerca, en el mapa",
  "No sabes qué hay bueno en tu barrio, y por eso cruzas media ciudad "
  "para ir donde siempre. Abre el mapa y mira lo que tienes a diez minutos "
  "andando: precios, trabajos y opiniones. "
  "A veces lo bueno está a dos calles.",
  "Mira el mapa",
  "Cruzas media ciudad por costumbre. A veces lo bueno está a dos calles."),

 (43, "C"): (
  "Dos toques y no se te olvida",
  "Reservas y la cita se guarda con recordatorio. "
  "El día antes te llega el aviso al móvil con hora y dirección. "
  "No hay que apuntarlo en ningún sitio ni acordarse: "
  "el aviso llega solo.",
  "Reserva y olvídate",
  "El aviso llega el día antes con hora y dirección. No hay que apuntar nada."),

 (44, "A"): (
  "La campaña de Navidad se monta en noviembre",
  "En diciembre no hay tiempo ni de pensar: se trabaja. "
  "Lo que decida cómo te va ese mes se hace ahora, en noviembre: "
  "abrir las fechas fuertes, poner precio de temporada "
  "y montar un bono de regalo. Tres cosas.",
  "Prepara diciembre ya",
  "En diciembre solo se trabaja. Diciembre se decide en noviembre."),

 (44, "B"): (
  "Las fechas buenas ya se están yendo",
  "Todavía piensas que queda mucho para las fiestas, "
  "y las horas del veintitrés y el treinta y uno ya están cayendo. "
  "Las que quedan libres a última hora son las malas. "
  "Mira ahora y coge la tuya.",
  "Coge tu fecha ya",
  "El veintitrés y el treinta y uno se están llenando. Después quedan las horas malas."),

 (44, "C"): (
  "Abre tus fechas de fiestas en medio minuto",
  "Marca los días fuertes de diciembre, alarga el horario "
  "esas tardes concretas y ponles precio de temporada. "
  "Treinta segundos de trabajo y las reservas empiezan a entrar "
  "cuando tú ya estás en otra cosa.",
  "Abre diciembre",
  "Marcas los días fuertes y alargas la tarde. Treinta segundos."),

 (45, "A"): (
  "Abre la reserva anticipada de diciembre",
  "Quien se organiza reserva diciembre en noviembre, "
  "y esa gente es la mejor: viene, no falla y paga sin discutir. "
  "Si tu agenda no llega hasta allí, esas reservas se las lleva "
  "quien sí la tiene abierta.",
  "Abre la agenda de diciembre",
  "La gente organizada reserva con un mes. Si tu agenda no llega, reserva en otra parte."),

 (45, "B"): (
  "El diciembre del salón, cuadrado antes",
  "Diciembre con cinco profesionales y sin cuadrante hecho "
  "es un mes de gritos. Ahora, con calma, marcáis vacaciones, "
  "refuerzos y horarios ampliados. En diciembre solo hay que trabajar, "
  "no organizar.",
  "Cuadra diciembre en noviembre",
  "Con el cuadrante hecho, en diciembre solo se trabaja."),

 (45, "C"): (
  "El plan de Black Friday, con todo el equipo",
  "Decidid tres cosas antes: qué servicios entran en oferta, "
  "qué días concretos y cuántas plazas como mucho. "
  "Sin límite de plazas, el Black Friday llena la agenda "
  "de trabajo barato y deja fuera al que paga entero.",
  "Prepara vuestro Black Friday",
  "Qué servicios, qué días y cuántas plazas. Sin límite, se llena de trabajo barato."),

 (46, "A"): (
  "Black Friday: dos meses de regalo",
  "Estos días el plan anual sale a precio de diez meses. "
  "Pagas una vez, tienes el año entero cubierto "
  "y te olvidas del recibo. Es la única vez al año "
  "que el año sale a este precio.",
  "Coge el plan anual",
  "Doce meses al precio de diez. Solo estos días."),

 (46, "B"): (
  "Echa la cuenta del año",
  "Doce meses sueltos, o diez pagados de una vez. "
  "La diferencia son dos meses enteros de trabajo "
  "que te quedas tú. Si ya llevas medio año usándolo "
  "y sabes que sigues, la cuenta se hace sola.",
  "Haz la cuenta",
  "Doce sueltos o diez de una vez. La diferencia son dos meses tuyos."),

 (46, "C"): (
  "Pagas diez, usas doce",
  "Sin trampa: el plan anual cuesta lo que diez mensualidades "
  "y dura doce meses. Si lo dejas a mitad de año, "
  "te devolvemos la parte que no has usado. "
  "No hay permanencia ni penalización.",
  "Mira el plan anual",
  "Diez mensualidades, doce meses. Y si lo dejas, devolución de lo no usado."),

 (47, "A"): (
  "En diciembre una ausencia duele el doble",
  "Un hueco vacío en julio es una pena. En diciembre es una hora "
  "que tenías vendida tres veces. Con recordatorio automático "
  "y confirmación, quien no puede venir lo cambia con tiempo "
  "y ese hueco se lo lleva otra.",
  "Activa las confirmaciones",
  "Un hueco de diciembre estaba vendido tres veces. Que se libere a tiempo."),

 (47, "B"): (
  "El aviso te llega al móvil",
  "En diciembre se te juntan las cenas, los regalos y la familia, "
  "y una cita se olvida sin querer. El aviso te llega al teléfono "
  "el día antes con hora y sitio, y si no puedes "
  "lo cambias desde el mismo mensaje.",
  "Reserva con aviso",
  "En diciembre se olvida todo. El aviso llega solo el día antes."),

 (47, "C"): (
  "Menos ausencias en plena avalancha",
  "Tres cosas bajan las ausencias de diciembre: recordatorio el día antes, "
  "confirmación con un toque y que cancelar sea fácil. "
  "Parece raro, pero cuando cancelar es fácil, "
  "la gente avisa en vez de desaparecer.",
  "Baja tus ausencias",
  "Cuando cancelar es fácil, la gente avisa en vez de desaparecer."),

 (48, "A"): (
  "El equipo del salón en diciembre",
  "Es el mes en que todas trabajan al límite y cualquier hueco "
  "de organización se paga caro. En una pantalla ves las agendas "
  "de todas, mueves una cita de la que va ahogada "
  "a la que tiene aire, y el día se salva.",
  "Mira a tu equipo",
  "En diciembre todas van al límite. Mover una cita a tiempo salva el día."),

 (48, "B"): (
  "Reserva también para tu amiga",
  "Le hablas de tu peluquera y se queda en «me pasas el contacto». "
  "Y ahí muere. Comparte su perfil directamente: "
  "tu amiga ve trabajos, precios y horas libres, "
  "y reserva sin pedirte nada más.",
  "Comparte el perfil",
  "«Pásame el contacto» y ahí muere. Comparte el perfil y reserva sola."),

 (48, "C"): (
  "Encontrar hueco en pleno diciembre",
  "Parece que no queda nada, pero las cancelaciones sueltan huecos "
  "todo el día. Filtra por esta semana y mira dos veces al día: "
  "los huecos que se liberan por la mañana "
  "suelen estar cogidos por la tarde.",
  "Busca huecos liberados",
  "Las cancelaciones sueltan huecos todo el día. Hay que mirar dos veces."),

 (49, "A"): (
  "Diciembre es el mes más denso del año",
  "Se trabajan más horas que nunca y aun así se pierde dinero "
  "por desorden: citas pisadas, ausencias, huecos que nadie llena. "
  "El mes se aguanta si la agenda está en un solo sitio "
  "y avisa sola.",
  "Ordena tu diciembre",
  "En diciembre no se pierde dinero por falta de trabajo. Se pierde por desorden."),

 (49, "B"): (
  "Los últimos huecos antes de las fiestas",
  "Quedan los de primera hora y los de última, "
  "y se van en dos días. Si quieres ir arreglada a la cena de Nochebuena, "
  "esta es la semana de reservar. La que viene "
  "ya solo quedarán cancelaciones.",
  "Coge tu hueco",
  "Quedan los de primera y última hora. La semana que viene, solo cancelaciones."),

 (49, "C"): (
  "Tres ajustes para un diciembre tranquilo",
  "Uno: duraciones reales, para que el día no se caiga. "
  "Dos: recordatorio automático, para que no falten. "
  "Tres: horario ampliado solo los días fuertes. "
  "Tres ajustes en diez minutos y el mes cambia de carácter.",
  "Haz los tres ajustes",
  "Duraciones reales, recordatorio automático y horario ampliado. Diez minutos."),

 (50, "A"): (
  "Cenas de empresa: flujo de tarde hasta la noche",
  "En diciembre la gente se arregla después del trabajo, "
  "y a las siete tienes cola mientras la mañana está vacía. "
  "Abre horas hasta las diez solo esas semanas "
  "y cierra alguna mañana. El día cunde el doble.",
  "Alarga tus tardes",
  "En diciembre nadie viene por la mañana. Todos a las siete."),

 (50, "B"): (
  "El salón a pleno rendimiento",
  "Las semanas de cenas de empresa el salón va al máximo "
  "y la recepción no da abasto. Si las citas entran solas por la app, "
  "recepción se dedica a recibir y cobrar, "
  "que es lo que de verdad necesita a una persona delante.",
  "Descarga la recepción",
  "En las semanas de cenas, recepción no da abasto. Que las citas entren solas."),

 (50, "C"): (
  "El flujo de tarde antes de las fiestas",
  "De seis a nueve se concentra medio día de trabajo. "
  "Mira en el panel qué tardes concretas revientan "
  "y refuerza solo esas. No hace falta ampliar el mes entero: "
  "con cuatro tardes bien cubiertas basta.",
  "Refuerza tus tardes",
  "Medio día de trabajo entre las seis y las nueve. Refuerza solo esas tardes."),

 (51, "A"): (
  "Cuántas citas has hecho este año",
  "Se acaba el año y no sabes si has trabajado más o menos que el anterior. "
  "Está contado: citas del año, meses fuertes, meses flojos "
  "y cuántas clientas nuevas entraron. "
  "Mirarlo cuesta un minuto y sirve para todo el año que viene.",
  "Mira tu año",
  "Citas del año, meses fuertes y clientas nuevas. Contado, no a ojo."),

 (51, "B"): (
  "Empieza el año con el mes gratis",
  "Enero es el mes para probar cosas: hay menos trabajo "
  "y tiempo para ordenar. Monta el perfil ahora, "
  "usa enero entero gratis y llega a febrero "
  "con la agenda ya funcionando sola.",
  "Empieza enero gratis",
  "Enero tiene menos trabajo y más tiempo. Es el mes de ordenar."),

 (51, "C"): (
  "Cierra el año sin la libreta",
  "Sumar doce libretas para saber cómo fue el año no lo hace nadie, "
  "y por eso nadie sabe cómo fue su año. "
  "Si las citas están dentro, el resumen ya está hecho: "
  "lo abres y lo lees.",
  "Mira tu resumen",
  "Nadie suma doce libretas. Por eso nadie sabe cómo le fue el año."),

 (52, "A"): (
  "El look de fin de año se reserva hoy",
  "El treinta y uno todo el mundo quiere estar bien, "
  "y las horas de esa tarde son las primeras que vuelan. "
  "Mira quién tiene sitio, coge la tuya "
  "y quítate esa preocupación de encima.",
  "Reserva tu Nochevieja",
  "Las horas del treinta y uno son las primeras que vuelan."),

 (52, "B"): (
  "Año nuevo, agenda nueva, primer mes gratis",
  "Empezar el año con la agenda ordenada cambia cómo trabajas. "
  "El primer mes es gratis y sin tarjeta: montas el perfil "
  "entre fiesta y fiesta, y el uno de enero "
  "ya recibes reservas mientras duermes.",
  "Empieza el año en ibook",
  "El primer mes gratis y sin tarjeta. El uno de enero ya te reservan."),

 (52, "C"): (
  "Coge tu hueco de enero en dos clics",
  "En enero todo el mundo quiere arreglarse lo que dejó en diciembre, "
  "y la primera semana se llena entera. "
  "Reserva ahora tu hueco de enero: dos clics "
  "y empiezas el año con eso resuelto.",
  "Reserva tu enero",
  "La primera semana de enero se llena entera. Cógela ahora, dos clics."),
}


def main():
    d = json.load(open(PUT, encoding="utf-8"))
    n = 0
    for v in d:
        k = (v["week"], v["slot"])
        if k in TEKSTY and not v.get("vo", "").strip():
            h, vo, cta, cap = TEKSTY[k]
            v["hook"], v["vo"], v["cta"], v["caption"] = h, vo, cta, cap
            n += 1
    json.dump(d, open(PUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    g = sum(1 for v in d if v.get("vo", "").strip())
    print(f"  добавлено: {n}")
    print(f"  испанский: {g} из 156, осталось {156 - g}")
    if g >= 156:
        dl = [len(v["vo"].split()) for v in d]
        print(f"  длина: в среднем {sum(dl)/len(dl):.0f} слов, от {min(dl)} до {max(dl)}")


if __name__ == "__main__":
    main()
