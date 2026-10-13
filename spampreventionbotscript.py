#If anyone wants to replicate this, they can use this Discord bot script to clean up their Discord server. It just checks for messages that are the same and deletes all except the first one.
#This is my Webhook for those scammers again 👍
#https://discord.com/api/webhooks/1559385346981109761/5wPQOkRiu61hLtHjbKCaBdHc5GKINUK9O1o0n_28xKv_XbZV6PXMyvUSS4rqkJWdA-1D

import os
from collections import defaultdict, deque
import discord
from discord.ext import commands
TOKEN = os.environ["DISCORD_TOKEN"]
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)
HISTORY_LIMIT = 500
MIN_LENGTH = 5
EXEMPT_ROLES = {"Admin", "Moderator", "Bot"}
seen: dict[int, deque] = defaultdict(lambda: deque(maxlen=HISTORY_LIMIT))
def is_exempt(member: discord.Member) -> bool:
    if member.bot:
        return False
    return any(r.name in EXEMPT_ROLES for r in member.roles)
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({len(bot.guilds)} servers)")
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.guild is None:
        await bot.process_commands(message)
        return
    content = message.content.strip()
    if len(content) < MIN_LENGTH or is_exempt(message.author):
        await bot.process_commands(message)
        return
    history = seen[message.guild.id]
    for original in history:
        if original["content"] == content:
            try:
                await message.delete()
                print(
                    f"Deleted duplicate in {message.guild.name}#{message.channel.name} "
                    f"by {message.author} (original {original['id']})"
                )
            except discord.Forbidden:
                print("Missing permission to delete messages")
            except discord.HTTPException as e:
                print(f"Failed to delete: {e}")
            await bot.process_commands(message)
            return
    history.append(
        {
            "id": message.id,
            "content": content,
            "author": message.author.id,
            "channel": message.channel.id,
        }
    )
    await bot.process_commands(message)
bot.run(TOKEN)
