#!/usr/bin/env python3
"""
Испанские тексты, партия первая: недели 1-8.

Как написано. Не переводом с русского, а заново, испанской речью. Владелец
про это сказал прямо на казахском: носитель видит машинный перевод с первой
строки, и «казахи сразу судят». Испанцы судят так же.

Что учтено в языке:

    tuteo        обращаемся на «ты». В испанской бьюти-среде «usted» звучит
                 как письмо из налоговой, а не как разговор с коллегой.
    España       «móvil», а не «celular»; «agenda», а не «calendario»;
                 «cita», а не «turno». Латиноамериканские слова выдали бы,
                 что текст писали не здесь.
    reales       «autónoma», «cuota de autónomos», «vuelta al cole» - то,
                 чем живёт испанский мастер, а не общие слова про бизнес.

Строение каждого ролика то же, что в готовых языках:

    крючок    неудобный вопрос или узнаваемая картина, первые три секунды
    боль      во что это обходится - деньгами или нервами
    решение   что делает ibook, одним понятным действием
    призыв    короткий, без восклицаний

Длина текста держится около 55-65 слов: на испанском это 22-26 секунд,
а именно столько досматривают в ленте.

    python teksty_es_1.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PUT = os.path.join(HERE, "scenarii", "videos_es.json")

# Ключ - неделя и слот. Значения: крючок, текст, призыв, подпись.
TEKSTY = {
 (1, "B"): (
  "Buscas hora y nadie coge el teléfono",
  "Quieres cortarte el pelo esta semana y empiezas la ronda: llamas, no contestan, "
  "escribes por Instagram, te leen y no responden. Al final vas donde sea. En ibook "
  "ves quién tiene hueco hoy, a qué hora y por cuánto, y reservas en dos toques. "
  "Sin llamar, sin esperar respuesta.",
  "Busca hueco en ibook",
  "Llamar, esperar, insistir. Y al final ir donde sea porque no te queda tiempo. "
  "En ibook ves los huecos libres de hoy con precio y reservas en dos toques."),

 (1, "C"): (
  "Tu perfil listo en diez minutos",
  "Dices que no tienes tiempo para montar el perfil, y llevas medio año perdiendo "
  "clientas por eso. Son diez minutos: foto, lista de servicios con precios, horario "
  "y tres trabajos tuyos. Ya está. A partir de ahí la clienta te encuentra sola y "
  "reserva sin escribirte.",
  "Monta tu perfil hoy",
  "Diez minutos: foto, servicios con precio, horario y tres trabajos. "
  "A partir de ahí te encuentran y reservan solas."),

 (2, "A"): (
  "Te escriben a las once de la noche",
  "Tu clienta se acuerda de la cita cuando ya está en la cama. Te escribe a las once, "
  "tú lo ves por la mañana, y para entonces ya ha reservado en otro sitio. "
  "En ibook tu agenda está abierta de noche igual que de día: ella elige la hora "
  "y se apunta sola, tú lo ves al despertarte.",
  "Abre tu agenda día y noche",
  "La gente decide de noche y reserva de noche. Si tu agenda duerme, la cita se va a otra."),

 (2, "B"): (
  "Una llamada perdida es una clienta perdida",
  "Estás con las manos en un tinte y suena el teléfono. No lo coges, claro. "
  "Esa persona no vuelve a llamar: llama a la siguiente de la lista. "
  "Con ibook no hace falta que cojas nada. Ella entra, ve tu hueco de las seis "
  "y lo reserva mientras tú terminas tranquila.",
  "Que reserven sin llamarte",
  "Con las manos ocupadas no se coge el teléfono. Y quien no te encuentra, encuentra a otra."),

 (2, "C"): (
  "Dos pasos y el salón entero dentro",
  "Montar el salón en ibook son dos cosas: das de alta el local con sus servicios, "
  "y añades a tu equipo. Cada profesional tiene su agenda, pero tú ves todas juntas "
  "en una pantalla. Quién está libre, quién va lleno, cuánto ha hecho cada una este mes.",
  "Da de alta tu salón",
  "El local, el equipo, y todas las agendas en una pantalla. Dos pasos."),

 (3, "A"): (
  "Todo el salón en una pantalla",
  "Cuando llevas cinco profesionales, saber quién está libre a las cinco es un "
  "interrogatorio. Preguntas a una, preguntas a otra, y la clienta esperando al "
  "teléfono. En ibook abres la agenda del salón y lo ves todo de golpe: "
  "huecos, reservas y quién puede cogerla ahora mismo.",
  "Mira tu salón de un vistazo",
  "Cinco agendas en una pantalla. Quién está libre ahora, sin preguntar a nadie."),

 (3, "B"): (
  "Reservar sin hablar por teléfono",
  "Hay gente a la que llamar le da pereza y punto. Prefiere no ir antes que "
  "descolgar el teléfono. Esa clienta existe y es la mitad de tu barrio. "
  "En ibook elige servicio, ve el precio, coge la hora que le va bien "
  "y reserva sin decir una palabra.",
  "Reserva sin llamar",
  "A mucha gente le cuesta llamar. Con ibook eligen hora y precio sin hablar con nadie."),

 (3, "C"): (
  "Precios claros en cinco minutos",
  "Lo más pesado del día es contestar veinte veces cuánto vale un balayage. "
  "Súbelo una vez: cada servicio con su precio y su duración. "
  "Quien entra en tu perfil ya sabe lo que cuesta y cuánto tarda, "
  "y te escribe solo quien viene decidida.",
  "Sube tus precios hoy",
  "Escribe tus precios una vez y deja de contestar lo mismo veinte veces al día."),

 (4, "A"): (
  "Treinta días gratis, sin tarjeta",
  "El primer mes es gratis y no te pedimos tarjeta. Ni número, ni datos bancarios, "
  "ni permanencia. Montas el perfil, recibes reservas treinta días y decides. "
  "Si no te encaja, lo dejas y no pasa nada. Nadie te va a cobrar por sorpresa.",
  "Empieza gratis 30 días",
  "Treinta días sin pagar y sin tarjeta. Pruebas, y si no te sirve lo dejas."),

 (4, "B"): (
  "Lo tuve montado en diez minutos",
  "No hay que aprender nada. Pones tu nombre, subes una foto, escribes los servicios "
  "que haces con su precio, marcas los días que trabajas. Diez minutos y ya recibes "
  "reservas. Si te lías con algo, escríbenos y te lo dejamos hecho.",
  "Móntalo en diez minutos",
  "Nombre, foto, servicios, horario. Diez minutos y ya te reservan."),

 (4, "C"): (
  "Busca el servicio, no el nombre",
  "No sabes cómo se llama la que hace buenas uñas cerca de tu casa, "
  "y por eso llevas dos meses sin arreglártelas. En ibook no buscas nombres: "
  "pones el servicio que quieres, miras quién lo hace cerca, "
  "ves precios y trabajos, y reservas con la que te guste.",
  "Busca por servicio en ibook",
  "No hace falta saber nombres. Pones el servicio, ves quién lo hace cerca y reservas."),

 (5, "A"): (
  "San Valentín se llena la semana antes",
  "El catorce de febrero todo el mundo quiere venir el mismo día, y tú acabas "
  "diciendo que no a la mitad. Abre las horas ahora: quien se organiza reserva "
  "en enero, y tú llegas a la semana con la agenda hecha "
  "en vez de contestando mensajes a la carrera.",
  "Abre tus horas de febrero",
  "En San Valentín todas quieren el mismo día. Abre las horas ahora y llega con la agenda hecha."),

 (5, "B"): (
  "Este catorce regálate la cita",
  "Llevas meses diciendo que la semana que viene te arreglas el pelo, "
  "y la semana que viene nunca llega. Reservar tarda menos que pensarlo: "
  "miras quién tiene hueco el catorce, ves el precio, coges la hora "
  "y ya está apuntada. Sin llamar a nadie.",
  "Reserva tu cita ya",
  "Llevas meses aplazándolo. Mira quién tiene hueco el catorce y resérvalo en dos toques."),

 (5, "C"): (
  "El recordatorio se manda solo",
  "Cada tarde repasas la agenda de mañana y escribes uno por uno para confirmar. "
  "Media hora al día en eso. En ibook el recordatorio sale solo el día antes, "
  "y la clienta confirma o cambia desde el mismo mensaje. Tú no escribes nada.",
  "Deja de recordar a mano",
  "Media hora al día escribiendo recordatorios. O ninguna, porque salen solos."),

 (6, "A"): (
  "Dos clientas a la misma hora",
  "Apuntaste una en la libreta, la otra por Instagram, y las dos aparecen a las cinco. "
  "Alguien se va enfadada y no vuelve. Cuando la agenda es una sola, "
  "esa hora se cierra en cuanto la cogen: no hay forma de apuntar a dos.",
  "Una sola agenda",
  "La libreta y el Instagram no se hablan entre ellos. Una agenda única no deja huecos dobles."),

 (6, "B"): (
  "La recepción a tope de gente",
  "Sábado a mediodía: dos esperando de pie, el teléfono sonando y alguien "
  "preguntando precios en la puerta. Tu recepcionista no da abasto. "
  "Si las citas entran solas por la app, en recepción queda lo que de verdad "
  "necesita a una persona: recibir y cobrar.",
  "Quita trabajo a recepción",
  "El sábado a mediodía no hay manos para el teléfono. Que las citas entren solas."),

 (6, "C"): (
  "Sube tus trabajos de San Valentín",
  "Las fotos buenas de febrero se quedan en tu galería y no las ve nadie. "
  "Súbelas al perfil: quien entre en marzo verá lo que sabes hacer, "
  "no una lista de precios a secas. Es un minuto por foto "
  "y trabaja para ti todo el año.",
  "Sube tus trabajos hoy",
  "Las fotos buenas no sirven de nada en la galería del móvil. En el perfil sí."),

 (7, "A"): (
  "Que avise la app, no tú",
  "Escribir a cada una el día antes es trabajo invisible: nadie te lo paga "
  "y te come la tarde. El aviso automático sale a la hora que tú digas, "
  "con el nombre del servicio y la dirección. Y si alguien no puede, "
  "lo cambia desde ahí mismo y el hueco vuelve a quedar libre.",
  "Activa los avisos",
  "El aviso del día antes se manda solo. Y si cambian, el hueco vuelve a abrirse."),

 (7, "B"): (
  "El aviso llega y no te lías",
  "Reservaste hace tres semanas y se te ha ido de la cabeza. "
  "El día antes te llega el aviso con la hora, la dirección y lo que te vas a hacer. "
  "Si te ha surgido algo, cambias la cita desde el mismo mensaje. "
  "Sin llamar, sin quedar mal.",
  "Reserva y olvídate",
  "El aviso llega solo el día antes. Y si no puedes, lo cambias desde ahí."),

 (7, "C"): (
  "Quién trabajó y cuánto en San Valentín",
  "Pasa el catorce y no sabes bien quién llevó más carga ni quién tuvo huecos. "
  "En el panel del salón lo ves por persona: cuántas citas hizo cada una, "
  "cuánto entró, qué horas quedaron vacías. Con eso repartes mejor "
  "el turno del año que viene.",
  "Mira el informe del salón",
  "Quién llevó la carga y quién tuvo huecos. En números, no de memoria."),

 (8, "A"): (
  "Tus trabajos en el perfil, no en el chat",
  "Cada vez que alguien pregunta te toca buscar la foto en el móvil "
  "y mandarla por privado. Y al siguiente igual. Súbelas una vez al perfil: "
  "quien te encuentre verá tus mejores trabajos sin preguntarte nada, "
  "y llegará sabiendo lo que quiere.",
  "Sube tus trabajos",
  "Buscar la foto y mandarla por privado, otra vez. O tenerla en el perfil para siempre."),

 (8, "B"): (
  "El precio se ve antes de entrar",
  "Cuando el precio no está escrito, mucha gente ni pregunta: se va a otro perfil "
  "donde sí lo pone. No es que sea caro, es que no quiere el paseo de preguntar. "
  "Ponlo claro y te escribirá solo quien ya está de acuerdo.",
  "Pon tus precios visibles",
  "Sin precio a la vista, la mitad ni pregunta. Ponlo y te escriben las decididas."),

 (8, "C"): (
  "Lee las opiniones antes de reservar",
  "Ir a alguien nuevo da respeto, sobre todo si es color. "
  "En ibook las opiniones son de clientas que fueron de verdad, "
  "con la foto del trabajo al lado. Lees tres, miras las fotos "
  "y ya sabes si quieres sentarte en esa silla.",
  "Mira las opiniones en ibook",
  "Opiniones de gente que fue de verdad, con foto del trabajo. Lees tres y lo tienes claro."),
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
    gotovo = sum(1 for v in d if v.get("vo", "").strip())
    print(f"  добавлено текстов: {n}")
    print(f"  испанский готов: {gotovo} из 156, осталось {156 - gotovo}")
    dl = [len(v["vo"].split()) for v in d if v.get("vo", "").strip()]
    print(f"  длина текста: в среднем {sum(dl)/len(dl):.0f} слов, от {min(dl)} до {max(dl)}")


if __name__ == "__main__":
    main()
