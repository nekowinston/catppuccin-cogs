from redbot.core.bot import Red

from .hornytimer import HornyTimer


async def setup(bot: Red) -> None:
    await bot.add_cog(HornyTimer(bot))
