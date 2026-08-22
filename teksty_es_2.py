#!/usr/bin/env python3
"""
Испанские тексты, партия вторая: недели 9-18.

Продолжение teksty_es_1. Строение и язык те же: обращение на «ты», лексика
именно испанская, а не общеиспаноязычная, и разговорная интонация вместо
рекламной.

Что в этой партии учтено особо:

    Día de la Madre  в Испании это первое воскресенье мая, а не второе,
                     как в большинстве стран. Ошибиться тут - выдать себя.
    Semana Santa     не «Пасха» одним днём, а целая неделя, когда половина
                     страны уезжает. Для мастера это и провал, и пик разом.
    graduaciones     выпускные в июне, с ними идёт волна причёсок и макияжа.
    autónoma         испанский мастер платит фиксированную месячную квоту
                     независимо от выручки. Это сильная боль, её и трогаем.

    python teksty_es_2.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PUT = os.path.join(HERE, "scenarii", "videos_es.json")

TEKSTY = {
 (9, "A"): (
  "Quién trabajó de verdad este mes",
  "A final de mes crees saber cómo ha ido el salón, pero es una sensación, no un dato. "
  "En el panel lo ves por persona: cuántas citas hizo cada una, cuánto entró, "
  "qué días quedaron flojos. Con eso repartes turnos con criterio "
  "y no discutes de memoria con nadie.",
  "Mira el informe por persona",
  "A final de mes, sensaciones no: cuántas citas y cuánto entró por cada profesional."),

 (9, "B"): (
  "Ves los huecos libres sin preguntar",
  "Escribes «¿tienes hueco?» y esperas. A veces media hora, a veces hasta mañana. "
  "En ibook los huecos están a la vista: entras, miras el jueves, "
  "hay un sitio a las seis y lo coges. La conversación entera te la ahorras.",
  "Mira los huecos en ibook",
  "«¿Tienes hueco?» y a esperar. O entrar, verlo tú misma y reservarlo."),

 (9, "C"): (
  "Tu primera opinión en medio minuto",
  "Un perfil sin opiniones da desconfianza aunque trabajes de maravilla. "
  "Pídesela a la clienta de siempre justo cuando termina y está contenta: "
  "le llega el enlace y lo deja en treinta segundos. Con tres opiniones "
  "el perfil ya se lee como algo serio.",
  "Pide tu primera opinión",
  "Un perfil sin opiniones no lo elige nadie. La primera se pide en treinta segundos."),

 (10, "A"): (
  "El Día de la Madre se reserva antes",
  "El primer domingo de mayo todas quieren regalar algo a su madre, "
  "y lo piensan tres días antes. Abre ahora las horas de esa semana "
  "y pon un bono de regalo. Quien compra para su madre lo compra con tiempo, "
  "y tú llegas con la agenda llena en vez de con prisas.",
  "Abre las horas de mayo",
  "El Día de la Madre se decide con días de antelación. Abre las horas y pon el bono."),

 (10, "B"): (
  "Regálale a tu madre una cita",
  "Otra vez las flores que duran cuatro días. Este año regálale dos horas "
  "para ella sola: mira quién tiene hueco el fin de semana del Día de la Madre, "
  "elige el servicio y resérvalo desde el móvil. "
  "Ella recibe el aviso y solo tiene que ir.",
  "Reserva su cita en ibook",
  "Flores otra vez, o dos horas para ella sola. Reserva desde el móvil en un minuto."),

 (10, "C"): (
  "Los días fuertes se cierran en dos pasos",
  "Sabes qué semanas del año se te llenan. En vez de sufrirlas, ábrelas antes: "
  "marcas esos días como horario ampliado y pones un precio de reserva anticipada. "
  "Dos acciones. El resto lo hace la gente sola, sin que contestes un mensaje.",
  "Prepara tus días fuertes",
  "Las semanas de pico se preparan antes, no se sufren después."),

 (11, "A"): (
  "Vacaciones cuando tú quieras",
  "Coger días libres siendo autónoma da vértigo: parece que cierras el negocio. "
  "En ibook bloqueas las fechas y ya está: nadie puede reservar esos días "
  "y nadie te escribe preguntando. Vuelves y la agenda sigue abierta "
  "justo donde la dejaste.",
  "Bloquea tus días libres",
  "Bloqueas las fechas y nadie puede reservarlas. Ni un mensaje preguntando."),

 (11, "B"): (
  "Turnos de vacaciones sin líos",
  "En agosto media plantilla está fuera y el cuadrante es un caos de mensajes. "
  "Cada profesional marca sus días en su agenda, y tú ves el mes entero "
  "en una pantalla: quién está, quién no, y qué días se quedan sin nadie. "
  "El hueco se ve antes de que sea un problema.",
  "Organiza el cuadrante",
  "El cuadrante de agosto en una pantalla. Los días sin nadie se ven a tiempo."),

 (11, "C"): (
  "Tu día libre se llena solo",
  "Te sale un plan y decides no trabajar el viernes. Antes eso eran diez mensajes "
  "avisando. Ahora bloqueas el día y las que buscaban hueco ven directamente "
  "el lunes. Nadie se queda esperando respuesta y tú no das explicaciones.",
  "Bloquea el día en un toque",
  "Un toque y ese día desaparece de tu agenda. Sin avisar a nadie."),

 (12, "A"): (
  "Las opiniones llegan solas",
  "Pedir opiniones da apuro y por eso no las pides. Que lo haga la app: "
  "cuando termina la cita le llega sola la petición, sin que tú digas nada. "
  "Una de cada tres responde, y en un mes tienes el perfil lleno "
  "de gente que fue de verdad.",
  "Activa las opiniones",
  "Pedir opiniones da apuro. Que las pida la app cuando termina la cita."),

 (12, "B"): (
  "Opiniones solo de quien fue",
  "En internet cualquiera escribe lo que quiera, y por eso ya no te fías. "
  "En ibook solo opina quien tuvo una cita de verdad, y al lado se ve "
  "qué servicio se hizo. Por eso son cortas y aburridas, "
  "y por eso puedes creértelas.",
  "Lee opiniones reales",
  "Solo opina quien fue de verdad. Por eso se pueden creer."),

 (12, "C"): (
  "Profesional nueva, agenda al minuto",
  "Entra alguien nuevo al equipo y hasta que se entera de todo pasan semanas. "
  "La das de alta, marcas sus servicios y sus horas, y esa misma tarde "
  "ya puede recibir reservas. Sin explicarle un sistema, "
  "sin que dependa de recepción para nada.",
  "Añade a tu equipo",
  "Alguien nuevo puede recibir citas la misma tarde. Sin formación."),

 (13, "A"): (
  "Una sola ausencia cuesta más que el mes",
  "Cuando alguien no aparece pierdes la hora entera y el dinero de esa hora. "
  "Pasa dos veces al mes y ya te has comido lo que cuesta la app. "
  "Con aviso automático y confirmación, las ausencias bajan solas: "
  "quien no puede venir lo cambia el día antes y el hueco se libera.",
  "Reduce las ausencias",
  "Dos ausencias al mes cuestan más que la app. El aviso automático las baja."),

 (13, "B"): (
  "Cero comisión por tus servicios",
  "Otras plataformas se llevan un porcentaje de cada cita, y cuanto mejor "
  "te va, más pagas. Aquí no: pagas lo mismo hagas diez citas o cien, "
  "y ni un céntimo de tu servicio se va a nadie. "
  "Lo que cobras es tuyo entero.",
  "Sin comisiones, nunca",
  "Ni un porcentaje de tus servicios. Pagas lo mismo con diez citas que con cien."),

 (13, "C"): (
  "Tres cosas antes de las graduaciones",
  "En junio llega la avalancha de peinados y maquillajes de graduación. "
  "Deja tres cosas hechas antes: los servicios de esa semana con su precio, "
  "tus mejores fotos de recogidos, y las horas abiertas. "
  "Quien busca en junio te encuentra lista.",
  "Prepara junio hoy",
  "Servicios, fotos y horas abiertas. Tres cosas antes de la avalancha de junio."),

 (14, "A"): (
  "Bodas: abre la reserva anticipada",
  "En temporada de bodas las novias cierran mucho antes que el resto. "
  "Si tu agenda solo tiene las dos semanas próximas, para ellas no existes. "
  "Abre los meses de verano ya: la que se casa en agosto "
  "quiere dejarlo cerrado en abril.",
  "Abre tus fechas de verano",
  "Las novias cierran con meses. Si tu agenda solo llega a dos semanas, no te encuentran."),

 (14, "B"): (
  "Cierra tu look antes de que vuelen las fechas",
  "Te casas en verano y todavía no has cerrado peluquería ni maquillaje. "
  "Las buenas fechas se van primero, y luego toca conformarse. "
  "Mira quién tiene libre tu día, reserva la prueba y la boda de una vez, "
  "y quítatelo de la cabeza.",
  "Reserva tu prueba y tu boda",
  "Las fechas buenas vuelan. Cierra prueba y boda de una vez."),

 (14, "C"): (
  "Tu base de clientas está en el chat",
  "Los nombres, los teléfonos y lo que se hizo cada una están repartidos "
  "entre Instagram, WhatsApp y una libreta. Si pierdes el móvil, pierdes el negocio. "
  "En ibook cada clienta tiene su ficha con su historial, "
  "y esa lista es tuya, no de una red social.",
  "Pasa tu base a ibook",
  "Tu negocio no puede vivir dentro de WhatsApp. La lista tiene que ser tuya."),

 (15, "A"): (
  "Quién lleva tres meses sin venir",
  "Tienes clientas buenas que se han ido perdiendo sin motivo: "
  "cambiaron de curro, se lió el mes, y ya está. En la lista las ves ordenadas "
  "por última visita. Un mensaje a las diez primeras "
  "te llena media semana floja.",
  "Mira quién no vuelve",
  "Clientas buenas que se perdieron sin motivo. Se ven en una lista y vuelven con un mensaje."),

 (15, "B"): (
  "La ficha la ve todo el equipo",
  "Se va una profesional y con ella se va lo que sabía de cada clienta: "
  "el tono exacto, la alergia, lo que no le gusta. En ibook la ficha vive "
  "en el salón, no en un móvil. Quien la atienda mañana "
  "abre y ve todo el historial.",
  "Guarda la ficha en el salón",
  "Si el historial vive en un móvil, se va con esa persona. En el salón se queda."),

 (15, "C"): (
  "Tu hora de comer, protegida",
  "Te apuntan una cita encima de la comida y acabas comiendo de pie otra vez. "
  "Marca ese rato como no disponible y desaparece de la agenda. "
  "Nadie puede reservarlo, ni tú te lías. Dos toques y tienes "
  "una hora que es tuya de verdad.",
  "Protege tu hora de comer",
  "Dos toques y esa hora deja de existir para las reservas."),

 (16, "A"): (
  "Un enlace en vez de veinte mensajes",
  "Cada cita nueva son ocho mensajes: qué te haces, cuánto vale, "
  "qué día, a qué hora, dónde estás. Manda tu enlace y ahí está todo: "
  "servicios, precios, horas libres y dirección. "
  "Ella elige y tú solo ves la cita aparecer.",
  "Comparte tu enlace",
  "Ocho mensajes por cita, o un enlace donde está todo."),

 (16, "B"): (
  "Un enlace y ya estás dentro",
  "Te pasan un enlace y en la misma pantalla ves lo que hace, "
  "cuánto cuesta, cuándo tiene hueco y dónde está. "
  "Eliges y ya está reservado. Sin descargarte nada, "
  "sin registrarte, sin escribir a nadie.",
  "Reserva desde el enlace",
  "Todo en una pantalla: servicio, precio, hora y sitio. Eliges y listo."),

 (16, "C"): (
  "Graduación sin llamar a nadie",
  "La semana de las graduaciones se llena todo y contestar al teléfono "
  "es imposible para ellas y para ti. Miras quién tiene hueco ese día, "
  "reservas peinado y maquillaje seguidos, y te olvidas. "
  "El aviso te llega el día antes.",
  "Reserva tu graduación",
  "Esa semana no hay quien coja el teléfono. Reserva peinado y maquillaje de una vez."),

 (17, "A"): (
  "Te encuentran en el buscador y en el mapa",
  "Hoy solo te conocen quienes ya te conocen. En ibook tu perfil sale "
  "cuando alguien busca tu servicio en tu zona, y también apareces "
  "en el mapa. La que vive tres calles más allá "
  "puede encontrarte sin que nadie se lo diga.",
  "Sal en el buscador",
  "Te encuentran quienes ya te conocen. En el mapa te encuentra el barrio entero."),

 (17, "B"): (
  "Clientas que no son del boca a boca",
  "El boca a boca es lento y se acaba: te trae a la prima y a la vecina "
  "y hasta ahí. Un perfil con precios, fotos y horas libres trabaja "
  "mientras tú duermes, y te trae gente que no conocía "
  "a nadie de tu círculo.",
  "Amplía tu círculo",
  "El boca a boca trae a la prima y a la vecina. El perfil trae al barrio."),

 (17, "C"): (
  "Pack de graduación en medio minuto",
  "Peinado y maquillaje suelen ir juntos, pero los tienes sueltos "
  "y la clienta reserva solo uno. Créalos como un pack con su precio "
  "y su duración real. Treinta segundos de trabajo "
  "y sube lo que deja cada cita.",
  "Crea tu pack",
  "Peinado y maquillaje juntos, con precio y duración. Treinta segundos."),

 (18, "A"): (
  "Semana Santa: cierra la agenda antes",
  "En Semana Santa medio barrio se va y la otra mitad quiere arreglarse "
  "antes de irse. Los dos días previos son de locos y el resto está muerto. "
  "Abre horas extra el martes y el miércoles, "
  "y bloquea lo que no vas a trabajar.",
  "Prepara tu Semana Santa",
  "Dos días de locos y el resto muerto. Se prepara antes, no se improvisa."),

 (18, "B"): (
  "Arréglate antes de irte",
  "Te vas de viaje en Semana Santa y quieres ir bien, pero lo dejas "
  "para el último día y ya no hay sitio en ningún lado. "
  "Mira ahora quién tiene hueco el martes o el miércoles "
  "y déjalo cerrado. Son dos toques.",
  "Reserva antes de Semana Santa",
  "El último día ya no hay sitio en ningún lado. Cierra la cita ahora."),

 (18, "C"): (
  "Temporada de bodas en dos pasos",
  "Para vivir del sector de bodas hacen falta dos cosas en el perfil: "
  "un servicio de novia con prueba incluida y su precio, "
  "y cinco fotos de recogidos de verdad. Lo montas en una tarde "
  "y trabaja todo el verano por ti.",
  "Monta tu servicio de novia",
  "Servicio con prueba y cinco fotos reales. Una tarde de trabajo, un verano de bodas."),
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


if __name__ == "__main__":
    main()
