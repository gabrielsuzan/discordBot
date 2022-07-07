# -*- coding: utf-8 -*-
import discord
import config
from discord.ext import commands

intents = discord.Intents.all()
discord.member = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}({bot.user.id})")

@bot.event
async def on_member_join(member):
    # channel = bot.get_channel(config.NEW_USER_CHANNEL)
    channel = member.guild.system_channel
    true_member_count = len([m for m in channel.guild.members if not m.bot])
    
    embed = discord.Embed(
        title="Olá "+ member.name +"!",
        description="""
        Seja bem vindo ao Sfclan!
        
        Agora somos {0} membros!
        
        Este canal é específico para visitantes, o acesso completo ao servidor será disponibilizado após a confirmação de que seu personagem está na guild. Chame por alguém da staff para ganhar o cargo de Guildmate e dar continuição a integração na guild.
        
        Enquanto aguarda, leia também as {1.mention}
        
        Coloque o nome do seu personagem principal em {2.mention} para adiantar o processo.
        """.format(true_member_count,
                   discord.utils.get(channel.guild.channels, name = 'regras'),
                   discord.utils.get(channel.guild.channels, name = 'identifique-se')),
        color=discord.Color.green()
    )

    if channel is not None:
        await channel.send(embed=embed)
    
    newcomer_role = int(config.NEW_USER_ROLE)
    role = discord.utils.get(member.guild.roles, id=newcomer_role)
    await member.add_roles(role)    

@bot.command()
async def ping(ctx):
    await ctx.send("pong")
    
# @bot.command()
# async def assign_raid_roles(ctx):
#     await ctx.channel.send(
#         "This is a button test",
#         components = [
#             discord.ui.Button(style=ButtonStyle.blue, label="Button 1")
#         ]
#     )

if __name__ == "__main__":
    bot.run(config.TOKEN)
