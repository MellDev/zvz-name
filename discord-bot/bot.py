import logging
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")


class ZvZBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logging.info("Slash commands synced for guild %s", GUILD_ID)
        else:
            await self.tree.sync()
            logging.info("Global slash commands synced")

    async def on_ready(self) -> None:
        assert self.user is not None
        logging.info("Bot online as %s (%s)", self.user, self.user.id)


bot = ZvZBot()


@bot.command(name="ping")
async def ping_command(ctx: commands.Context) -> None:
    latency_ms = round(bot.latency * 1000)
    await ctx.reply(f"Pong! {latency_ms}ms")


@bot.tree.command(name="ping", description="Mostra a latencia do bot.")
async def ping_slash(interaction: discord.Interaction) -> None:
    latency_ms = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! {latency_ms}ms", ephemeral=True)


@bot.tree.command(name="zvz", description="Mostra um aviso basico de ZvZ.")
@app_commands.describe(mensagem="Mensagem para enviar no canal")
async def zvz_slash(interaction: discord.Interaction, mensagem: str = "Formando ZvZ!") -> None:
    await interaction.response.send_message(mensagem)


def main() -> None:
    if not TOKEN:
        raise RuntimeError("Defina DISCORD_BOT_TOKEN no arquivo .env")

    bot.run(TOKEN)


if __name__ == "__main__":
    main()
