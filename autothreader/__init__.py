from redbot.core.bot import Red

from .autothreader import AutoThreader


async def setup(bot: Red) -> None:
    await bot.add_cog(AutoThreader(bot))
