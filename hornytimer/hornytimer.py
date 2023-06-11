import random
from datetime import datetime, timedelta
from typing import List, TypedDict

import discord
from discord import Guild, Interaction
from redbot.core import Config, app_commands, commands
from redbot.core.utils.chat_formatting import humanize_timedelta, pagify


class BonkImage(TypedDict):
    name: str
    url: str


class HornyTimer(commands.Cog):
    """Tracks how low your discord has managed to not be horny for."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=3849421352, force_registration=True
        )
        default_guild = {
            "last_horny": 0,
            "reset_count": 0,
            "bonk_images": [],
        }
        self.config.register_guild(**default_guild)

    @app_commands.command(name="resethornytimer")
    @app_commands.guild_only()
    async def reset(self, interaction: Interaction) -> None:
        """Reset the timer."""
        if not interaction.guild:
            return

        prev_timestamp = await self._get_last_horny(interaction.guild)

        await self.config.guild(interaction.guild).last_horny.set(
            datetime.now().timestamp()
        )
        await self.config.guild(interaction.guild).reset_count.set(
            (await self.config.guild(interaction.guild).reset_count()) + 1
        )

        embed = discord.Embed(
            title="Timer reset.",
            description=f"Timer reset. This discord managed to not be horny for {self._get_time_diff(prev_timestamp)}.",
        )

        image = await self._get_random_bonk_image(interaction.guild)
        if image:
            embed.set_image(url=image["url"])

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="checkhornytimer")
    @app_commands.guild_only()
    async def check_timer(self, interaction: Interaction) -> None:
        """Check for how long this Discord has managed to not be horny."""
        if not interaction.guild:
            return

        diff = self._get_time_diff(await self._get_last_horny(interaction.guild))
        await interaction.response.send_message(
            f"Timer hasn't been reset for {diff}. Good job everyone!"
        )

    @commands.group()
    @commands.guild_only()
    @commands.mod_or_permissions(manage_channels=True)
    async def bonkimage(self, _: commands.Context):
        """Manage bonk images."""

    @bonkimage.command(name="add")
    async def bonk_image_add(self, ctx: commands.Context, name: str, url: str) -> None:
        """Add a bonk image to the list of bonk images."""
        if not ctx.guild:
            return

        bonk_images = await self._get_bonk_images(ctx.guild)

        if any(image["name"] == name for image in bonk_images):
            await ctx.send("Bonk image with that name already exists.")
            return

        bonk_images.append({"name": name, "url": url})
        await self.config.guild(ctx.guild).bonk_images.set(bonk_images)

        await ctx.send("Bonk image added.")

    @bonkimage.command(name="remove")
    async def bonk_image_remove(self, ctx: commands.Context, name: str) -> None:
        """Remove a bonk image from the list of bonk images."""
        if not ctx.guild:
            return

        bonk_images = await self._get_bonk_images(ctx.guild)
        bonk_images = [image for image in bonk_images if image["name"] != name]
        await self.config.guild(ctx.guild).bonk_images.set(bonk_images)

        await ctx.send("Bonk image removed.")

    @bonkimage.command(name="list")
    async def bonk_image_list(self, ctx: commands.Context) -> None:
        """Remove a bonk image from the list of bonk images."""
        if not ctx.guild:
            return

        embed_list = []
        for image in await self._get_bonk_images(ctx.guild):
            embed_list.append(f"**{image['name']}** - <{image['url']}>")

        if len(embed_list) == 0:
            await ctx.send("No bonk images found.")
            return

        for page in pagify("\n".join(embed_list)):
            await ctx.send(page)

    def _get_time_diff(self, timestamp: float) -> str:
        return humanize_timedelta(
            timedelta=(timedelta(seconds=datetime.now().timestamp() - timestamp))
        )

    async def _get_last_horny(self, guild: Guild) -> float:
        return await self.config.guild(guild).last_horny()

    async def _get_reset_count(self, guild: Guild) -> int:
        return await self.config.guild(guild).reset_count()

    async def _get_bonk_images(self, guild: Guild) -> List[BonkImage]:
        return await self.config.guild(guild).bonk_images()

    async def _get_random_bonk_image(self, guild: Guild) -> BonkImage | None:
        bonk_images = await self._get_bonk_images(guild)
        try:
            return bonk_images[random.randint(0, len(bonk_images) - 1)]
        except:
            return None
