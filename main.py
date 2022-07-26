# -*- coding: utf-8 -*-
# TABELAS:
# presets: preset_name(VARCHAR 30), title (VARCHAR 50), description (TEXT), guide_url (TEXT), image_url(TEXT), buttons (TEXT)(Normal Mode-1415-VALTAN_NM/Hard Mode-1445-VALTAN_HM)(Warrior-1415-Warrior)
# classes: class_name (VARCHAR 30), class (VARCHAR 20)
# channels: channel_name (VARCHAR 30), Id (TEXT)[visitante, regras, identifique-se, classes, raids, eventos]
# roles: role_name (VARCHAR 30)[Visitante (0), Guildmate (1), Guild Officer (2), Guild Deputy (3), Guild Master (4)]

from datetime import datetime, timedelta
from discord.ext import commands
from discord_components import DiscordComponents, Button, Select, SelectOption, ActionRow
import discord
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
roles = {}
admin_roles = []

@bot.event
async def on_ready():   
    global channels, classes, roles, admin_roles         
    cursor.execute("UPDATE event_presets SET role_to_ping = 'Valtan_NM' WHERE preset_name = 'Valtan_Normal'")
    cursor.execute("UPDATE event_presets SET role_to_ping = 'Valtan_HM' WHERE preset_name = 'Valtan_Hard'")
    connection.commit()
     
    cursor.execute("SELECT * FROM channels")
    result = cursor.fetchall()
    channels = {result[i][0]: int(result[i][1]) for i in range(0, len(result))}
    
    cursor.execute("SELECT class_name FROM classes")
    classes = [name[0] for name in cursor.fetchall()]
    
    cursor.execute("SELECT role_name, id, admin FROM roles")
    result = cursor.fetchall()
    admin_roles = [name[0] for name in result if name[2] is True]
    roles = {result[i][0]: int(result[i][1]) for i in range(0, len(result))}#[name[0] for name in cursor.fetchall()]
    print(f"Logged in as {bot.user.name}({bot.user.id})")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(channels['visitante'])
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
    
    role = discord.utils.get(member.guild.roles, id=roles["Visitante"])
    await member.add_roles(role)    

@bot.command()
async def selectSQL(ctx, table, where=None):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        sql = f"SELECT * FROM {table}"
        if where is not None: sql = sql + f" WHERE {where}"
        cursor.execute(sql)
        result = cursor.fetchall()
        await ctx.send(result)
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")

@bot.command()
async def executeSQL(ctx, sql):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        try:
            cursor.execute(sql)
            connection.commit()
            await ctx.send("Comando SQL executado com sucesso!")
        except:
            await ctx.send("Erro ao executar o comando SQL!")
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")
        
# @bot.command()
# async def ping(ctx):
#     await ctx.send("pong")

@bot.command(
    help="!criar_embed canal preset\n\nExemplo: !criar_embed raids Valtan",
    brief="Cria uma embed com base na tabela presets. (Use !help criar_embed)"
    )
async def criar_embed(ctx, canal, titulo_preset):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        cursor.execute(f"SELECT title, description, guide_url, image_url, buttons FROM presets WHERE preset_name = '{titulo_preset}'")
        if len(cursor.fetchall()) and channels[canal] is not None:
            result = cursor.fetchall()[0]
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
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")

