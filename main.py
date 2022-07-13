# -*- coding: utf-8 -*-
import os
import discord
import psycopg2
from discord_components import DiscordComponents, Button, ActionRow, interaction
from discord.ext import commands

#REMOVER DEPOIS
# from dotenv import load_dotenv
# load_dotenv()

intents = discord.Intents.all()
discord.member = True
bot = commands.Bot(command_prefix="!", intents=intents)
DiscordComponents(bot)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
connection = psycopg2.connect(DATABASE_URL, sslmode = 'require')
cursor = connection.cursor()
channels = {}
classes = []

NEWCOMER_ROLE_ID = int(os.getenv("NEW_USER_ROLE_ID"))
# ROLEGIVING_CHANNEL_ID = int(os.getenv("ROLEGIVING_CHANNEL_ID"))
EVENTPLANNER_CHANNEL_ID = int(os.getenv("EVENTPLANNER_CHANNEL_ID"))

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

@bot.event
async def on_ready():   
    global channels, classes
    cursor.execute("SELECT * FROM channels")
    result = cursor.fetchall()
    channels = {result[i][0]: int(result[i][1]) for i in range(0, len(result))}
    
    cursor.execute("SELECT class_name FROM classes")
    classes = [name[0] for name in cursor.fetchall()]
    print(f"Logged in as {bot.user.name}({bot.user.id})")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(channels['visitante'])
    # channel = member.guild.system_channel
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
                   discord.utils.get(channel.guild.channels, id = channels['regras']),
                   discord.utils.get(channel.guild.channels, id = channels['identifique-se'])),
        color=discord.Color.green()
    )

    if channel is not None:
        await channel.send(embed=embed)
    
    role = discord.utils.get(member.guild.roles, id=NEWCOMER_ROLE_ID)
    await member.add_roles(role)    

@bot.command()
@commands.has_any_role('Ademir', 'Officer')
async def selectSQL(ctx, table, where=None):
    sql = f"SELECT * FROM {table}"
    if where is not None: sql = sql + f" WHERE {where}"
    cursor.execute(sql)
    result = cursor.fetchall()
    await ctx.send(result)

@bot.command()
@commands.has_any_role('Ademir', 'Officer')
async def executeSQL(ctx, sql):
    try:
        cursor.execute(sql)
        connection.commit()
        await ctx.send("Comando SQL executado com sucesso!")
    except:
        await ctx.send("Erro ao executar o comando SQL!")
        
@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command(
    help="!criar_embed canal preset\n\nExemplo: !criar_embed raids Valtan",
    brief="Cria uma embed com base na tabela presets. (Use !help criar_embed)"
    )
@commands.has_permissions(manage_roles=True)
async def criar_embed(ctx, canal, titulo_preset):
    cursor.execute(f"SELECT title, description, guide_url, image_url, buttons FROM presets WHERE preset_name = '{titulo_preset}'")
    result = cursor.fetchall()[0]
    if result is not None and channels[canal] is not None:
        embed=discord.Embed(title=result[0], description=result[1], url=result[2], color=0xFF5733)
        embed.set_image(url=result[3])
        
        buttons = []
        for item in result[4].split('/'):
            mode, ilevel, role_id = item.split('-')
            if ilevel != 'null': embed.add_field(name = mode.upper(), value=ilevel, inline=True)
            buttons.append(Button(custom_id=role_id, label=mode))
            
        action_row = ActionRow(*buttons)
        channel = discord.utils.get(ctx.guild.channels, id = channels[canal])
        await channel.send(embed=embed, components=[action_row])
    else:
        await ctx.send("Não há nenhum preset com este nome e/ou canal está errado! :(")

# @bot.command()
# async def criar_evento(ctx):
#     channel = bot.get_channel(EVENTPLANNER_CHANNEL_ID)
#     embed=discord.Embed(title="Teste - Evento", color=0x0000FF)
#     buttons = [Button(custom_id='Teste', label='Teste 1')]
#     action_row = ActionRow(*buttons)
#     await channel.send(embed=embed, components=[action_row])

@bot.event
async def on_button_click(interaction):
    if interaction.responded: return
    if interaction.channel_id == channels['raids']:
        has_role, role = giveRole(interaction)
        
        if has_role: 
            await interaction.author.remove_roles(role) 
            await interaction.send(content = f"Você não receberá mais avisos de {interaction.custom_id}! :(") 
        else:
            await interaction.author.add_roles(role)
            events = discord.utils.get(interaction.guild.channels, id = channels['eventos'])
            await interaction.send(content = f"Você agora receberá avisos de {interaction.custom_id}! Fique de olho em {events.mention} e boa sorte! <3") 
        
        await interaction.send(content = f"Botão {interaction.custom_id} apertado no canal {interaction.channel} pelo usuário {interaction.author}") 
    elif interaction.channel_id == channels['classes']:
        has_role, role = giveRole(interaction)
        author_roles = [role.name for role in interaction.author.roles]
        
        if has_role: 
            await interaction.author.remove_roles(role) 
            author_roles.remove(role.name)
            await interaction.send(content = f"Você não tem mais um(a) {interaction.custom_id} cadastrado(a). :(\n\nSuas classes cadastradas: {set(classes).intersection(author_roles)}") 
        else:
            if len(set(classes).intersection(author_roles)) >= 6: 
                await interaction.send(content = f"Você não pode ter mais de 6 personagens! :( De preferência marque apenas os personagens que ganhem Gold em Raids! <3\n\nSuas classes cadastradas: {set(classes).intersection(author_roles)}")
            else:
                await interaction.author.add_roles(role)
                author_roles.append(interaction.custom_id)
                await interaction.send(content = f"Agora você tem um(a) {interaction.custom_id} cadastrado(a)!\n\nSuas classes cadastradas: {set(classes).intersection(author_roles)}")
        # buttons = [Button(custom_id='Teste1', label='Teste 1'),Button(custom_id='Teste2', label='Teste 2'),Button(custom_id='Teste3', label='Teste 3'),Button(custom_id='Teste4', label='Teste 4'),Button(custom_id='Teste5', label='Teste 5')]
        # action_row1 = ActionRow(*buttons)
        # buttons2 = [Button(custom_id='Teste6', label='Teste 6'),Button(custom_id='Teste7', label='Teste 7'),Button(custom_id='Teste8', label='Teste 8'),Button(custom_id='Teste9', label='Teste 9'),Button(custom_id='Teste10', label='Teste 10')]
        # action_row2 = ActionRow(*buttons2)
        # buttons.append(Button(custom_id=interaction.author.roles[1].name, label=interaction.author.roles[1].name))
        #, components=[action_row1, action_row2]

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