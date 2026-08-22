import os
import traceback

from discord.ext import commands

from utilidades.embeds import crear_embed, responder


def _ruta_log():
    directorio = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(directorio, "datos", "errores.log")


def _guardar_traceback(error):
    texto = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    print(texto)
    try:
        with open(_ruta_log(), "a", encoding="utf-8") as f:
            f.write(texto + "\n" + "=" * 60 + "\n")
    except OSError:
        pass


class ManejadorErrores(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.HybridCommandError) and error.original:
            error = error.original
        _guardar_traceback(error)
        if isinstance(error, commands.MissingRequiredArgument):
            await self._enviar_error(ctx, f"Falta el argumento **{error.param.name}**.")
            return
        if isinstance(error, commands.BadArgument):
            await self._enviar_error(ctx, "Argumento inválido.")
            return
        if isinstance(error, commands.MissingPermissions):
            await self._enviar_error(ctx, "No tienes permisos para usar este comando.")
            return
        if isinstance(error, commands.CheckFailure):
            await self._enviar_error(ctx, "No puedes usar este comando.")
            return
        if isinstance(error, commands.CommandOnCooldown):
            await self._enviar_error(ctx, f"Comando en cooldown. Espera **{int(error.retry_after)}s**.")
            return
        await self._enviar_error(ctx, "Ocurrió un error inesperado. Inténtalo de nuevo.")

    async def _enviar_error(self, ctx, mensaje):
        embed = crear_embed("❌ Error", mensaje, 0xff0000)
        try:
            await responder(ctx, embed=embed)
        except Exception as e:
            _guardar_traceback(e)