@bot.command()
async def criar_evento(ctx, datahora=None, nome_preset=None):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        cursor.execute(f"SELECT role_to_ping, title, description, image_url, multi_participation, max_pt_size FROM event_presets WHERE preset_name = '{nome_preset}'")
        if len(cursor.fetchall()):
            result = cursor.fetchall()[0]
            if datahora is not None: 
                try:
                    dt = datetime.strptime(datahora, '%d/%m/%Y %H:%M')
                    dt_string = dt.strftime("%A, %d de %B de %Y - %H:%M")
                except:
                    await ctx.send("Data/hora inválida")
                    return
            #<@&ROLE_ID>s)
            if result[0] == 'everyone': role = ctx.guild.default_role
            else: role = discord.utils.get(ctx.guild.roles, name=result[0])
            
            channel = bot.get_channel(channels['eventos'])
            embed=discord.Embed(title=result[1], description=result[2], color=0x0000FF)
            embed.set_image(url=result[3])
            embed.add_field(name="Data/Hora", value=dt_string, inline=False)
            embed.add_field(name="\✅ Presente", value="-", inline=True)
            embed.add_field(name="\❌ Recusado", value="-", inline=True)
            embed.add_field(name="\❔ Sem certeza", value="-", inline=True)
            embed.set_footer(text=f"Evento criado por: {ctx.author}\nHora: ")
            embed.timestamp = datetime.now() + timedelta(hours=3)
            
            multi_participation = str(result[4])
            max_pt_size = str(result[5])
            buttons = [Button(custom_id=f'Participar_{multi_participation}', label='✅ Participar'),
                       Button(custom_id=f'Recusar', label='❌ Recusar'),
                       Button(custom_id=f'Tentativa', label='❔ Talvez'),
                       Button(custom_id=f'Split_{max_pt_size}', label='Dividir Party')]
            action_row = ActionRow(*buttons)
            
            if result[0] == 'everyone': await channel.send(content=f"{role}", embed=embed, components=[action_row])
            else: await channel.send(content=f"{role.mention}", embed=embed, components=[action_row])
        else:
            await ctx.send("Não há nenhum preset com este nome! (Dica: cheque os presets com !presets) :slight_frown:")
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")
        
@bot.command()
async def presets(ctx):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        sql = "SELECT preset_name FROM presets"
        cursor.execute(sql)
        result = [name[0] for name in cursor.fetchall()]
        
        str_output = "**EMBEDS:**\n"
        for item in result:
            str_output = str_output + "- " + item + "\n"
        
        str_output = str_output + "\n**PRESETS EVENTOS:**\n";    
        sql = "SELECT preset_name FROM event_presets"
        cursor.execute(sql)
        result = [name[0] for name in cursor.fetchall()]
        for item in result:
            str_output = str_output + "- " + item + "\n"
                
        await ctx.send(str_output)
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")

@bot.event
async def on_button_click(interaction):
    if interaction.channel_id == channels['raids']:
        has_role, role = giveRole(interaction)
        
        if has_role:
            await interaction.author.remove_roles(role) 
            await interaction.respond(content = f"Você não receberá mais avisos de {interaction.custom_id}! :slight_frown:") 
        else:
            await interaction.author.add_roles(role)
            events = discord.utils.get(interaction.guild.channels, id = channels['eventos'])
            await interaction.respond(content = f"Você agora receberá avisos de {interaction.custom_id}! Fique de olho em {events.mention} e boa sorte! :hearts:") 
            
    elif interaction.channel_id == channels['classes']:
        has_role, role = giveRole(interaction)
        author_roles = [role.name for role in interaction.author.roles]
        
        if has_role: 
            await interaction.author.remove_roles(role) 
            author_roles.remove(role.name)
            roles = set(classes).intersection(author_roles)
            if roles == set(): roles = "Nenhuma"
            await interaction.respond(content = f"Você não tem mais um(a) {interaction.custom_id} cadastrado(a). :slight_frown:\n\nSuas classes cadastradas: {roles}")   
        else:
            await interaction.author.add_roles(role)
            author_roles.append(interaction.custom_id)
            await interaction.respond(content = f"Agora você tem um(a) {interaction.custom_id} cadastrado(a)! :hearts:\n\nSuas classes cadastradas: {set(classes).intersection(author_roles)}")
    
    elif interaction.channel_id == channels['eventos']: 
        custom_id = interaction.custom_id.split('_')[0]
        if custom_id == 'Split':
            await interaction.respond(content = f"Essa funcionalidade ainda não está pronta. :slight_frown:")
        else:
            custom_id = interaction.custom_id.split('_')[0]
            if custom_id == 'Participar':
                try: multi_participation = interaction.custom_id.split('_')[1]
                except: multi_participation = "False"
                
                if multi_participation == "True":
                    options = []
                    roles = set(classes).intersection([role.name for role in interaction.author.roles])
                    if roles == set():
                        canal_classe = discord.utils.get(interaction.guild.channels, id = channels['classes'])
                        await interaction.respond(content = f"Antes de participar de um evento, vá em {canal_classe.mention} e escolha as classes que você joga!")
                        return
                    for item in roles:
                        class_name = item.replace("'", "")
                        options.append(SelectOption(label=class_name, value=interaction.author.name+"_"+class_name))
                    await interaction.respond(content = "Escolha com qual classe você irá participar do evento:", components=[Select(placeholder = "Selecione uma classe:", options=options)])
                else:
                    event_message = interaction.message
                    clone_embed = editEmbed(event_message.embeds[0], interaction.author.name, 1)
                    await interaction.edit_origin(embed=clone_embed)

            if custom_id == "Recusar":
                event_message = interaction.message
                clone_embed = editEmbed(event_message.embeds[0], interaction.author.name, 2)
                await interaction.edit_origin(embed=clone_embed)
                
            if custom_id == "Tentativa":
                event_message = interaction.message
                clone_embed = editEmbed(event_message.embeds[0], interaction.author.name, 3)
                await interaction.edit_origin(embed=clone_embed)

