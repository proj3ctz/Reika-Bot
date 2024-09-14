import discord
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    
    @commands.command()
    async def ping(self, ctx):
        """Check the bot's response time."""
        latency = self.bot.latency * 1000  # Convert latency to milliseconds
        await ctx.send(f'Pong! 🏓\nLatency is {latency:.2f} ms')

    @commands.command()
    async def locate(self, ctx, member: discord.Member):
        """Locate which voice channel a member is in."""
        voice_state = member.voice

        if voice_state and voice_state.channel:
            embed = discord.Embed(
                title="Member Located",
                description=f"{member.mention} is currently in the voice channel: {voice_state.channel.mention}",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Member Not Found",
                description=f"{member.mention} is not in any voice channel.",
                color=discord.Color.red()
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def move(self, ctx, member: discord.Member = None):
        """Moves a specified member to the voice channel the command issuer is in."""
        if not ctx.author.guild_permissions.move_members and not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have permission to move members.")
            return

        if member is None:
            await ctx.send("You need to mention a member to move. Usage: `&move @username`")
            return

        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel.")
            return

        if member.voice is None:
            await ctx.send(f"{member.mention} is not in a voice channel.")
            return

        target_channel = ctx.author.voice.channel

        try:
            await member.move_to(target_channel)
            await ctx.send(f"{member.mention} has been moved to {target_channel.mention}.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to move members.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
            
    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, new_nick: str):
        embed = discord.Embed()

        # Allow changing their own nickname
        if member != ctx.author and member.top_role >= ctx.author.top_role:
            embed.title = "Role Error"
            embed.description = f'You cannot change the nickname for {member.mention} because they have a higher role than you.'
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return

        try:
            await member.edit(nick=new_nick)
            embed.title = "Nickname Changed"
            embed.description = f'Nickname for {member.mention} has been changed to {new_nick}.'
            embed.color = discord.Color.green()
        except discord.Forbidden:
            embed.title = "Permission Error"
            embed.description = 'I do not have permission to change that member\'s nickname.'
            embed.color = discord.Color.from_str('#171C2F')
        except discord.HTTPException as e:
            embed.title = "Error"
            embed.description = f'Failed to change nickname: {e}'
            embed.color = discord.Color.red()

        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Clears a specified number of messages in the channel."""
        embed_color = 0x020A1D
        
        if amount <= 0:
            embed = discord.Embed(
                title="Error",
                description="Please enter a number greater than 0.",
                color=embed_color
            )
            await ctx.send(embed=embed)
            return
        elif amount > 100:
            embed = discord.Embed(
                
                description="<a:false:1282775862395146316>  〉 **You can only delete up to 100 messages at a time.**",
                color=embed_color
            )
            await ctx.send(embed=embed)
            return

        deleted = await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title="Success",
            description=f"Deleted {len(deleted)} message(s).",
            color=embed_color
        )
        await ctx.send(embed=embed, delete_after=3)
async def setup(bot):
    await bot.add_cog(Utility(bot))