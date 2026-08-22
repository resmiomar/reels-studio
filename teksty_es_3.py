#!/usr/bin/env python3
"""
Испанские тексты, партия третья: недели 19-29.

Летняя часть года. Тут меняется сама боль мастера: зимой она в пустом кресле,
летом - в том, что клиенты разъехались, а расходы остались. Тексты идут за
этим, а не повторяют январские слова другими буквами.

Про деньги в этой партии говорим прямо, потому что тема того требует:

    цена дня      делим месячную плату на тридцать - выходит меньше кофе.
                  Испанцу это понятно без объяснений.
    один салон    платит салон, а не каждый мастер отдельно. Для владельца
                  с пятью креслами это решающий довод.
    год за десять два месяца в подарок при годовой оплате.
    клиенту       приложение бесплатное, и это надо говорить вслух: люди
                  привыкли, что за запись где-то берут комиссию.

    python teksty_es_3.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PUT = os.path.join(HERE, "scenarii", "videos_es.json")

TEKSTY = {
 (19, "A"): (
  "Puentes y festivos: quién se queda",
  "Llega un puente y empieza el lío de quién trabaja y quién libra. "
  "Cada profesional marca sus días en su propia agenda y tú ves el puente entero "
  "en una pantalla. Si un día se queda sin nadie, lo ves antes "
  "y no el mismo lunes por la mañana.",
  "Organiza el puente",
  "Quién trabaja el puente y quién libra. Se ve en una pantalla, no en un grupo de WhatsApp."),

 (19, "B"): (
  "Duermes y la cita entra sola",
  "Las once y media de la noche es la hora a la que más gente reserva. "
  "Están en el sofá, se acuerdan y lo hacen en ese momento. "
  "Si en ese momento no pueden reservar, mañana ya se les ha olvidado. "
  "Tu agenda no duerme aunque tú sí.",
  "Que reserven de noche",
  "La gente reserva a las once y media de la noche. Si no puede, mañana ya no se acuerda."),

 (19, "C"): (
  "El cuadrante del equipo en un minuto",
  "Cuadrar turnos a mano son dos horas y siempre se cuela un error. "
  "Cada una marca sus horas, tú abres el mes y lo ves montado: "
  "quién entra, quién libra, dónde falta gente. "
  "Cambias lo que haga falta y todas lo ven al momento.",
  "Monta el cuadrante",
  "Dos horas cuadrando turnos, o un minuto mirando el mes ya montado."),

 (20, "A"): (
  "Bodas: reservas con un mes de margen",
  "En temporada de bodas la clienta cierra con semanas de antelación, "
  "y si tu agenda solo enseña los próximos quince días, no puede reservarte. "
  "Abre los meses de verano enteros. Ella cierra en mayo lo de agosto "
  "y tú ya sabes cómo viene el verano.",
  "Abre los meses de verano",
  "Si tu agenda llega a dos semanas, las bodas de agosto se van a otra."),

 (20, "B"): (
  "La prueba antes de la boda",
  "El día de tu boda no es día de experimentos. La prueba se hace semanas antes, "
  "con calma, para ver cómo aguanta el peinado y si el tono te convence. "
  "Reserva prueba y boda a la vez y las dos fechas quedan cerradas "
  "en el mismo minuto.",
  "Reserva prueba y boda",
  "El día de la boda no se prueba nada. La prueba va semanas antes."),

 (20, "C"): (
  "Pon la duración real de cada servicio",
  "Si un color son dos horas y en la agenda pone una, todo tu día va con retraso "
  "y la de las siete se queda esperando de pie. Escribe la duración de verdad, "
  "una sola vez. A partir de ahí la agenda se monta sola sin pisarse.",
  "Ajusta tus duraciones",
  "Una hora en la agenda y dos en la silla. Así se cae el día entero."),

 (21, "A"): (
  "Cuánto te cuesta al día, échalo",
  "Divide lo que pagas al mes entre treinta días. Sale menos que un café "
  "con leche. Y con una sola clienta que te llegue por el perfil "
  "ya está pagado el mes entero. Lo demás son citas que antes "
  "no te habrían encontrado.",
  "Calcula tu día",
  "Menos que un café al día. Una clienta nueva paga el mes entero."),

 (21, "B"): (
  "Un precio para todo el salón",
  "Otras herramientas cobran por cada profesional, y con cinco personas "
  "la factura se dispara. Aquí paga el salón, no cada silla. "
  "Da igual que seáis tres o diez: el precio es el mismo "
  "y no sube porque crezcas.",
  "Un precio, todo el equipo",
  "No se paga por cabeza. Tres o diez, el salón paga lo mismo."),

 (21, "C"): (
  "El precio se ve antes de reservar",
  "Preguntar cuánto cuesta da corte, y hay quien prefiere no ir "
  "antes que preguntar. En ibook el precio está al lado del servicio, "
  "con la duración. Sabes lo que vas a pagar y cuánto vas a tardar "
  "antes de reservar nada.",
  "Mira precios en ibook",
  "Preguntar el precio da corte. Aquí está escrito al lado del servicio."),

 (22, "A"): (
  "Diez meses pagados, doce de uso",
  "Si pagas el año entero de una vez, dos meses te salen gratis. "
  "Sale a cuenta si ya sabes que vas a seguir, y te quitas "
  "el recibo mensual de la cabeza. Y si dejas de usarlo, "
  "te devolvemos lo que quede sin gastar.",
  "Mira el plan anual",
  "Pagas diez meses y usas doce. Y si lo dejas, te devolvemos lo que quede."),

 (22, "B"): (
  "Para ti, clienta, es gratis",
  "Reservar en ibook no te cuesta nada, ni ahora ni nunca. "
  "No hay comisión por reservar, ni recargo, ni suscripción. "
  "Pagas tu servicio a tu profesional como siempre, en su silla. "
  "La app la paga ella, no tú.",
  "Descarga ibook gratis",
  "Reservar no te cuesta nada. Pagas tu servicio donde siempre."),

 (22, "C"): (
  "El plan anual, sin letra pequeña",
  "Vamos con calma: pagas doce meses de golpe al precio de diez. "
  "No hay permanencia, no hay penalización, y si lo dejas a mitad "
  "te devolvemos la parte no usada. Eso es todo. "
  "No hay más condiciones escondidas.",
  "Mira las condiciones",
  "Doce meses al precio de diez. Sin permanencia y con devolución si lo dejas."),

 (23, "A"): (
  "Las graduaciones vienen en oleada",
  "No llegan repartidas: se juntan todas en dos semanas de junio. "
  "Si no lo preparas, dices que no a la mitad y trabajas hasta la noche "
  "con la otra mitad. Abre horas extra solo esos días "
  "y ponles precio de temporada.",
  "Prepara la oleada",
  "Las graduaciones se juntan en dos semanas. O las preparas, o las sufres."),

 (23, "B"): (
  "Gradúate peinada, no corriendo",
  "La semana de tu graduación está todo cogido, y las que se quedan libres "
  "son las horas malas. Mira ahora quién tiene sitio ese día, "
  "coge peinado y maquillaje seguidos y déjalo cerrado. "
  "Luego ya no hay dónde elegir.",
  "Reserva tu graduación",
  "Esa semana solo quedan las horas malas. Cierra la tuya ahora."),

 (23, "C"): (
  "Un día de boda, paso a paso",
  "Los días de boda son maratones: novia a las siete, madrina a las nueve, "
  "invitadas seguidas. Si cada servicio tiene su duración real en la agenda, "
  "el día se monta solo y no se pisa nada. "
  "Tú solo miras la pantalla y vas.",
  "Monta tu día de boda",
  "Novia a las siete y todo seguido. Con duraciones reales, el día no se cae."),

 (24, "A"): (
  "Te vas de vacaciones sin dar explicaciones",
  "Antes irte dos semanas era avisar a treinta personas una por una. "
  "Bloqueas las fechas y ya está: nadie puede reservar esos días "
  "y nadie te escribe preguntando. Vuelves, quitas el bloqueo "
  "y la agenda sigue viva.",
  "Bloquea tus vacaciones",
  "Bloqueas las fechas y desaparecen. Ni un mensaje preguntando."),

 (24, "B"): (
  "Vacaciones del equipo sin romper el salón",
  "En agosto se van todas por turnos y el salón no puede cerrar. "
  "Cada una marca sus semanas y tú ves el mes completo: "
  "dónde hay cobertura y qué días quedan pelados. "
  "Los arreglas en mayo, no el mismo día.",
  "Cuadra agosto ya",
  "Los días pelados de agosto se ven en mayo. En agosto ya no se arreglan."),

 (24, "C"): (
  "Vacaciones sin perder clientas",
  "El miedo de siempre: me voy dos semanas y cuando vuelvo se han ido a otra. "
  "Deja las fechas de la vuelta abiertas antes de irte. "
  "Quien te busque en agosto verá que el uno de septiembre estás "
  "y reservará ahí mismo.",
  "Abre tu vuelta",
  "Deja abiertas las fechas de la vuelta y reservarán mientras estás fuera."),

 (25, "A"): (
  "Los huecos de media mañana en verano",
  "En verano las mañanas se quedan muertas y las tardes revientan. "
  "Pon una oferta solo en las horas flojas: mismo servicio, "
  "un poco más barato de once a una. Quien tenga el día libre "
  "vendrá por la mañana y te llenará el hueco.",
  "Llena tus mañanas",
  "Mañanas muertas y tardes a tope. Una oferta solo en las horas flojas lo cambia."),

 (25, "B"): (
  "Un hueco para hoy en un minuto",
  "Se te ha liberado la tarde y te apetece arreglarte, "
  "pero llamar a cinco sitios preguntando por hoy es un suplicio. "
  "Filtra por hoy y ve quién tiene libre ahora mismo cerca de ti. "
  "Reservas y te vas.",
  "Busca hueco para hoy",
  "Filtras por hoy y ves quién tiene libre ahora mismo. Sin llamar a nadie."),

 (25, "C"): (
  "Así se llenan los huecos del salón",
  "Un hueco de tarde vacío es dinero que no vuelve. "
  "Cuando alguien cancela, ese hueco se libera solo en la app "
  "y aparece disponible para quien esté buscando. "
  "Muchas veces se llena antes de que te enteres.",
  "Recupera tus huecos",
  "Una cancelación libera el hueco sola. A veces se llena antes de que lo veas."),

 (26, "A"): (
  "Cuántas citas has hecho este mes",
  "Si te preguntan cuántas citas hiciste en junio, dices una cifra a ojo "
  "y te equivocas siempre. Está contado: citas del mes, comparación "
  "con el mes anterior y qué días fueron los buenos. "
  "Sin apuntar nada a mano.",
  "Mira tus números",
  "Cuántas citas hiciste este mes, contadas. No a ojo."),

 (26, "B"): (
  "Lo que has ganado se calcula solo",
  "Sumar la libreta a final de mes es media tarde y sale mal. "
  "Cada cita ya lleva su precio, así que el total está hecho: "
  "cuánto ha entrado, con qué servicios y en qué días. "
  "Lo miras en diez segundos.",
  "Mira tus ingresos",
  "Sumar la libreta a final de mes, o mirarlo hecho en diez segundos."),

 (26, "C"): (
  "Tu informe en dos toques",
  "No hace falta exportar nada ni pelearse con hojas de cálculo. "
  "Abres la app, tocas informes y ahí está el mes: "
  "citas, ingresos, servicios más pedidos y horas más flojas. "
  "Dos toques y lo tienes.",
  "Abre tus informes",
  "Ni hojas de cálculo ni exportar nada. Dos toques y ves el mes."),

 (27, "A"): (
  "Media ciudad de vacaciones, ¿y tú?",
  "En julio tus clientas de siempre están fuera y el día se queda a medias. "
  "Pero también hay gente que se queda y no sabe dónde ir. "
  "Si estás en el buscador con horas libres, "
  "esas son las que llenan tu semana muerta.",
  "Sal en el buscador",
  "Las tuyas están fuera, pero hay quien se queda y no sabe dónde ir."),

 (27, "B"): (
  "De viaje también se necesita peluquería",
  "Estás quince días fuera y se te queda el pelo imposible, "
  "pero no conoces a nadie en esa ciudad y no te fías. "
  "Busca por zona, mira trabajos y opiniones, "
  "y reserva con alguien que ya han probado otras.",
  "Busca donde estés",
  "Fuera de casa no conoces a nadie. Mira trabajos y opiniones antes de sentarte."),

 (27, "C"): (
  "Cierra el hueco de esta tarde",
  "Te ha cancelado la de las cinco y te queda un agujero. "
  "Pon una oferta solo para esa hora: se publica al momento "
  "y la ve quien esté buscando cita para hoy. "
  "Muchas veces se llena en menos de una hora.",
  "Publica tu hueco",
  "Te cancelan a las cinco. Pones oferta para esa hora y se llena antes de las cuatro."),

 (28, "A"): (
  "El martes muerto se arregla con una oferta",
  "Los martes de agosto no viene nadie y aun así abres. "
  "En vez de mirar la puerta, pon un precio distinto solo ese día. "
  "Quien tiene el martes libre y le sobra tiempo "
  "vendrá justo porque le sale mejor.",
  "Pon oferta de martes",
  "Abres el martes y no viene nadie. Un precio distinto solo ese día lo cambia."),

 (28, "B"): (
  "La carga del salón en verano",
  "En julio y agosto la carga baja, pero no baja igual todos los días. "
  "En el panel ves qué días de la semana aguantan y cuáles se hunden. "
  "Con eso ajustas turnos y no pagas horas "
  "de gente mirando la puerta.",
  "Mira tu carga de verano",
  "No todos los días bajan igual. Los flojos se ven en el panel y se ajustan."),

 (28, "C"): (
  "Profesional en tu ciudad de vacaciones",
  "Llegas a la playa y descubres que necesitas unas uñas para la boda del sábado. "
  "No conoces la ciudad ni a nadie. Buscas por zona, "
  "ves quién tiene hueco el viernes, miras sus trabajos y reservas. "
  "Cinco minutos.",
  "Busca en tu destino",
  "En una ciudad que no conoces, buscas por zona y ves trabajos antes de reservar."),

 (29, "A"): (
  "Tú en la playa, la agenda trabajando",
  "El domingo por la tarde estás en la toalla y no piensas en el trabajo. "
  "Mientras tanto tres personas han entrado en tu perfil "
  "y dos han reservado para la semana que viene. "
  "Lo ves cuando abres el móvil, y ya está hecho.",
  "Deja que reserven solas",
  "En la toalla el domingo, y dos citas cerradas para el lunes."),

 (29, "B"): (
  "Reserva de noche sin molestar a nadie",
  "Son las doce y te acuerdas de que necesitas cita. "
  "Escribir a esa hora da apuro y por la mañana se te olvidará. "
  "Entras, coges la hora que te viene bien y listo. "
  "Nadie recibe un mensaje a medianoche.",
  "Reserva a cualquier hora",
  "A las doce de la noche no se escribe a nadie. Pero sí se reserva."),
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
