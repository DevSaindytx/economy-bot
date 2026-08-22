import discord

from utilidades.configuracion import cargar_config


def crear_embed(titulo, descripcion, color=0x00ff00):
    config = cargar_config()
    embed = discord.Embed(title=titulo, description=descripcion, color=color)
    embed.set_footer(text=config["bot"]["pie"])
    embed.timestamp = discord.utils.utcnow()
    return embed


def embed_error(mensaje):
    return crear_embed("❌ Error", mensaje, 0xff0000)


def embed_exito(mensaje):
    return crear_embed("✅ Éxito", mensaje, 0x00ff00)


async def responder(ctx, mensaje=None, embed=None):
    if embed is None:
        if mensaje and mensaje.startswith("❌"):
            embed = embed_error(mensaje)
        elif mensaje and mensaje.startswith("✅"):
            embed = embed_exito(mensaje)
        else:
            embed = crear_embed("ℹ️ Información", mensaje or "")
    if ctx.interaction:
        interaction = ctx.interaction
        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.followup.send(embed=embed)
    else:
        await ctx.send(embed=embed)