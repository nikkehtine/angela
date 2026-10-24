import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN") or ""

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


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
        case _:
            return None


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    funny_response = match_response(message.content)
    if funny_response:
        await message.channel.send(funny_response)

    if message.content.lower().startswith(
        "hello"
    ) or message.content.lower().startswith("hi"):
        hello = random.choice(["Hi", "Hello"])
        await message.channel.send(hello)


client.run(TOKEN)
