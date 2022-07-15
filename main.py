# -*- coding: utf-8 -*-
# TABELAS:
# presets: preset_name(VARCHAR 30), title (VARCHAR 50), description (TEXT), guide_url (TEXT), image_url(TEXT), buttons (TEXT)(Normal Mode-1415-VALTAN_NM/Hard Mode-1445-VALTAN_HM)(Warrior-1415-Warrior)
# classes: class_name (VARCHAR 30), class (VARCHAR 20)
# channels: channel_name (VARCHAR 30), Id (TEXT)[visitante, regras, identifique-se, classes, raids, eventos]

from datetime import datetime, timedelta
from discord.ext import commands
from discord_components import DiscordComponents, Button, Select, SelectOption, ActionRow, interaction
import discord
import locale
import os
import psycopg2

#REMOVER DEPOIS
# from dotenv import load_dotenv
# load_dotenv()

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
    embed.timestamp = datetime.now() + timedelta(hours=3)
    buttons = [Button(custom_id=f'Participar', label='✅ Participar'),
               Button(custom_id=f'Recusar', label='❌ Recusar'),
               Button(custom_id=f'Tentative', label='❔ Talvez'),
               Button(custom_id=f'Split', label='Dividir Party')]
    action_row = ActionRow(*buttons)
    await channel.send(embed=embed, components=[action_row])

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
        clone_embed = interaction.message.embeds[0]

        if interaction.custom_id == 'Split':
            await interaction.send(content = f"Essa funcionalidade ainda não está pronta. :slight_frown:")
        else:
            # old_name = clone_embed.fields[index].name
            # old_text = clone_embed.fields[index].value
            if interaction.custom_id == 'Participar': 
                # clone_embed.set_field_at(1, name="\✅ Presente", value="> Teste\n", inline=True)
                options = []
                roles = set(classes).intersection([role.name for role in interaction.author.roles])
                for item in roles:
                    class_name = item.replace("'", "")
                    options.append(SelectOption(label=class_name, value=str(interaction.message.id)+"_"+interaction.author.name+"_"+class_name))
                    print(str(interaction.message.id)+"_"+interaction.author.name+"_"+class_name)
                await interaction.send(content = "Teste inicial", components=[Select(placeholder = "Selecione uma classe:", options=options)])

            # new_embed = editEmbed(author=interaction.author, message=message, index=1)
            # elif msg_option == 'Recusar': new_embed = editEmbed(author=interaction.author, message=message, index=2)
            # elif msg_option == 'Tentative': new_embed = editEmbed(author=interaction.author, message=message, index=3)
            # await message.edit(embed=new_embed)    

@bot.event
async def on_select_option(interaction):
    if interaction.responded: return
    await interaction.send(content = interaction.values[0])
        
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