# -*- coding: utf-8 -*-
# TABELAS:
# presets: preset_name(VARCHAR 30), title (VARCHAR 50), description (TEXT), guide_url (TEXT), image_url(TEXT), buttons (TEXT)(Normal Mode-1415-VALTAN_NM/Hard Mode-1445-VALTAN_HM)(Warrior-1415-Warrior)
# classes: class_name (VARCHAR 30), class (VARCHAR 20)
# channels: channel_name (VARCHAR 30), Id (TEXT)[visitante, regras, identifique-se, classes, raids, eventos]

from datetime import datetime, timezone
from discord.ext import commands
from discord_components import DiscordComponents, Button, ActionRow, interaction
from dotenv import load_dotenv
import discord
import locale
import os
import psycopg2
# Setar a linguagem
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR')
except:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil')

#REMOVER DEPOIS
load_dotenv()

# Configs do Discord
intents = discord.Intents.all()
discord.member = True
bot = commands.Bot(command_prefix="!", intents=intents)
DiscordComponents(bot)

# Variaveis do environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
connection = psycopg2.connect(DATABASE_URL, sslmode = 'require')
cursor = connection.cursor()

# Inicializando listas e dicts
channels = {}
classes = []

NEWCOMER_ROLE_ID = int(os.getenv("NEW_USER_ROLE_ID"))
# ROLEGIVING_CHANNEL_ID = int(os.getenv("ROLEGIVING_CHANNEL_ID"))
# EVENTPLANNER_CHANNEL_ID = int(os.getenv("EVENTPLANNER_CHANNEL_ID"))

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
        await ctx.send("Não há nenhum preset com este nome e/ou canal está errado! :slight_frown:")

@bot.command()
async def criar_evento(ctx, datahora=None, title=None, description=None, image_url=None):
    if datahora is not None: 
        try:
            dt = datetime.strptime(datahora, '%d/%m/%Y %H:%M')
            dt_string = dt.strftime("%A, %d de %B de %Y - %H:%M")
        except:
            await ctx.send("Data/hora inválida")
            return
    
    channel = bot.get_channel(channels['eventos'])
    embed=discord.Embed(title=title, description=description, color=0x0000FF)
    embed.set_image(url=image_url)
    embed.add_field(name="Data/Hora", value=dt_string, inline=False)
    embed.add_field(name="\✅ Presente", value="-", inline=True)
    embed.add_field(name="❌ Recusado", value="-", inline=True)
    embed.add_field(name="❔ Sem certeza", value="-", inline=True)
    embed.set_footer(text=f"Evento criado por: {ctx.author}\nHora: ")
    embed.timestamp = datetime.now(timezone.utc).astimezone()
    message = await channel.send(embed=embed)
    print(message.id)
    buttons = [Button(custom_id=f'Sim_{message.id}', label='✅ Sim'),
               Button(custom_id=f'Não_{message.id}', label='❌ Não'),
               Button(custom_id=f'Tentative_{message.id}', label='❔ Talvez'),
               Button(custom_id=f'Split_{message.id}', label='Dividir Party')]
    action_row = ActionRow(*buttons)
    await message.edit(components=[action_row])

@bot.event
async def on_button_click(interaction):
    if interaction.responded: return
    if interaction.channel_id == channels['raids']:
        has_role, role = giveRole(interaction)
        
        if has_role: 
            await interaction.author.remove_roles(role) 
            await interaction.send(content = f"Você não receberá mais avisos de {interaction.custom_id}! :slight_frown:") 
        else:
            await interaction.author.add_roles(role)
            events = discord.utils.get(interaction.guild.channels, id = channels['eventos'])
            await interaction.send(content = f"Você agora receberá avisos de {interaction.custom_id}! Fique de olho em {events.mention} e boa sorte! :hearts:") 
        
        await interaction.send(content = f"Botão {interaction.custom_id} apertado no canal {interaction.channel} pelo usuário {interaction.author}") 
    elif interaction.channel_id == channels['classes']:
        has_role, role = giveRole(interaction)
        author_roles = [role.name for role in interaction.author.roles]
        
        if has_role: 
            await interaction.author.remove_roles(role) 
            author_roles.remove(role.name)
            await interaction.send(content = f"Você não tem mais um(a) {interaction.custom_id} cadastrado(a). :slight_frown:\n\nSuas classes cadastradas: {set(classes).intersection(author_roles)}") 
        else:
            if len(set(classes).intersection(author_roles)) >= 6: 
                await interaction.send(content = f"Você não pode ter mais de 6 personagens! :slight_frown: De preferência marque apenas os personagens que ganhem Gold em Raids! :hearts:\n\nSuas classes cadastradas: {set(classes).intersection(author_roles)}")
            else:
                await interaction.author.add_roles(role)
                author_roles.append(interaction.custom_id)
                await interaction.send(content = f"Agora você tem um(a) {interaction.custom_id} cadastrado(a)! :hearts:\n\nSuas classes cadastradas: {set(classes).intersection(author_roles)}")
    elif interaction.channel_id == channels['eventos']:
        channel = bot.get_channel(channels['eventos'])
        msg_option, msg_id = interaction.custom_id.split('_')
        message = await channel.fetch_message(msg_id)
        
        clone_embed = message.embeds[0]
        clone_embed.set_field_at(1, name="\✅ Presente", value="> Teste\n", inline=True)
        await message.edit(embed=clone_embed)

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