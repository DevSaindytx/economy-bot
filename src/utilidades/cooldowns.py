from datetime import datetime, timedelta, timezone

from utilidades.embeds import crear_embed, responder


async def en_cooldown(ctx, econ, accion, cooldown_segundos):
    uid = str(ctx.author.id)
    ahora = datetime.now(timezone.utc)
    usuario = econ.get("usuarios", {}).get(uid, {})
    cd = usuario.get("cooldowns", {})
    ultimo_str = cd.get(accion)

    if ultimo_str:
        try:
            ultima = datetime.fromisoformat(ultimo_str)
            restante = (ultima + timedelta(seconds=cooldown_segundos)) - ahora
            if restante > timedelta(0):
                segundos = int(restante.total_seconds())
                mins, secs = divmod(segundos, 60)
                embed = crear_embed(
                    "⏳ Cooldown",
                    f"Espera **{mins}m {secs}s** para usar `{accion}`.",
                    0xffaa00,
                )
                await responder(ctx, embed=embed)
                return True
        except ValueError:
            pass

    return False


def aplicar_cooldown(econ, uid, accion):
    uid = str(uid)
    ahora = datetime.now(timezone.utc)
    usuario = econ.setdefault("usuarios", {}).setdefault(uid, {})
    if "cooldowns" not in usuario:
        usuario["cooldowns"] = {}
    usuario["cooldowns"][accion] = ahora.isoformat()