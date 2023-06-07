from discord import Message, TextChannel
from redbot.core import Config, commands


class AutoThreader(commands.Cog):
    """Create a thread for each message in a channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=8957967497, force_registration=True
        )
        self.config.register_guild(autothread_channels=[])

    @commands.Cog.listener()
    async def on_message(self, msg: Message) -> None:
        """Create a thread for each message in a channel."""
        guild = msg.guild

        # ignore DMs/own messages
        if guild is None or msg.author.bot:
            return

        watched_channels = await self.config.guild(guild).autothread_channels()

        if msg.channel.id in watched_channels:
            await self.create_thread(msg)

    @commands.guild_only()
    @commands.admin_or_permissions(manage_channels=True)
    @commands.command(name="autothread")
    async def autothread(self, ctx: commands.Context, channel: TextChannel) -> None:
        """Setup a channel for autothreading."""
        guild = ctx.guild

        if guild is None:
            return

        watched_channels = await self.config.guild(guild).autothread_channels()

        if channel.id in watched_channels:
            watched_channels.remove(channel.id)
            await ctx.send("Autothreading disabled for this channel.")
        else:
            watched_channels.append(channel.id)
            await ctx.send("Autothreading enabled for this channel.")

        await self.config.guild(guild).autothread_channels.set(watched_channels)

    async def create_thread(self, msg: Message) -> None:
        """Setup a channel for autothreading."""
        channel = msg.channel
        thread_title = (
            msg.content
            or f"{msg.author.display_name} on {msg.created_at.strftime('%H:%M %d/%m/%Y')}"
        )

        if isinstance(channel, TextChannel):
            thread = await channel.create_thread(name=thread_title, message=msg)
            msgs = [
                f"Hi {msg.author.mention}! I've created this thread for you.",
                "Please keep discussion in the thread.",
            ]
            await thread.send("\n".join(msgs))
