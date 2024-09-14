import discord
from discord.ext import commands
from discord.ui import Button, View

class OnlyOwners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner():
        """Check if the user is the server owner."""
        async def predicate(ctx):
            return ctx.guild is not None and ctx.author.id == ctx.guild.owner_id
        return commands.check(predicate)

    
    # Add more owner-only commands here
    @commands.command()
    @is_owner()
    async def deleteroles(self, ctx):
        """Deletes all roles in the server after confirmation."""

        # Create a confirmation embed
        embed = discord.Embed(
            title="Role Deletion Confirmation",
            description="Are you sure you want to delete all roles in the server? This action cannot be undone.",
            color=discord.Color.orange()
        )

        # Create buttons for confirmation
        view = discord.ui.View()

        # Button for confirmation
        async def confirm_callback(interaction):
            if interaction.user == ctx.author:  # Ensure the interaction is from the command author
                await interaction.response.send_message("Deleting roles...", ephemeral=True)
                await delete_roles(ctx)
                # Disable the buttons after confirmation
                for item in view.children:
                    item.disabled = True
                await interaction.message.edit(view=view)
            else:
                await interaction.response.send_message("You are not authorized to confirm this action.", ephemeral=True)

        # Button for denial
        async def deny_callback(interaction):
            if interaction.user == ctx.author:
                await interaction.response.send_message("Role deletion canceled.", ephemeral=True)
                # Disable the buttons after denial
                for item in view.children:
                    item.disabled = True
                await interaction.message.edit(view=view)
            else:
                await interaction.response.send_message("You are not authorized to cancel this action.", ephemeral=True)

        # Add buttons to the view
        confirm_button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.green)
        deny_button = discord.ui.Button(label="Deny", style=discord.ButtonStyle.red)

        confirm_button.callback = confirm_callback
        deny_button.callback = deny_callback

        view.add_item(confirm_button)
        view.add_item(deny_button)

        # Send the confirmation message with buttons
        await ctx.send(embed=embed, view=view)

    async def delete_roles(self, ctx):
        """Deletes all roles in the server."""
        guild = ctx.guild

        # Iterate through all roles in the server
        for role in guild.roles:
            if role.name != "@everyone":  # Optional: Don't delete the @everyone role
                try:
                    await role.delete()
                    await ctx.send(f"Successfully Deleted role: {role.name}")
                except discord.Forbidden:
                    await ctx.send(f"Failed to delete role: {role.name} (Insufficient permissions)")
                except discord.HTTPException as e:
                    await ctx.send(f"Failed to delete role: {role.name} ({e})")

        await ctx.send("Role deletion complete.")
        
    @commands.command()
    @is_owner()  # Ensures only the owner can run this command
    async def deletechannels(self, ctx):
        """Deletes all channels and categories, excluding the one the command was run in, with confirmation."""
        guild = ctx.guild
        excluded_channel = ctx.channel

        # Create confirmation and deny buttons
        confirm_button = Button(label="Confirm", style=discord.ButtonStyle.green)
        deny_button = Button(label="Deny", style=discord.ButtonStyle.red)

        # Define what happens when the confirm button is pressed
        async def confirm_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                for channel in guild.channels:
                    if channel != excluded_channel:
                        try:
                            await channel.delete()
                        except discord.Forbidden:
                            error_embed = discord.Embed(
                                title="Error",
                                description=f"Failed to delete channel: {channel.name} (Insufficient permissions)",
                                color=discord.Color.red()
                            )
                            await ctx.send(embed=error_embed)
                        except discord.HTTPException as e:
                            error_embed = discord.Embed(
                                title="Error",
                                description=f"Failed to delete channel: {channel.name} ({e})",
                                color=discord.Color.red()
                            )
                            await ctx.send(embed=error_embed)
                success_embed = discord.Embed(
                    title="Success",
                    description="Channel deletion complete, excluding this channel.",
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=success_embed)
            else:
                # Simply return if the user is not authorized
                return

            # Disable both buttons after action
            confirm_button.disabled = True
            deny_button.disabled = True
            await interaction.message.edit(view=view)

        # Define what happens when the deny button is pressed
        async def deny_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                cancel_embed = discord.Embed(
                    title="Canceled",
                    description="Channel deletion has been canceled.",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=cancel_embed, ephemeral=True)
            else:
                # Simply return if the user is not authorized
                return

            # Disable both buttons after action
            confirm_button.disabled = True
            deny_button.disabled = True
            await interaction.message.edit(view=view)

        # Set button callbacks
        confirm_button.callback = confirm_callback
        deny_button.callback = deny_callback

        # Create a view to hold the buttons
        view = View()
        view.add_item(confirm_button)
        view.add_item(deny_button)

        # Send the confirmation message with the buttons
        confirm_embed = discord.Embed(
            title="⚠️ Confirmation",
            description="Are you sure you want to delete all channels except this one?",
            color=discord.Color.orange()
        )
        await ctx.send(embed=confirm_embed, view=view)

    @deletechannels.error
    async def deletechannels_error(self, ctx, error):
        # No action taken for non-owner triggers
        pass
            
            
    @commands.command()
    @commands.is_owner()  # Ensures only the owner can use this command
    async def rules(self, ctx, channel: discord.TextChannel, *, text: str):
        """Sets the server rules in the specified channel."""
        embed = discord.Embed(
            title="Server Rules",
            description=text,
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Rules set by {ctx.author}", icon_url=ctx.author.avatar.url)

        try:
            # Send the rules embed to the specified channel
            await channel.send(embed=embed)
            await ctx.send(f"✅ Rules have been successfully posted in {channel.mention}.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to send messages in that channel.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to send rules. Error: {e}")

    @rules.error
    async def rules_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("You don't have permission to set the rules.")
        else:
            await ctx.send(f"An error occurred: {error}")
            
# Setup function to add this cog to the bot
async def setup(bot):
    await bot.add_cog(OnlyOwners(bot))