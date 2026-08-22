import os
import traceback

import discord
from discord.ext import commands

from utilidades.configuracion import cargar_config
from utilidades.embeds import crear_embed, responder
from comandos.economia import Economia
from comandos.juegos import Juegos
from comandos.perfil import Perfil
from comandos.ayuda import Ayuda
from comandos.staff import Staff
from comandos.ranking import Ranking
from eventos.errores import ManejadorErrores


def _guardar_error(error):
    texto = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    print(texto)
    try:
        ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos", "errores.log")
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(texto + chr(10) + "=" * 60 + chr(10))
    except OSError:
        pass


class BotEconomia(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        config = cargar_config()
        super().__init__(command_prefix=config["prefijo"], intents=intents, help_command=None, *args, **kwargs)

        self.config = config

    async def setup_hook(self):
        await self.add_cog(Economia(self))
        await self.add_cog(Juegos(self))
        await self.add_cog(Perfil(self))
        await self.add_cog(Ayuda(self))
        await self.add_cog(Staff(self))
        await self.add_cog(Ranking(self))
        await self.add_cog(ManejadorErrores(self))

    async def on_ready(self):
        print(f"✅ {self.user} está listo.")
        try:
            servidor_id = self.config.get("servidor_id")
            if servidor_id:
                guild = discord.Object(id=servidor_id)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print("✅ Comandos sincronizados en el servidor.")
                self.tree.clear_commands(guild=None)
                await self.tree.sync()
        except Exception as e:
            _guardar_error(e)

        canal_id = self.config["canal_id"]
        canal = self.get_channel(canal_id)
        if canal:
            embed = crear_embed(
                titulo="🟢 Bot en línea",
                descripcion=f"{self.user.mention} ya está operativo. ¡Usa `{self.config['prefijo']}ayuda` para ver los comandos!",
                color=0x00ff00,
            )
            await canal.send(embed=embed)

    async def on_application_command_error(self, ctx, error):
        _guardar_error(error)
        if ctx.response.is_done():
            await ctx.followup.send(embed=crear_embed("❌ Error", "Ocurrió un error inesperado. Inténtalo de nuevo.", 0xff0000))
        else:
            await ctx.response.send_message(embed=crear_embed("❌ Error", "Ocurrió un error inesperado. Inténtalo de nuevo.", 0xff0000))


if __name__ == "__main__":
    config = cargar_config()
    bot = BotEconomia()
    bot.run(config["token"])