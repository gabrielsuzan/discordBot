# -*- coding: utf-8 -*-
import os
import discord
from discord.ext import commands
intents = discord.Intents.all()
discord.member = True
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}({bot.user.id})")

@bot.event
async def on_member_join(member):
    embed = discord.Embed(
        title="Olá "+ member.name +"!",
        description="Seja bem vindo ao Sfclan!",
        color=discord.Color.green()
    )

    channel = bot.get_channel(994209459071094794)
    await channel.send(embed=embed)
    
    role = discord.utils.get(member.guild.roles, id=994206957621760061)
    await member.add_roles(role)
    print("Added role '" + role.name + "' to " + member.name)
    

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

if __name__ == "__main__":
    bot.run(TOKEN)
