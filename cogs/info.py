import discord
from discord.ext import commands
from datetime import datetime,timezone

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """Displays information about a specified user."""
        member = member or ctx.author

        roles = sorted(member.roles[1:], key=lambda r: r.position, reverse=True)
        roles_mentions = [role.mention for role in roles]
        roles_str = ", ".join(roles_mentions) if roles_mentions else "No roles"

        # Get permissions
        permissions = member.guild_permissions
        permission_list = []

        if permissions.administrator:
            permission_list.append("Administrator (All Perms 👑)")
        else:
            for perm, value in permissions:
                if value:  # If the permission is granted
                    formatted_perm = perm.replace('_', ' ').title()  # Format the permission name
                    permission_list.append(formatted_perm)

        permissions_str = ", ".join(permission_list) if permission_list else "No permissions"

        embed = discord.Embed(
            title=f"User Info - {member.display_name}",
            color=roles[0].color if roles else discord.Color.from_str('#020A1D'),
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="<:member:1284462011983593538>・Username", value=str(member), inline=True)
        embed.add_field(name="<:id_mem:1284462087980056668>・ID", value=member.id, inline=True)
        embed.add_field(name="<:exclamation:1284462141608431656>・Status", value=str(member.status).title(), inline=True)
        embed.add_field(name="<:doc:1284462124361322496>・Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="<:doc:1284462124361322496>・Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="<:parameter:1281427034916257844>・Roles", value=roles_str, inline=False)
        embed.add_field(name="<:lock:1283454417315692558>・Permissions", value=permissions_str, inline=False)  # New field for permissions

        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @commands.command()
    async def roleinfo(self, ctx, *, role: discord.Role):
    
        guild = ctx.guild
        roles = sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True)
        position = roles.index(role)
        now = datetime.now(timezone.utc)
        days_ago =(now - role.created_at).days
        
        embed = discord.Embed(
            title=f"{guild.name}",
            color=role.color if role.color.value != 0 else discord.Color.from_str('#020A1D'),
        )
        embed.add_field(name="<:id_mem:1284462087980056668>・ID", value=role.id, inline=False)
        embed.add_field(name="・Name", value=f"{role.name} ", inline=False)  
        embed.add_field(name="・Position", value=position + 1, inline=False)
        embed.add_field(name="・Color", value=str(role.color), inline=False)
        embed.add_field(name="・Hoisted", value="True" if role.hoist else "False", inline=False)
        embed.add_field(name="<:doc:1284462124361322496>・Created At",value=f"{role.created_at.strftime('%Y/%m/%d')} **({days_ago} days ago**)",inline=False)
        embed.add_field(name="<:members:1282722443177492541>・Members", value=len(role.members), inline=False)

        if role.icon:
            embed.set_thumbnail(url=role.icon.url)

        await ctx.send(embed=embed)


    @commands.command()
    async def serverinfo(self, ctx):
        """Provides information about the server."""
        guild = ctx.guild
        total_members = guild.member_count
        bot_count = len([member for member in guild.members if member.bot])
        human_count = total_members - bot_count

        embed = discord.Embed(
            title=f"{guild.name}",
            color=discord.Color.from_str('#020A1D')
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="<:id_mem:1284462087980056668>・Server ID", value=guild.id, inline=False)
        embed.add_field(name="<:member:1284462011983593538>・Owner", value=str(guild.owner.mention), inline=False)
        embed.add_field(name="<:doc:1284462124361322496>・Creation Date", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="<:members:1282722443177492541>・Members", value=f"{human_count} humans, {bot_count} bots", inline=False)
        embed.add_field(name="<:luck:1283471991709372456>・Channels ", value=f"{len(guild.text_channels)} text, {len(guild.voice_channels)} voice", inline=False)
        embed.add_field(name="・Roles", value=len(guild.roles), inline=False)
        embed.add_field(name="<:face:1283470113818935347>・Emojis", value=len(guild.emojis), inline=False)
        embed.add_field(name="<:boost:1283466459141509253>・Boosts", value=guild.premium_subscription_count, inline=False)

        await ctx.send(embed=embed)

    


    @commands.command()
    async def botinfo(self, ctx):
        """Displays information about the bot."""
        bot_user = self.bot.user
        bot_owner = (await self.bot.application_info()).owner
        bot_guild_count = len(self.bot.guilds)
        bot_member_count = sum(guild.member_count for guild in self.bot.guilds)
        bot_latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title=f"{bot_user.name} Information",
            color=discord.Color.from_str('#020A1D'),
            timestamp=datetime.utcnow()
        )
    
        embed.set_thumbnail(url=bot_user.avatar.url)
        embed.add_field(name="・Bot Name", value=bot_user.name, inline=True)
        embed.add_field(name="<:id_mem:1284462087980056668>・Bot ID", value=bot_user.id, inline=True)
        embed.add_field(name="<:member:1284462011983593538>・Owner", value=zen1t_h, inline=True)
        embed.add_field(name="<:servers:1284468530972196977>・Servers", value=bot_guild_count, inline=True)
        embed.add_field(name="<:members:1284462068614955041>・Users", value=bot_member_count, inline=True)
        embed.add_field(name="・Ping", value=f"{bot_latency} ms", inline=True)
        
    
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    
async def setup(bot):
    await bot.add_cog(Info(bot))