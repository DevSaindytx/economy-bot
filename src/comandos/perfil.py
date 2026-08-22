import discord
from discord.ext import commands

from utilidades.configuracion import cargar_config
from utilidades.economia import (
    cargar_economia,
    obtener_bolsillo,
    obtener_banco,
    inicializar_usuario,
)
from utilidades.embeds import crear_embed, responder


class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="perfil", description="Muestra el perfil de un usuario.")
    async def perfil(self, ctx, usuario: discord.Member = None):
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
            titulo=f"👤 Perfil de {usuario.display_name}",
            descripcion=(
                f"**Bolsillo:** {bolsillo} {config['moneda']['simbolo']}\n"
                f"**Banco:** {banco} {config['moneda']['simbolo']}\n"
                f"**Total:** {total} {config['moneda']['simbolo']}"
            ),
            color=0x00aaff,
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        await responder(ctx, embed=embed)
