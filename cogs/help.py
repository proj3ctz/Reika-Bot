import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def custom_help(self, ctx):
        embed = discord.Embed(
            title="Commands Help",
            color=discord.Color.from_str('#020A1D')
            )
        bot_avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else None
        if bot_avatar_url:
            embed.set_thumbnail(url=bot_avatar_url)
        # Add commands to the embed
        embed.add_field(name="Moderation", value="``&snipe,&lock``", inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(HelpCog(bot))
