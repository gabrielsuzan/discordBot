# -*- coding: utf-8 -*-
import os
import discord
from discord_components import DiscordComponents, Button, ActionRow, interaction
from discord.ext import commands

#REMOVER DEPOIS
# from dotenv import load_dotenv
# load_dotenv()

intents = discord.Intents.all()
discord.member = True
bot = commands.Bot(command_prefix="!", intents=intents)
DiscordComponents(bot)

NEWCOMER_ROLE = int(os.getenv("NEW_USER_ROLE_ID"))
ROLEGIVING_CHANNEL_ID = int(os.getenv("ROLEGIVING_CHANNEL_ID"))
EVENTPLANNER_CHANNEL_ID = int(os.getenv("EVENTPLANNER_CHANNEL_ID"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

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
        
        Enquanto aguarda, leia as {1.mention}.
        
        Coloque o nome do seu personagem principal em {2.mention} para adiantar o processo.
        """.format(true_member_count,
                   discord.utils.get(channel.guild.channels, name = 'regras'),
                   discord.utils.get(channel.guild.channels, name = 'identifique-se')),
        color=discord.Color.green()
    )

    if channel is not None:
        await channel.send(embed=embed)
    
    role = discord.utils.get(member.guild.roles, id=NEWCOMER_ROLE)
    await member.add_roles(role)    

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command(
    help="!criar_raid <'titulo'> <'url_guia'> <'url_imagem'> <'modo1,itemlevel1,id_role1'>-<'modo2,itemlevel2,id_role2'>-...-<['modoN,itemlevelN,id_roleN']>\n\nExemplo: !criar_raid 'Legion Raid - Valtan' 'www.link.com/guia-valtan' 'www.link.com/valtan.jpg' 'Normal Mode,1415,VALTAN_NM'-'Hard Mode,1445,VALTAN_HM'",
    brief="Cria uma nova raid p/ escolher cargos. (Use !help criar_raid)"
    )
@commands.has_permissions(manage_roles=True)
async def criar_raid(ctx, titulo, url_guia, url_imagem, *, niveis):
    try:
        embed=discord.Embed(title=titulo, url=url_guia, color=0xFF5733)
        embed.set_image(url=url_imagem)
        
        buttons = []
        for item in niveis.split('-'):
            item = item.replace("'",'')
            mode, ilevel, role_id = item.split(',')
            embed.add_field(name = mode.upper(), value=ilevel, inline=True)
            buttons.append(Button(custom_id=role_id, label=mode))
        
        action_row = ActionRow(*buttons)
        await ctx.send(embed=embed, components=[action_row])
    except:
        await ctx.send("Oh não! Houve algum problema ao executar o comando. Digite '!help criar_raid' caso tenha dúvidas! ")

@bot.event
async def on_button_click(interaction):
    if interaction.responded: return
    if interaction.channel_id == ROLEGIVING_CHANNEL_ID:
        has_role, role = giveRole(interaction)
        
        if has_role: 
            await interaction.author.remove_roles(role) 
            await interaction.send(content = f"Você não receberá mais avisos de {interaction.custom_id}! :(") 
        else:
            await interaction.author.add_roles(role)
            events = discord.utils.get(interaction.guild.channels, id = EVENTPLANNER_CHANNEL_ID)
            await interaction.send(content = f"Você agora receberá avisos de {interaction.custom_id}! Fique de olho em {events.mention} e boa sorte! <3") 
 
        await interaction.send(content = f"Botão {interaction.custom_id} apertado no canal {interaction.channel} pelo usuário {interaction.author}") 
    else:
        await interaction.send("Ops! Canal errado!")

def giveRole(interaction):
    has_role = False
    for roles in interaction.author.roles:
        if interaction.custom_id.upper() == roles.name.upper(): has_role = True
    
    role_id = None
    for roles in interaction.author.guild.roles:
        if roles.name.upper() == interaction.custom_id.upper(): 
            role_id = int(roles.id)
            break
    role = discord.utils.get(interaction.author.guild.roles, id=role_id)
    return has_role, role

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