@bot.event
async def on_select_option(interaction):
    if interaction.responded: return
    if interaction.channel_id == channels['eventos']: 
        author_name, author_class = interaction.values[0].split("_")
        event_message = await interaction.channel.fetch_message(interaction.raw_data['message']['message_reference']['message_id'])
        
        clone_embed = event_message.embeds[0]
        _, participation_text, refusal_text, tentative_text = [field.value for field in clone_embed.fields] # TO DO: refusal, tentative texts
        participation_list = participation_text.split("\n")
        refusal_list = refusal_text.split("\n")
        tentative_list = tentative_text.split("\n")
        filtered_list = []
        
        if participation_text.find(f"{author_name} ({author_class})") != -1: # se existe, remove
            for member in participation_list:
                if member.find(f" {author_name} ({author_class})") == -1: filtered_list.append("\n"+member)
            participation_text = ''.join(filtered_list)
            if participation_text == "": participation_text = "-"
        else: # senão, adiciona  
            if participation_text == "-": participation_text = ""
            participation_text = participation_text + f"\n> {author_name} ({author_class})"
        clone_embed.set_field_at(1, name="\✅ Presente", value=participation_text, inline=True)

        if refusal_text.find(f"{author_name}") != -1: # se existe, remove
            for member in refusal_list:
                if member.find(f" {author_name}") == -1: filtered_list.append("\n"+member)
            refusal_text = ''.join(filtered_list)
            if refusal_text == "": refusal_text = "-"
        clone_embed.set_field_at(2, name="\❌ Recusado", value=refusal_text, inline=True)
        
        if tentative_text.find(f"{author_name}") != -1: # se existe, remove
            for member in tentative_list:
                if member.find(f" {author_name}") == -1: filtered_list.append("\n"+member)
            tentative_text = ''.join(filtered_list)
            if tentative_text == "": tentative_text = "-"
        clone_embed.set_field_at(3, name="\❔ Sem certeza", value=tentative_text, inline=True)
        
        await event_message.edit(embed=clone_embed) 
        await interaction.respond(type=6)

def editEmbed(embed, author_name, index):
    # 1 - Participar
    # 2 - Recusar
    # 3 - Tentativa
    clone_embed = embed
    _, participation_text, refusal_text, tentative_text = [field.value for field in clone_embed.fields]
    
    participation_list = participation_text.split("\n")
    refusal_list = refusal_text.split("\n")
    tentative_list = tentative_text.split("\n")
    filtered_list = []
    filtered_str = ''
    
    for i in range(1, 4):
        filtered_list.clear()
        filtered_str = ''
        if i == 1:
            edit_list = participation_list
            item_name = "\✅ Presente"
        if i == 2:
            edit_list = refusal_list
            item_name = "\❌ Recusado"
        if i == 3:
            edit_list = tentative_list
            item_name = "\❔ Sem certeza"
                
        if index is not i:             
            for member in edit_list:
                if member.find(f" {author_name}") == -1: filtered_list.append("\n"+member)
            filtered_str = ''.join(filtered_list)
            if filtered_str == "": filtered_str = "-"
            
        if index is i:
            filtered_str = ''.join(edit_list)
            if filtered_str.find(f" {author_name}") != -1: # se existe, remove
                for member in edit_list:
                    if member.find(f" {author_name}") == -1: filtered_list.append("\n"+member)
                filtered_str = ''.join(filtered_list)
                if filtered_str == "": filtered_str = "-"
            else: # se não, adiciona
                if filtered_str == '-': filtered_str = ''
                filtered_str = filtered_str + f"\n> {author_name}"
        clone_embed.set_field_at(i, name=item_name, value=filtered_str, inline=True)
    return clone_embed

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