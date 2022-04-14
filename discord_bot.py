import discord
import sys

discord_url = str()
client = discord.Client()

@client.event
async def on_ready():
    global discord_url
    guild = client.get_guild('int number')
    discord_url = await guild.text_channels[0].create_invite(max_age=0, max_uses=0, temporary=False)

    await client.close()

client.run("token")
sys.stdout.write(str(discord_url))
