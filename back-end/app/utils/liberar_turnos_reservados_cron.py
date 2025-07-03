def liberar_turnos_expirados():
    ahora = datetime.utcnow()
    vencidos = Turno.query.filter(
        Turno.estado == "pendiente",
        Turno.fecha_expiracion < ahora,
        Turno.estado_pago == "pendiente"
    )

    for t in vencidos:
        t.estado = "libre"
        t.fecha_expiracion = None

    db.session.commit()
