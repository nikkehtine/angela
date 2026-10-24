import random

from discord.ext import commands


def match_response(msg: str) -> str | None:
    msg = msg.lower()
    match msg:
        case "ping":
            return "Pong!"
        case "sus":
            return "Amongus"
        case "amongus" | "amogus":
            return "Sus"
        case (
            "oh shit i'm sorry"
            | "oh shit, i'm sorry"
            | "oh shit im sorry"
            | "oh shit, im sorry"
        ):
            return "Sorry for what?"
        case "sperma":
            return ":sweat_drops:"
        case _:
            return None


class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        funny_response = match_response(message.content)
        if funny_response:
            await message.channel.send(funny_response)

        if message.content.lower().startswith(
            "hello"
        ) or message.content.lower().startswith("hi"):
            hello = random.choice(["Hi", "Hello"])
            await message.channel.send(hello)


async def setup(bot: commands.Bot):
    await bot.add_cog(Greetings(bot))
