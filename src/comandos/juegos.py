import random

import discord
from discord.ext import commands

from utilidades.configuracion import cargar_config
from utilidades.economia import (
    cargar_economia,
    guardar_economia,
    obtener_bolsillo,
    sumar_dinero,
    restar_dinero,
    inicializar_usuario,
)
from utilidades.embeds import crear_embed, responder
from utilidades.cooldowns import en_cooldown, aplicar_cooldown


class Juegos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="robo", aliases=["robar"], description="Roba dinero del bolsillo de otro usuario.")
    async def robo(self, ctx, usuario: discord.Member):
        if ctx.interaction: await ctx.defer()
        config = cargar_config()
        econ = cargar_economia()
        ladron_id = str(ctx.author.id)
        victima_id = str(usuario.id)
        inicializar_usuario(econ, ladron_id, config)
        inicializar_usuario(econ, victima_id, config)

        if ladron_id == victima_id:
            await responder(ctx, crear_embed("❌ Robo inválido", "No puedes robarte a ti mismo.", 0xff0000))
            return

        if not ctx.guild or usuario.id not in [m.id for m in ctx.guild.members]:
            await responder(ctx, crear_embed("❌ Usuario inválido", "El usuario no está en este servidor.", 0xff0000))
            return

        if await en_cooldown(ctx, econ, "robo", config["robo"]["cooldown"]):
            return

        dinero_victima = obtener_bolsillo(econ, victima_id)
        if dinero_victima <= 0:
            await responder(ctx, crear_embed("❌ Sin dinero", "El usuario no tiene dinero en el bolsillo.", 0xff0000))
            return

        if random.randint(1, 100) <= config["robo"]["probabilidad_exito"]:
            porcentaje = random.randint(config["robo"]["porcentaje_minimo"], config["robo"]["porcentaje_maximo"])
            cantidad_robo = int(dinero_victima * porcentaje / 100)
            sumar_dinero(econ, ladron_id, cantidad_robo)
            restar_dinero(econ, victima_id, cantidad_robo)
            econ["usuarios"][ladron_id]["estadisticas"]["robos"] += 1
            econ["usuarios"][ladron_id]["estadisticas"]["ganado"] += cantidad_robo
            guardar_economia(econ)
            embed = crear_embed(
                titulo="🥷 Robo exitoso",
                descripcion=f"🦹 Has robado **{cantidad_robo}** {config['moneda']['simbolo']} a {usuario.display_name}.",
                color=0x00ff00,
            )
        else:
            penalizacion = config["robo"]["penalizacion_fallo"]
            restar_dinero(econ, ladron_id, penalizacion)
            econ["usuarios"][ladron_id]["estadisticas"]["gastado"] += penalizacion
            guardar_economia(econ)
            embed = crear_embed(
                titulo="🥷 Robo fallido",
                descripcion=f"❌ Fallaste. Has perdido **{penalizacion}** {config['moneda']['simbolo']}.",
                color=0xff0000,
            )

        aplicar_cooldown(econ, ladron_id, "robo")
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="ruleta", description="Juega a la ruleta con una apuesta.")
    async def ruleta(self, ctx, cantidad: int):
        if ctx.interaction: await ctx.defer()
        config = cargar_config()
        econ = cargar_economia()
        uid = str(ctx.author.id)
        inicializar_usuario(econ, uid, config)

        if cantidad < config["ruleta"]["apuesta_minima"] or cantidad > config["ruleta"]["apuesta_maxima"]:
            await responder(ctx, crear_embed("❌ Apuesta inválida", f"La apuesta debe estar entre {config['ruleta']['apuesta_minima']} y {config['ruleta']['apuesta_maxima']}.", 0xff0000))
            return

        if obtener_bolsillo(econ, uid) < cantidad:
            await responder(ctx, crear_embed("❌ Saldo insuficiente", "No tienes suficiente dinero en tu bolsillo.", 0xff0000))
            return

        if await en_cooldown(ctx, econ, "ruleta", config["ruleta"]["cooldown"]):
            return

        restar_dinero(econ, uid, cantidad)
        econ["usuarios"][uid]["estadisticas"]["gastado"] += cantidad
        guardar_economia(econ)

        probabilidades = config["ruleta"]["probabilidades"]
        claves = list(probabilidades.keys())
        pesos = list(probabilidades.values())
        resultado = random.choices(claves, weights=pesos)[0]

        if resultado == "perder":
            embed = crear_embed(
                titulo="🎡 Ruleta",
                descripcion=f"🍀 ¡Perdiste **{cantidad}** {config['moneda']['simbolo']}!",
                color=0xff0000,
            )
        else:
            multiplicador = {"x2": 2, "x3": 3, "x5": 5, "jackpot": 10}[resultado]
            ganancia = cantidad * multiplicador
            sumar_dinero(econ, uid, ganancia)
            econ["usuarios"][uid]["estadisticas"]["ruleta"] += 1
            econ["usuarios"][uid]["estadisticas"]["ganado"] += ganancia
            guardar_economia(econ)
            embed = crear_embed(
                titulo="🎡 Ruleta",
                descripcion=f"🍀 ¡Ganaste **{ganancia}** {config['moneda']['simbolo']}!",
                color=0x00ff00,
            )

        aplicar_cooldown(econ, uid, "ruleta")
        await responder(ctx, embed=embed)