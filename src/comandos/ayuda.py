from discord.ext import commands

from utilidades.configuracion import cargar_config
from utilidades.embeds import crear_embed, responder


class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ayuda", description="Muestra la lista de comandos disponibles.")
    async def ayuda(self, ctx):
        if ctx.interaction: await ctx.defer()
        config = cargar_config()
        prefijo = config["prefijo"]

        embed = crear_embed(
            titulo="📚 Comandos Disponibles",
            descripcion=(
                f"**Economía**\n"
                f"`{prefijo}bolsillo` - Ver tu dinero en efectivo\n"
                f"`{prefijo}balance [usuario]` - Ver balance completo\n"
                f"`{prefijo}trabajo` - Gana dinero trabajando\n"
                f"`{prefijo}diario` - Reclama tu recompensa diaria\n"
                f"`{prefijo}depositar [cantidad|todo]` - Deposita en el banco\n"
                f"`{prefijo}retirar [cantidad|todo]` - Retira del banco\n"
                f"`{prefijo}pagar [usuario] [cantidad]` - Paga a otro usuario\n"
                f"\n"
                f"**Juegos**\n"
                f"`{prefijo}robar [usuario]` - Roba a otro usuario\n"
                f"`{prefijo}ruleta [cantidad]` - Juega a la ruleta\n"
                f"\n"
                f"**Perfil**\n"
                f"`{prefijo}perfil [usuario]` - Ver perfil de un usuario\n"
                f"`{prefijo}ranking` - Ver el ranking de riqueza\n"
                f"\n"
                f"**Ayuda**\n"
                f"`{prefijo}ayuda` - Ver esta lista de comandos\n"
                f"\n"
                f"**Staff**\n"
                f"`{prefijo}staff [usuario]` - Balance de un usuario\n"
                f"`{prefijo}dar [usuario] [cantidad]` - Dar dinero\n"
                f"`{prefijo}quitar [usuario] [cantidad]` - Quitar dinero\n"
                f"`{prefijo}establecer [usuario] [bolsillo/banco] [cantidad]` - Establecer cantidad\n"
                f"`{prefijo}resetear [usuario]` - Resetear economía\n"
                f"`{prefijo}estadísticas [usuario]` - Estadísticas de un usuario\n"
            ),
            color=0x00aaff,
        )
        await responder(ctx, embed=embed)
