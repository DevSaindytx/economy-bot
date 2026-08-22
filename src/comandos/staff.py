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
    sumar_dinero,
    restar_dinero,
    inicializar_usuario,
    registrar_accion_staff,
)
from utilidades.embeds import crear_embed, responder


class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _verificar(self, ctx):
        config = cargar_config()
        roles_staff = config.get("staff", {}).get("roles", [])
        return any(rol.id in roles_staff for rol in ctx.author.roles)

    @commands.hybrid_command(name="staff", description="Muestra el balance de un usuario.")
    async def staff(self, ctx, usuario: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        if not await self._verificar(ctx):
            await responder(ctx, crear_embed("❌ Sin permisos", "No tienes permisos de staff.", 0xff0000))
            return
        if usuario is None:
            usuario = ctx.author
        econ = cargar_economia()
        config = cargar_config()
        uid = str(usuario.id)
        inicializar_usuario(econ, uid, config)
        embed = crear_embed(
            titulo=f"👤 Balance de {usuario.display_name}",
            descripcion=f"**Bolsillo:** {obtener_bolsillo(econ, uid)} {config['moneda']['simbolo']}\n**Banco:** {obtener_banco(econ, uid)} {config['moneda']['simbolo']}",
            color=0x00aaff,
        )
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="dar", description="Da dinero a un usuario.")
    async def dar(self, ctx, usuario: discord.Member, cantidad: int):
        if ctx.interaction: await ctx.defer()
        if not await self._verificar(ctx):
            await responder(ctx, crear_embed("❌ Sin permisos", "No tienes permisos de staff.", 0xff0000))
            return
        config = cargar_config()
        econ = cargar_economia()
        uid = str(usuario.id)
        inicializar_usuario(econ, uid, config)
        if cantidad <= 0:
            await responder(ctx, crear_embed("❌ Cantidad inválida", "La cantidad debe ser mayor que cero.", 0xff0000))
            return
        sumar_dinero(econ, uid, cantidad)
        econ["usuarios"][uid]["estadisticas"]["ganado"] += cantidad
        guardar_economia(econ)
        registrar_accion_staff(ctx.author.id, uid, "dar", cantidad, f"Da {cantidad} a {usuario.display_name}")
        await self._enviar_registro(ctx, f"💸 {ctx.author.display_name} dio {cantidad} {config['moneda']['simbolo']} a {usuario.display_name}")
        embed = crear_embed(
            titulo="✅ Dinero entregado",
            descripcion=f"Has dado **{cantidad}** {config['moneda']['simbolo']} a {usuario.display_name}.",
            color=0x00ff00,
        )
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="quitar", description="Quita dinero a un usuario.")
    async def quitar(self, ctx, usuario: discord.Member, cantidad: int):
        if ctx.interaction: await ctx.defer()
        if not await self._verificar(ctx):
            await responder(ctx, crear_embed("❌ Sin permisos", "No tienes permisos de staff.", 0xff0000))
            return
        config = cargar_config()
        econ = cargar_economia()
        uid = str(usuario.id)
        inicializar_usuario(econ, uid, config)
        if cantidad <= 0:
            await responder(ctx, crear_embed("❌ Cantidad inválida", "La cantidad debe ser mayor que cero.", 0xff0000))
            return
        restar_dinero(econ, uid, cantidad)
        econ["usuarios"][uid]["estadisticas"]["gastado"] += cantidad
        guardar_economia(econ)
        registrar_accion_staff(ctx.author.id, uid, "quitar", cantidad, f"Quita {cantidad} a {usuario.display_name}")
        await self._enviar_registro(ctx, f"💸 {ctx.author.display_name} quitó **{cantidad}** {config['moneda']['simbolo']} a {usuario.display_name}")
        embed = crear_embed(
            titulo="✅ Dinero quitado",
            descripcion=f"Has quitado **{cantidad}** {config['moneda']['simbolo']} a {usuario.display_name}.",
            color=0x00ff00,
        )
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="establecer", description="Establece el bolsillo o banco de un usuario.")
    async def establecer(self, ctx, usuario: discord.Member, ubicacion: str, cantidad: int):
        if ctx.interaction: await ctx.defer()
        if not await self._verificar(ctx):
            await responder(ctx, crear_embed("❌ Sin permisos", "No tienes permisos de staff.", 0xff0000))
            return
        config = cargar_config()
        econ = cargar_economia()
        uid = str(usuario.id)
        inicializar_usuario(econ, uid, config)
        if ubicacion not in ("bolsillo", "banco"):
            await responder(ctx, crear_embed("❌ Ubicación inválida", "Usa `bolsillo` o `banco`.", 0xff0000))
            return
        if cantidad < 0:
            await responder(ctx, crear_embed("❌ Cantidad inválida", "La cantidad no puede ser negativa.", 0xff0000))
            return
        if ubicacion == "bolsillo":
            establecer_bolsillo(econ, uid, cantidad)
        else:
            establecer_banco(econ, uid, cantidad)
        guardar_economia(econ)
        registrar_accion_staff(ctx.author.id, uid, "establecer", cantidad, f"Establece {ubicacion} a {cantidad}")
        await self._enviar_registro(ctx, f"⚙️ {ctx.author.display_name} estableció el {ubicacion} de {usuario.display_name} a **{cantidad}** {config['moneda']['simbolo']}")
        embed = crear_embed(
            titulo="✅ Cantidad establecida",
            descripcion=f"Has establecido el {ubicacion} de {usuario.display_name} a **{cantidad}** {config['moneda']['simbolo']}.",
            color=0x00ff00,
        )
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="resetear", description="Resetea la economía de un usuario.")
    async def resetear(self, ctx, usuario: discord.Member):
        if ctx.interaction: await ctx.defer()
        if not await self._verificar(ctx):
            await responder(ctx, crear_embed("❌ Sin permisos", "No tienes permisos de staff.", 0xff0000))
            return
        config = cargar_config()
        econ = cargar_economia()
        uid = str(usuario.id)
        inicializar_usuario(econ, uid, config)
        dinero_inicial = config["economia"]["dinero_inicial"]
        establecer_bolsillo(econ, uid, dinero_inicial)
        establecer_banco(econ, uid, 0)
        guardar_economia(econ)
        registrar_accion_staff(ctx.author.id, uid, "resetear", None, f"Resetea economía a {dinero_inicial}")
        await self._enviar_registro(ctx, f"🔄 {ctx.author.display_name} reseteó la economía de {usuario.display_name}")
        embed = crear_embed(
            titulo="🔄 Economía reseteada",
            descripcion=f"Has reseteado la economía de {usuario.display_name}.",
            color=0xffaa00,
        )
        await responder(ctx, embed=embed)

    @commands.hybrid_command(name="estadísticas", description="Muestra las estadísticas de un usuario.")
    async def estadisticas(self, ctx, usuario: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        if not await self._verificar(ctx):
            await responder(ctx, crear_embed("❌ Sin permisos", "No tienes permisos de staff.", 0xff0000))
            return
        if usuario is None:
            usuario = ctx.author
        econ = cargar_economia()
        config = cargar_config()
        uid = str(usuario.id)
        inicializar_usuario(econ, uid, config)
        stats = econ["usuarios"][uid]["estadisticas"]
        embed = crear_embed(
            titulo=f"📊 Estadísticas de {usuario.display_name}",
            descripcion=(
                f"**Bolsillo:** {obtener_bolsillo(econ, uid)} {config['moneda']['simbolo']}\n"
                f"**Banco:** {obtener_banco(econ, uid)} {config['moneda']['simbolo']}\n"
                f"**Ganado:** {stats['ganado']} {config['moneda']['simbolo']}\n"
                f"**Gastado:** {stats['gastado']} {config['moneda']['simbolo']}\n"
                f"**Robos:** {stats['robos']}\n"
                f"**Ruleta:** {stats['ruleta']}\n"
                f"**Trabajos:** {stats['trabajos']}\n"
                f"**Diarios:** {stats['diarios']}"
            ),
            color=0x00ccff,
        )
        await responder(ctx, embed=embed)

    async def _enviar_registro(self, ctx, mensaje):
        config = cargar_config()
        canal_id = config.get("staff", {}).get("canal_registros_id")
        if canal_id:
            canal = self.bot.get_channel(canal_id)
            if canal:
                embed = crear_embed("📋 Registro Staff", mensaje, 0xffaa00)
                await canal.send(embed=embed)