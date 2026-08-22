def en_mismo_servidor(ctx, uid):
    if not ctx.guild:
        return False
    return ctx.guild.get_member(int(uid)) is not None


def cantidad_valida(cantidad, minimo, maximo):
    try:
        cantidad = int(cantidad)
    except (ValueError, TypeError):
        return False
    return minimo <= cantidad <= maximo


def cantidad_positiva(cantidad):
    try:
        return int(cantidad) > 0
    except (ValueError, TypeError):
        return False


def tiene_dinero(econ, uid, cantidad):
    bolsillo = econ.get("usuarios", {}).get(str(uid), {}).get("bolsillo", 0)
    return bolsillo >= cantidad


def usuario_valido(ctx, uid):
    if not ctx.guild:
        return False
    return ctx.guild.get_member(int(uid)) is not None