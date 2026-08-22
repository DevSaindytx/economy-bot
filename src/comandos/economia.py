import random

import discord
from discord.ext import commands

from utilidades.configuracion import cargar_config
from utilidades.economia import (
    cargar_economia,
    guardar_economia,
    obtener_bolsillo,
    obtener_banco,
    establecer_bolsillo,
    establecer_banco,
    inicializar_usuario,
)
from utilidades.embeds import crear_embed, responder
from utilidades.cooldowns import en_cooldown, aplicar_cooldown


class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="bolsillo", description="Muestra tu dinero en el bolsillo.")
    async def bolsillo(self, ctx, usuario: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        config = cargar_config()
        econ = cargar_economia()
        if usuario is None:
            usuario = ctx.author
        uid = str(usuario.id)
        inicializar_usuario(econ, uid, config)
        bolsillo = obtener_bolsillo(econ, uid)
        embed = crear_embed(
            titulo=f"👛 Bolsillo de {usuario.display_name}",
            descripcion=f"Tienes **{bolsillo}** {config['moneda']['simbolo']}.",
            color=0x00ff00,
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="balance", description="Muestra tu balance completo.")
    async def balance(self, ctx, usuario: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        config = cargar_config()
        econ = cargar_economia()
        if usuario is None:
            usuario = ctx.author
        uid = str(usuario.id)
        inicializar_usuario(econ, uid, config)
        bolsillo = obtener_bolsillo(econ, uid)
        banco = obtener_banco(econ, uid)
        total = bolsillo + banco
        embed = crear_embed(
            titulo=f"💰 Balance de {usuario.display_name}",
            descripcion=(
                f"**👛 Bolsillo:** {bolsillo} {config['moneda']['simbolo']}\n"
                f"**🏦 Banco:** {banco} {config['moneda']['simbolo']}\n"
                f"**📊 Total:** {total} {config['moneda']['simbolo']}"
            ),
            color=0x00aaff,
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="trabajo", description="Trabaja y gana dinero.")
    async def trabajo(self, ctx):
        if ctx.interaction: await ctx.defer()
        config = cargar_config()
        econ = cargar_economia()
        uid = str(ctx.author.id)
        inicializar_usuario(econ, uid, config)

        if await en_cooldown(ctx, econ, "trabajo", config["trabajo"]["cooldown"]):
            return

        recompensa = random.randint(config["trabajo"]["minimo"], config["trabajo"]["maximo"])
        establecer_bolsillo(econ, uid, obtener_bolsillo(econ, uid) + recompensa)
        econ["usuarios"][uid]["estadisticas"]["trabajos"] += 1
        econ["usuarios"][uid]["estadisticas"]["ganado"] += recompensa
        guardar_economia(econ)
        aplicar_cooldown(econ, uid, "trabajo")

        embed = crear_embed(
            titulo="💼 Trabajo completado",
            descripcion=f"Has ganado **{recompensa}** {config['moneda']['simbolo']}.",
            color=0x00ff00,
        )
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="diario", description="Reclama tu recompensa diaria.")
    async def diario(self, ctx):
        if ctx.interaction: await ctx.defer()
        config = cargar_config()
        econ = cargar_economia()
        uid = str(ctx.author.id)
        inicializar_usuario(econ, uid, config)

        if await en_cooldown(ctx, econ, "diario", config["diario"]["cooldown"]):
            return

        recompensa = random.randint(config["diario"]["minimo"], config["diario"]["maximo"])
        establecer_bolsillo(econ, uid, obtener_bolsillo(econ, uid) + recompensa)
        econ["usuarios"][uid]["estadisticas"]["diarios"] += 1
        econ["usuarios"][uid]["estadisticas"]["ganado"] += recompensa
        guardar_economia(econ)
        aplicar_cooldown(econ, uid, "diario")

        embed = crear_embed(
            titulo="📅 Recompensa diaria",
            descripcion=f"Has reclamado **{recompensa}** {config['moneda']['simbolo']}.",
            color=0x00ff00,
        )
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="depositar", description="Deposita dinero en el banco.")
    async def depositar(self, ctx, cantidad: int):
        if ctx.interaction: await ctx.defer()
        config = cargar_config()
        econ = cargar_economia()
        uid = str(ctx.author.id)
        inicializar_usuario(econ, uid, config)

        if cantidad <= 0:
            await responder(ctx, crear_embed("❌ Cantidad inválida", "La cantidad debe ser mayor que cero.", 0xff0000))
            return

        if cantidad > obtener_bolsillo(econ, uid):
            await responder(ctx, crear_embed("❌ Saldo insuficiente", "No tienes suficiente dinero en tu bolsillo.", 0xff0000))
            return

        maximo_banco = config["economia"]["maximo_banco"]
        if obtener_banco(econ, uid) + cantidad > maximo_banco:
            await responder(ctx, crear_embed("❌ Límite superado", f"Superarías el máximo del banco ({maximo_banco}).", 0xff0000))
            return

        establecer_bolsillo(econ, uid, obtener_bolsillo(econ, uid) - cantidad)
        establecer_banco(econ, uid, obtener_banco(econ, uid) + cantidad)
        guardar_economia(econ)

        embed = crear_embed(
            titulo="🏦 Depósito",
            descripcion=f"Has depositado **{cantidad}** {config['moneda']['simbolo']} al banco.",
            color=0x0000ff,
        )
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="retirar", description="Retira dinero del banco.")
    async def retirar(self, ctx, cantidad: str):
        if ctx.interaction: await ctx.defer()
        config = cargar_config()
        econ = cargar_economia()
        uid = str(ctx.author.id)
        inicializar_usuario(econ, uid, config)

        if cantidad == "todo":
            cantidad = obtener_banco(econ, uid)
        else:
            try:
                cantidad = int(cantidad)
            except ValueError:
                await responder(ctx, crear_embed("❌ Cantidad inválida", "Cantidad inválida.", 0xff0000))
                return

        if cantidad <= 0:
            await responder(ctx, crear_embed("❌ Cantidad inválida", "La cantidad debe ser mayor que cero.", 0xff0000))
            return

        if cantidad > obtener_banco(econ, uid):
            await responder(ctx, crear_embed("❌ Saldo insuficiente", "No tienes suficiente dinero en el banco.", 0xff0000))
            return

        maximo_bolsillo = config["economia"]["maximo_bolsillo"]
        if obtener_bolsillo(econ, uid) + cantidad > maximo_bolsillo:
            await responder(ctx, crear_embed("❌ Límite superado", f"Superarías el máximo del bolsillo ({maximo_bolsillo}).", 0xff0000))
            return

        establecer_banco(econ, uid, obtener_banco(econ, uid) - cantidad)
        establecer_bolsillo(econ, uid, obtener_bolsillo(econ, uid) + cantidad)
        guardar_economia(econ)

        embed = crear_embed(
            titulo="🏦 Retiro",
            descripcion=f"Has retirado **{cantidad}** {config['moneda']['simbolo']} del banco.",
            color=0x0000ff,
        )
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="pagar", description="Paga dinero a otro usuario.")
    async def pagar(self, ctx, usuario: discord.Member, cantidad: int):
        if ctx.interaction: await ctx.defer()
        config = cargar_config()
        econ = cargar_economia()
        autor_id = str(ctx.author.id)
        destino_id = str(usuario.id)
        inicializar_usuario(econ, autor_id, config)
        inicializar_usuario(econ, destino_id, config)

        if cantidad <= 0:
            await responder(ctx, crear_embed("❌ Cantidad inválida", "La cantidad debe ser mayor que cero.", 0xff0000))
            return

        if cantidad > obtener_bolsillo(econ, autor_id):
            await responder(ctx, crear_embed("❌ Saldo insuficiente", "No tienes suficiente dinero en tu bolsillo.", 0xff0000))
            return

        establecer_bolsillo(econ, autor_id, obtener_bolsillo(econ, autor_id) - cantidad)
        establecer_bolsillo(econ, destino_id, obtener_bolsillo(econ, destino_id) + cantidad)
        econ["usuarios"][autor_id]["estadisticas"]["gastado"] += cantidad
        guardar_economia(econ)

        embed = crear_embed(
            titulo="💸 Pago realizado",
            descripcion=f"Has pagado **{cantidad}** {config['moneda']['simbolo']} a **{usuario.display_name}**.",
            color=0x00ff00,
        )
        await responder(ctx, embed=embed)