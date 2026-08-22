import discord
from discord.ext import commands

from utilidades.configuracion import cargar_config
from utilidades.economia import cargar_economia
from utilidades.embeds import crear_embed, responder


class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ranking", description="Muestra el ranking de los usuarios más ricos del servidor.")
    async def ranking(self, ctx):
        if ctx.interaction: await ctx.defer()
        econ = cargar_economia()
        config = cargar_config()

        usuarios = econ.get("usuarios", {})
        datos = []
        for uid, datos_usuario in usuarios.items():
            total = datos_usuario.get("bolsillo", 0) + datos_usuario.get("banco", 0)
            datos.append((uid, total))

        datos.sort(key=lambda x: x[1], reverse=True)

        if not datos:
            await responder(ctx, crear_embed("❌ Sin datos", "No hay usuarios con dinero en el servidor.", 0xff0000))
            return

        lineas = []
        for i, (uid, total) in enumerate(datos[:10], start=1):
            miembro = ctx.guild.get_member(int(uid)) if ctx.guild else None
            nombre = miembro.display_name if miembro else "Usuario Desconocido"
            lineas.append(f"`{i}.` **{nombre}** — {total} {config['moneda']['simbolo']}")

        embed = crear_embed(
            titulo="🏆 Ranking de Riqueza",
            descripcion="\n".join(lineas),
            color=0xffd700,
        )
        await responder(ctx, embed=embed)