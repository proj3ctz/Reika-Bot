import discord
import asyncio
import re
from discord.ui import Button, View
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped_messages = {}
        self.mute_log_channels = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        self.sniped_messages[message.channel.id] = (message.content, message.author, message.created_at)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def snipe(self, ctx):
        channel = ctx.channel
        try:
            content, author, timestamp = self.sniped_messages[channel.id]

            embed = discord.Embed(
                description=content,
                color=discord.Color.red(),
                timestamp=timestamp
            )
            embed.set_author(name=f"{author}", icon_url=author.avatar.url)
            embed.set_footer(text=f"Deleted in #{channel.name}")

            await ctx.send(embed=embed)
        except KeyError:
            await ctx.send("There's nothing to snipe in this channel!", delete_after=5)

    @snipe.error
    async def snipe_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.", delete_after=5)

    
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """Lock a channel so that members cannot send messages."""
        channel = channel or ctx.channel  # Default to the current channel if none is provided

        overwrite = channel.overwrites_for(ctx.guild.default_role)  # Get overwrites for the @everyone role

        if overwrite.send_messages is False:
            await ctx.send(f"🔒 {channel.mention} is already locked.")
        else:
            overwrite.send_messages = False  # Deny sending messages
            try:
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)  # Update the channel permissions
                await ctx.send(f"🔒 {channel.mention} has been locked.")
                print(f"[DEBUG] Locked channel: {channel.name}")
            except discord.Forbidden:
                await ctx.send("I don't have permission to lock this channel.")
                print("[DEBUG] Failed to lock the channel: Missing permissions")
            except discord.HTTPException as e:
                await ctx.send(f"Failed to lock the channel. Error: {e}")
                print(f"[DEBUG] HTTP Exception: {e}")

    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to lock channels.", delete_after=5, ephemeral=True)
        else:
            await ctx.send(f"An error occurred: {error}")
            print(f"[DEBUG] Error in lock command: {error}")
       
       
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """Unlocks a channel, allowing members to send messages."""
        channel = channel or ctx.channel
    
        overwrite = channel.overwrites_for(ctx.guild.default_role)
    
        if overwrite.send_messages is True:
            await ctx.send(f"🔓 {channel.mention} is already unlocked.")
        else:    
            overwrite.send_messages = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(f"🔓 {channel.mention} has been unlocked.")

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to unlock channels.", delete_after=5, ephemeral=True)
        else:
            await ctx.send(f"An error occurred: {error}")
            print(f"[DEBUG] Error in unlock command: {error}")    
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member = None, *, role_name: str = None):
        """Assigns or removes a role from a user, ensuring the author's highest role is higher than the role being assigned/removed."""

        # Check if member or role name is missing
        if member is None or role_name is None:
            embed = discord.Embed(
                title="Invalid Usage",
                description="Please make sure that you've mentioned someone and mentioned the role (by name or ID) \n Correct usage: `&role @user Role name/Role ID`",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Explanation",
                value="To assign or remove a role from a user, mention the user and specify the role. For example: `&role @user RoleName/Role ID`.\n <a:alert:1281429686810841212> **It is recommended to put only role name or ID because tagging a role may bother those who have the tagged role.**"
            )
            await ctx.send(embed=embed)
            return

        # Find all roles that contain the provided role name (case insensitive)
        matching_roles = [role for role in ctx.guild.roles if role_name.lower() in role.name.lower()]

        # Handle if no roles were found
        if not matching_roles:
            embed = discord.Embed(
                title="Role Not Found",
                description=f"No roles found containing `{role_name}`.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # If multiple roles match, present buttons for selection
        if len(matching_roles) > 1:
            embed = discord.Embed(
                title="Multiple Roles Found",
                description=f"Multiple roles contain `{role_name}`. Please select one.",
                color=discord.Color.orange()
            )

            view = discord.ui.View()

            for role in matching_roles:
                button = discord.ui.Button(label=role.name, style=discord.ButtonStyle.primary)
                
                async def button_callback(interaction, selected_role=role):
                    if interaction.user == ctx.author:
                        await self.assign_or_remove_role(ctx, member, selected_role)
                        # Disable buttons after selection
                        for item in view.children:
                            item.disabled = True
                        await interaction.response.edit_message(content=f"Selected role: **{selected_role.name}**", view=view)
                    else:
                        await interaction.response.send_message("You are not authorized to select this role.", ephemeral=True)

                button.callback = button_callback
                view.add_item(button)

            await ctx.send(embed=embed, view=view)
            return

        # Only one role matches, continue with role assignment/removal
        role = matching_roles[0]
        await self.assign_or_remove_role(ctx, member, role)

    async def assign_or_remove_role(self, ctx, member, role):
        """Assigns or removes a role from a user, depending on their current role status, but ensures the author has a high enough role."""

        # Check if the author's highest role is high enough to manage the specified role
        author_top_role = ctx.author.top_role
        if author_top_role.position <= role.position:
            embed = discord.Embed(
                title="Role Management Error",
                description=f"You cannot manage a role higher or equal to your highest role: **{author_top_role.name}**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the bot's role is high enough to manage the specified role
        bot_role = ctx.guild.me.top_role
        if bot_role.position <= role.position:
            embed = discord.Embed(
                title="Role Management Error",
                description=f"The bot cannot manage a role equal to or higher than its own.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Perform role assignment or removal
        if role in member.roles:
            # If the member already has the role, remove it
            await member.remove_roles(role)
            embed = discord.Embed(
                title="Role Updated",
                description=f"Removed **{role.mention}** from {member.mention}.",
                color=discord.Color.red()
            )
        else:
            # If the member does not have the role, assign it
            await member.add_roles(role)
            embed = discord.Embed(
                title="Role Updated",
                description=f"Assigned **{role.mention}** to {member.mention}.",
                color=discord.Color.green()
            )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def setmutelog(self, ctx, channel_id: int):
        """Sets the channel for mute logs."""
        channel = self.bot.get_channel(channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            await ctx.send("Invalid channel ID. Please provide a valid text channel ID.")
            return

        self.mute_log_channels[ctx.guild.id] = channel_id
        await ctx.send(f"Mute log channel has been set to {channel.mention}.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided"):
        """Mutes a user in the server for a specified duration (e.g., 5m or 2h)."""
        # Create or get the mute role
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)

        await member.add_roles(mute_role, reason=reason)

        # Log to the mute log channel for the specific guild if set
        log_channel_id = self.mute_log_channels.get(ctx.guild.id)
        if log_channel_id:
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                log_embed = discord.Embed(
                    title="User Muted",
                    description=f"{member.mention} has been muted.",
                    color=discord.Color.red()
                )
                log_embed.add_field(name="Reason", value=reason, inline=False)
                await log_channel.send(embed=log_embed)

        # Parse duration
        if duration:
            match = re.match(r'(\d+)([mh])', duration)
            if match:
                time_value = int(match.group(1))
                time_unit = match.group(2)

                if time_unit == 'm':
                    await asyncio.sleep(time_value * 60)  # Convert minutes to seconds
                elif time_unit == 'h':
                    await asyncio.sleep(time_value * 3600)  # Convert hours to seconds

                await member.remove_roles(mute_role)

                # Log unmute action
                if log_channel_id:
                    if log_channel:
                        unmute_log_embed = discord.Embed(
                            title="User Unmuted",
                            description=f"{member.mention} has been unmuted.",
                            color=discord.Color.green()
                        )
                        unmute_log_embed.add_field(name="Duration", value=f"{time_value} {time_unit}", inline=False)
                        await log_channel.send(embed=unmute_log_embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Unmutes a user in the server."""
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role, reason=reason)

            # Log unmute action for the specific guild
            log_channel_id = self.mute_log_channels.get(ctx.guild.id)
            if log_channel_id:
                log_channel = self.bot.get_channel(log_channel_id)
                if log_channel:
                    log_embed = discord.Embed(
                        title="User Unmuted",
                        description=f"{member.mention} has been unmuted.",
                        color=discord.Color.green()
                    )
                    log_embed.add_field(name="Reason", value=reason, inline=False)
                    await log_channel.send(embed=log_embed)
        else:
            # Log not muted error
            log_channel_id = self.mute_log_channels.get(ctx.guild.id)
            if log_channel_id:
                log_channel = self.bot.get_channel(log_channel_id)
                if log_channel:
                    not_muted_embed = discord.Embed(
                        title="Error",
                        description=f"{member.mention} is not muted.",
                        color=discord.Color.orange()
                    )
                    await log_channel.send(embed=not_muted_embed)

    @setmutelog.error
    async def setmutelog_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
        else:
            await ctx.send(f"An error occurred: {error}")
            
            
    @commands.command()
    @commands.has_permissions(administrator=True)  # Restricting command to server owner
    async def reactionrole(self, ctx, message_text: str, *roles: discord.Role):
        """Creates a reaction role embed with buttons for multiple roles."""
        
        if not roles:
            await ctx.send("You must provide at least one role.", delete_after=5)
            return

        # Create an embed with the provided text
        embed = discord.Embed(
            title="React to get your Role",
            description=message_text,
            color=discord.Color.from_str('#020A1D')
        )
        embed.set_footer(text="React to get/remove a role!")

        # Create a view to hold the buttons
        view = View()

        # Loop through each provided role and create a button for it
        for role in roles:
            button = Button(label=role.name, style=discord.ButtonStyle.primary, custom_id=f"role_{role.id}")

            # Define the behavior for when each button is pressed
            async def button_callback(interaction: discord.Interaction, role=role):
                member = interaction.user
                if role in member.roles:
                    # If the user already has the role, remove it
                    await member.remove_roles(role)
                    await interaction.response.send_message(f"❌ Role {role.name} removed!", ephemeral=True)
                else:
                    # If the user doesn't have the role, assign it
                    await member.add_roles(role)
                    await interaction.response.send_message(f"✅ Role {role.name} assigned!", ephemeral=True)

            # Set the callback for each button
            button.callback = button_callback

            # Add the button to the view
            view.add_item(button)

        # Send the embed with the buttons in the specified channel
        await ctx.send(embed=embed, view=view)

    @reactionrole.error
    async def reactionrole_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("Only the server owner can use this command!", delete_after=5)
        else:
            await ctx.send(f"An error occurred: {error}")            
            
async def setup(bot):
    await bot.add_cog(Moderation(bot))