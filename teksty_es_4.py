#!/usr/bin/env python3
"""
Испанские тексты, партия четвёртая: недели 29-41.

Осенняя часть. Здесь другая боль: не пустота, а хаос. Все вернулись разом,
поток пошёл, и мастер тонет в переписках, накладках и забытых мелочах.

Что важно в этой части:

    vuelta al cole   в Испании это сильное общее переживание, конец августа
                     и первая неделя сентября. Волна детских стрижек.
    la libreta       бумажный блокнот у испанских мастеров живуч. Не смеёмся
                     над ним, а показываем, чем он опасен: он теряется.
    tres mensajerías WhatsApp, Instagram и телефон одновременно - обычная
                     картина, и именно она съедает вечер.

    python teksty_es_4.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PUT = os.path.join(HERE, "scenarii", "videos_es.json")

TEKSTY = {
 (29, "C"): (
  "Tres reglas para contestar sin morir",
  "Contestar mensajes te come el día. Tres reglas: precios escritos en el perfil, "
  "para no repetirlos nunca; horas visibles, para no negociar cada cita; "
  "y enlace de reserva en la respuesta, en vez de proponer horas a mano. "
  "Con eso el chat baja a la mitad.",
  "Aplica las tres reglas",
  "Precios escritos, horas visibles y un enlace. El chat baja a la mitad."),

 (30, "A"): (
  "La clienta vuelve sola",
  "Cuando alguien queda contenta, quiere volver, pero luego pasan seis semanas "
  "y se le olvida. Si en la app tiene tu perfil guardado y su última cita a la vista, "
  "repetir es un toque. Vuelve porque le resulta fácil, "
  "no porque tú la persigas.",
  "Haz fácil que vuelvan",
  "Quedan contentas y aun así no vuelven. Porque volver cuesta más de lo que parece."),

 (30, "B"): (
  "Repetir cita en un toque",
  "La clienta abre su última visita, toca repetir y elige el día. "
  "No hay que explicar otra vez qué se hizo ni cuánto duró: "
  "está guardado. Para ella son cinco segundos "
  "y para ti es una cita más sin escribir nada.",
  "Activa la repetición",
  "Repetir la cita anterior en un toque. Sin explicar nada de nuevo."),

 (30, "C"): (
  "Recupera clientas en dos pasos",
  "Abre la lista y ordénala por última visita. Coge las diez primeras, "
  "las que hace más de dos meses que no vienen, y mándales una hora concreta "
  "de esta semana. Dos pasos. Suele volver una de cada tres, "
  "y eso ya es media semana salvada.",
  "Recupera tu lista",
  "Ordenas por última visita, mandas diez horas concretas. Vuelve una de cada tres."),

 (31, "B"): (
  "Corte de vuelta al cole, antes de la avalancha",
  "La última semana de agosto todas las madres del barrio quieren "
  "lo mismo el mismo día. Si esperas, te quedan las horas de las nueve "
  "de la mañana del viernes. Mira ahora quién tiene sitio "
  "y déjalo cerrado con dos toques.",
  "Reserva antes del cole",
  "La última semana de agosto no queda nada. Cierra el corte ahora."),

 (31, "C"): (
  "Tu perfil listo para septiembre en tres pasos",
  "Antes de que llegue la avalancha: uno, sube el corte infantil "
  "como servicio propio con su precio. Dos, abre horas de tarde "
  "esa última semana. Tres, pon dos fotos de peinados de niño. "
  "Diez minutos y septiembre entra ordenado.",
  "Prepara septiembre",
  "Servicio infantil, horas de tarde y dos fotos. Diez minutos."),

 (32, "A"): (
  "Abre el otoño ahora, no en octubre",
  "En septiembre la gente vuelve a organizarse y planifica el trimestre entero. "
  "Si tu agenda solo llega a quince días, esa planificación te deja fuera. "
  "Abre octubre y noviembre hoy: quien organiza su vida en septiembre "
  "te reserva en septiembre.",
  "Abre octubre y noviembre",
  "En septiembre la gente planifica el trimestre. Si tu agenda no llega, te deja fuera."),

 (32, "B"): (
  "Buscas profesional: enseña horario y condiciones",
  "Los anuncios de empleo del sector dicen todos lo mismo y no dicen nada. "
  "Enseña la agenda real del salón: cuántas citas entran, qué horario se hace, "
  "cómo se reparten. Quien busca sitio quiere ver eso, "
  "no un texto de siempre.",
  "Enseña tu salón de verdad",
  "Los anuncios se parecen todos. La agenda real no se puede fingir."),

 (32, "C"): (
  "Todo el equipo en un solo perfil",
  "El salón tiene un perfil y dentro está cada profesional con lo suyo: "
  "sus servicios, sus horas, sus trabajos. La clienta entra por el salón "
  "y elige con quién quiere ir. Si su habitual no tiene hueco, "
  "ve a las compañeras en la misma pantalla.",
  "Monta el perfil del salón",
  "Un perfil, todo el equipo dentro. Si una no tiene hueco, se ve a las demás."),

 (33, "A"): (
  "La libreta se ha quedado en casa",
  "Sales de casa, llegas al salón y la libreta está en la mesa de la cocina. "
  "Hoy trabajas de memoria y rezando. Cuando la agenda está en el móvil "
  "eso no puede pasar: la abres desde donde estés, "
  "incluso desde el autobús.",
  "Lleva la agenda encima",
  "La libreta se queda en casa. El móvil, no."),

 (33, "B"): (
  "Pierdes la libreta, pierdes el negocio",
  "Ahí están todos los nombres, los teléfonos y quién viene mañana. "
  "Si se moja, se pierde o alguien se la lleva, no hay copia. "
  "En la app está guardado fuera de tu móvil: "
  "cambias de teléfono y sigue todo ahí.",
  "Pon a salvo tu agenda",
  "Una libreta no tiene copia. Si se pierde, se pierde entera."),

 (33, "C"): (
  "Pasar la libreta al móvil, en una tarde",
  "No hace falta meterlo todo. Copia solo las clientas que vienen a menudo: "
  "nombre, teléfono y qué se hace. Son cuarenta o cincuenta, "
  "y con una tarde lo tienes. El resto se va añadiendo "
  "solo, según vayan reservando.",
  "Pasa tu libreta hoy",
  "No hace falta meterlo todo. Las cuarenta habituales, y el resto entra solo."),

 (34, "A"): (
  "Cierra recepción y las citas siguen entrando",
  "A las ocho se va la recepcionista y hasta mañana el teléfono no existe. "
  "Esas horas son justo cuando la gente decide. "
  "Con la agenda abierta en la app, las citas de la noche entran igual "
  "y por la mañana están ahí esperando.",
  "No cierres tu agenda",
  "Recepción cierra a las ocho. La gente decide a las once."),

 (34, "B"): (
  "Reservas tú, sin esperar a nadie",
  "No hay que llamar en horario comercial, ni esperar a que abran, "
  "ni que te devuelvan la llamada. Entras cuando puedes, "
  "eliges lo que quieres y la hora que te encaja, y ya está reservado. "
  "Todo el proceso son dos minutos.",
  "Reserva cuando quieras",
  "Sin llamar en horario comercial ni esperar a que te devuelvan la llamada."),

 (34, "C"): (
  "Cita del niño antes del cole, en dos pasos",
  "Entre el trabajo y la casa no hay hueco para andar llamando. "
  "Buscas corte infantil cerca, miras qué tardes de esta semana quedan libres "
  "y reservas. Dos pasos desde el móvil, "
  "mientras esperas en la fila del súper.",
  "Reserva el corte del niño",
  "Corte infantil cerca, tarde libre, reservado. Dos pasos desde la cola del súper."),

 (35, "A"): (
  "El primer mes es gratis, no arriesgas nada",
  "No hay tarjeta, no hay permanencia, no hay cobro sorpresa. "
  "Montas el perfil, trabajas treinta días con él y decides con datos, "
  "no con promesas: cuántas citas te llegaron, cuánto tiempo te ahorraste. "
  "Si no compensa, lo dejas.",
  "Prueba 30 días gratis",
  "Sin tarjeta y sin permanencia. Decides con lo que veas en treinta días."),

 (35, "B"): (
  "Está en App Store y en Google Play",
  "Se descarga como cualquier app, gratis y en un minuto. "
  "Buscas ibook, la instalas y ya puedes mirar profesionales cerca de ti. "
  "No hace falta registrarse para mirar: "
  "solo cuando quieras reservar de verdad.",
  "Descarga ibook",
  "Gratis en App Store y Google Play. Puedes mirar sin registrarte."),

 (35, "C"): (
  "Mira qué le falta a tu perfil",
  "La app te dice qué tienes flojo: faltan fotos, falta el precio "
  "de tres servicios, no tienes ninguna opinión. "
  "Son avisos concretos, no consejos vagos. "
  "Arreglas los tres primeros y tu perfil cambia de aspecto.",
  "Revisa tu perfil",
  "Avisos concretos: qué falta y dónde. No consejos generales."),

 (36, "A"): (
  "Todos han vuelto y la ola llega de golpe",
  "La primera semana de septiembre entra el mes entero en tres días. "
  "Si contestas a mano, pierdes la mitad por no llegar. "
  "Ten las horas abiertas y los precios puestos "
  "antes de que empiece, no durante.",
  "Prepárate para septiembre",
  "El mes entero entra en tres días. Si contestas a mano, pierdes la mitad."),

 (36, "B"): (
  "Vuelve con tu profesional de siempre",
  "Después del verano el pelo pide una cita urgente "
  "y tu peluquera de siempre está a tope. "
  "Abre su perfil, mira los huecos reales de la semana "
  "y coge el primero que te sirva. Sin insistir por WhatsApp.",
  "Vuelve a tu sitio",
  "Después del verano está todo a tope. Mira los huecos reales y coge el primero."),

 (36, "C"): (
  "Sube precios de otoño en dos pasos",
  "Subir precios da respeto, pero cambiar la lista no debería. "
  "Abres servicios, editas el importe y se aplica desde el día que digas. "
  "Las citas ya reservadas mantienen su precio, "
  "así que nadie se lleva una sorpresa.",
  "Actualiza tus precios",
  "Cambias el importe y se aplica desde el día que elijas. Lo ya reservado no cambia."),

 (37, "A"): (
  "Dos personas a la misma hora, imposible",
  "El error más caro es apuntar a dos en el mismo hueco: "
  "una se va enfadada y cuenta por qué. Con una agenda única "
  "la hora se cierra en cuanto la cogen. "
  "No es que sea difícil equivocarse: es que no se puede.",
  "Una agenda, sin choques",
  "El hueco se cierra en cuanto lo cogen. No se puede apuntar a dos."),

 (37, "B"): (
  "Toda la plantilla en una pantalla",
  "Con cuatro profesionales, saber quién tiene libre el jueves "
  "es preguntar cuatro veces. En la vista de equipo lo ves de golpe: "
  "las cuatro columnas, las horas ocupadas y los huecos. "
  "Colocas a la clienta sin levantarte.",
  "Mira a tu equipo junto",
  "Cuatro agendas en columnas. Colocas la cita sin preguntar a nadie."),

 (37, "C"): (
  "Cómo se quitan las citas pisadas",
  "Las citas se pisan por dos motivos: duraciones mal puestas "
  "y reservas apuntadas fuera de la app. Arregla las duraciones "
  "según lo que tardas de verdad y mete todo en un solo sitio. "
  "Con eso desaparecen casi todas.",
  "Quita los choques",
  "Duraciones reales y una sola agenda. Los choques se acaban solos."),

 (38, "A"): (
  "Todo el chat en un sitio",
  "Hoy hablas con clientas por WhatsApp, por Instagram y por teléfono, "
  "y siempre se te pierde algo. Cuando escriben dentro de la app, "
  "el mensaje llega junto a su ficha: sabes quién es, "
  "qué se hizo y cuándo viene.",
  "Junta tus conversaciones",
  "Tres mensajerías y siempre se pierde algo. En un sitio, no."),

 (38, "B"): (
  "Escríbele desde la propia app",
  "¿Quieres avisar de que llegas diez minutos tarde? "
  "Escribes desde la cita, y ella lo ve junto a tu reserva. "
  "No hace falta tener su número ni buscar la conversación "
  "entre cien chats.",
  "Escribe desde la cita",
  "Un mensaje pegado a la reserva. Sin buscar el chat entre cien."),

 (38, "C"): (
  "Cómo acordarte de cada clienta",
  "Nadie recuerda el tono exacto de treinta personas. "
  "Después de cada cita escribe dos líneas en su ficha: "
  "qué se usó y qué dijo ella. La próxima vez lo abres "
  "y pareces tener memoria de elefante.",
  "Escribe dos líneas",
  "Dos líneas después de cada cita. La próxima vez pareces tener memoria de elefante."),

 (39, "A"): (
  "Tus habituales, con todo su historial",
  "Las clientas fijas son el negocio, pero su historia vive "
  "en tu cabeza y en trozos de conversación. "
  "En su ficha está cada visita: qué se hizo, cuándo y por cuánto. "
  "Cuatro años de relación en una pantalla.",
  "Mira sus fichas",
  "Cada visita guardada: qué, cuándo y por cuánto. Sin fiarlo a la memoria."),

 (39, "B"): (
  "Lo del último día lo recuerda la app",
  "«¿Qué te puse la última vez?» es una pregunta que resta. "
  "Abre la ficha antes de que se siente y ahí está: "
  "servicio, producto, tiempo y lo que anotaste. "
  "Empiezas la conversación sabiendo, no preguntando.",
  "Abre la ficha antes",
  "Preguntar qué se hizo la última vez resta. Estar mirándolo, suma."),

 (39, "C"): (
  "Repetir cita, tres toques",
  "Abres tu última visita, tocas repetir, eliges día. Ya está. "
  "No hay que buscar el perfil, ni recordar el nombre del servicio, "
  "ni preguntar el precio. Tres toques desde la cola del autobús.",
  "Repite tu cita",
  "Tu última visita, repetir, elegir día. Tres toques."),

 (40, "A"): (
  "Miras los números y sabes qué cambiar",
  "Sin datos, cambiar cosas es adivinar. Con el mes delante ves "
  "qué servicio deja más, qué día flojea siempre "
  "y a qué hora no viene nadie. "
  "Cambias una cosa cada mes y en medio año se nota.",
  "Mira tu mes",
  "Qué servicio deja más y qué día flojea. Cambias una cosa al mes."),

 (40, "B"): (
  "Informe del salón: quién va lleno y quién no",
  "En el panel del salón está cada profesional con sus números: "
  "citas hechas, ingresos, horas libres. Se ve enseguida "
  "quién no da abasto y quién tiene huecos, "
  "y con eso repartes el trabajo sin discutir.",
  "Abre el panel del salón",
  "Quién no da abasto y quién tiene huecos. En números, no en discusiones."),

 (40, "C"): (
  "Repasa tu mes en cinco minutos",
  "Una vez al mes, siéntate cinco minutos con los números. "
  "Mira tres cosas: el servicio que más deja, el día más flojo "
  "y cuántas clientas nuevas entraron. "
  "Con eso ya sabes dónde tocar el mes que viene.",
  "Repasa tu mes",
  "Cinco minutos al mes: servicio que más deja, día más flojo, clientas nuevas."),

 (41, "A"): (
  "Las mañanas vacías tienen arreglo",
  "De diez a doce no entra nadie y aun así estás allí. "
  "Crea una oferta que solo exista en esas horas: "
  "quien trabaja por turnos o libra entre semana "
  "vendrá por la mañana justo porque le sale mejor.",
  "Llena tus mañanas",
  "De diez a doce no entra nadie. Una oferta solo en esas horas lo cambia."),

 (41, "B"): (
  "Un hueco de mañana ahora mismo",
  "Tienes la mañana libre y te vendría bien arreglarte, "
  "pero das por hecho que no habrá sitio. "
  "Filtra por hoy y por la mañana: casi siempre hay huecos "
  "que nadie ve porque nadie los busca.",
  "Mira los huecos de hoy",
  "Casi siempre hay huecos de mañana. No los ve nadie porque nadie los busca."),

 (41, "C"): (
  "Quién está parada, en treinta segundos",
  "Miras la pantalla del salón y ves las columnas vacías. "
  "Si una tiene tres huecos seguidos y otra va llena, "
  "mueves una cita y arreglas el día. "
  "Treinta segundos, sin preguntar a nadie.",
  "Mira quién está parada",
  "Columnas vacías a la vista. Mueves una cita y el día se arregla."),
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
