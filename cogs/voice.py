import asyncio

import discord
import yt_dlp
from discord.ext import commands

ytdl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "js_runtimes": {"deno": {}},
    "remote-components": "ejs:github",
    "quiet": True,
    "nowarnings": True,
    "nocheckcertificate": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}
ytdl = yt_dlp.YoutubeDL(ytdl_opts)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume=volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, options="-vn"), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command(name="play")
    async def play(self, ctx, url):
        print(f"url: {url}")
        if not url and ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

            await ctx.send(f"Now playing: {player.title}")

    @commands.command(name="pause")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send(f":pause_button: Stopped playback (by {ctx.author})")

    @commands.command(name="resume")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send(f":arrow_forward: Resumed playback (by {ctx.author})")
        else:
            await ctx.send("Excuse me. There's nothing to unpause.")

    @commands.command(name="stop", description="Stops the music and clears the queue")
    async def stop(self, ctx, self_request=False):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        if not self_request:
            await ctx.send(f"Stopped playback (by {ctx.author})")

    @commands.command(name="leave")
    async def leave(self, ctx):
        if ctx.voice_client:
            await self.stop(ctx, self_request=True)
            await ctx.voice_client.disconnect()
            await ctx.send(f"Stopped playback and left the channel (by {ctx.author})")

    @play.before_invoke
    @join.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(
                    "I can't fulfill your request. You are not connected to any voice channel."
                )
                raise commands.CommandError(
                    "Requester is not connected to a voice channel"
                )
        elif ctx.voice_client.is_playing():
            ctx.voice_client.leave()


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
