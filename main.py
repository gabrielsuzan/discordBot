# -*- coding: utf-8 -*-
# TABELAS:
# presets: preset_name(VARCHAR 30), title (VARCHAR 50), description (TEXT), guide_url (TEXT), image_url(TEXT), buttons (TEXT)(Normal Mode-1415-VALTAN_NM/Hard Mode-1445-VALTAN_HM)(Warrior-1415-Warrior)
# event_presets: preset_name VARCHAR(30), role_to_ping VARCHAR(30), title VARCHAR(50), description TEXT, image_url TEXT, multi_participation BOOLEAN, max_pt_size INTEGER
# classes: class_name (VARCHAR 30), class (VARCHAR 20)
# channels: channel_name (VARCHAR 30), Id (TEXT)[visitante, regras, identifique-se, classes, raids, eventos]
# roles: role_name (VARCHAR 30), Id (TEXT), admin (BOOLEAN)[Visitante (0), Guildmate (1), Guild Officer (2), Guild Deputy (3), Guild Master (4)]

from datetime import datetime, timedelta
from discord.ext import commands
from discord_components import DiscordComponents, Button, ActionRow, Select, SelectOption
import discord
import os
import psycopg2
import asyncio

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
    cursor.execute("SELECT * FROM channels")
    result = cursor.fetchall()
    channels = {result[i][0]: int(result[i][1]) for i in range(0, len(result))}
    
    cursor.execute("SELECT class_name FROM classes")
    classes = [name[0] for name in cursor.fetchall()]
    
    cursor.execute("SELECT role_name, id, admin FROM roles")
    result = cursor.fetchall()
    admin_roles = [name[0] for name in result if name[2] is True]
    roles = {result[i][0]: int(result[i][1]) for i in range(0, len(result))}
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
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def selectSQL(ctx, table, where=None):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        try:
            sql = f"SELECT * FROM {table}"
            if where is not None: sql = sql + f" WHERE {where}"
            print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            await ctx.send(result)
        except:
            await ctx.send("Erro ao executar o comando SQL!")
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")

@bot.command()
async def executeSQL(ctx, sql):
    print(sql)
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        try:
            cursor.execute(sql)
            connection.commit()
            await ctx.send("Comando SQL executado com sucesso!")
        except:
            await ctx.send("Erro ao executar o comando SQL!")
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")
        
@bot.command(
    help="!nova_classe 'subclasse' 'classe'\nExemplo: !nova_classe 'Machinist' 'Gunner'",
    brief="Insere nova classe no BD. (reiniciar bot após)"
    )
async def nova_classe(ctx, subclasse, classe):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        try:
            cursor.execute(f"INSERT INTO classes(class_name, class) VALUES ('{classe}','{subclasse}')")
            connection.commit()
            await ctx.send("Nova classe inserida!")
        except:
            await ctx.send("Erro ao executar o comando SQL!")
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")
#     await ctx.send("pong")

@bot.command(
    help="!criar_embed canal preset\n\nExemplo: !criar_embed raids Valtan",
    brief="Cria uma embed com base na tabela presets."
    )
async def criar_embed(ctx, canal, titulo_preset):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        cursor.execute(f"SELECT title, description, guide_url, image_url, buttons FROM presets WHERE preset_name = '{titulo_preset}'")
        result = cursor.fetchone()
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
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")

@bot.command(
    help="!criar_evento data_hora* preset\n*:formato dd/mm/aaaa hh:mm\n\nExemplo: !criar_evento '27/07/2022 22:00' Valtan",
    brief="Cria um evento com base na tabela event_presets."
    )
async def criar_evento(ctx, datahora=None, nome_preset=None, custom_description=None):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        cursor.execute(f"SELECT role_to_ping, title, description, image_url, multi_participation, max_pt_size FROM event_presets WHERE preset_name = '{nome_preset}'")
        result = cursor.fetchone()

        if result is not None:
            if datahora is not None: 
                try:
                    dt = datetime.strptime(datahora, '%d/%m/%Y %H:%M')
                    dt_string = dt.strftime("%A, %d de %B de %Y - %H:%M")
                except:
                    await ctx.send("Data/hora inválida")
                    return
            else: dt_string = "Não definido"
            #<@&ROLE_ID>s)
            if result[0] == 'everyone': role = ctx.guild.default_role
            else: role = discord.utils.get(ctx.guild.roles, name=result[0])
    
            channel = bot.get_channel(channels['eventos'])
            embed=discord.Embed(title=result[1], description=result[2] if custom_description is None else custom_description, color=0x0000FF)
            embed.set_image(url=result[3])
            embed.add_field(name="Data/Hora", value=dt_string, inline=False)
            embed.add_field(name="\✅ Presente", value="-", inline=True)
            embed.add_field(name="\❌ Recusado", value="-", inline=True)
            embed.add_field(name="\❔ Sem certeza", value="-", inline=True)
            embed.add_field(name="\📆 Marcar outro dia", value="-", inline=True)
            embed.set_footer(text=f"Evento criado por: {ctx.author}\nHora: ")
            embed.timestamp = datetime.now()# + timedelta(hours=3)
    
            multi_participation = str(result[4])
            # max_pt_size = str(result[5])
            buttons = [Button(custom_id=f'Participar_{multi_participation}', label='✅ Participar'),
                       Button(custom_id=f'Recusar', label='❌ Recusar'),
                       Button(custom_id=f'Tentativa', label='❔ Talvez'),
                       Button(custom_id=f'AnotherDay', label='📆 Marcar outro dia')] #Button(custom_id=f'Split_{max_pt_size}', label='Dividir Party')
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
    def check(msg):
        if msg.author.id == interaction.author.id: return True
        else: return False
    
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
                    options.append(SelectOption(label=class_name, value=class_name))
                
                await interaction.send(content = "Escolha com qual classe você irá participar do evento:", components=[Select(placeholder = "Selecione uma classe:", options=options)])
                result = await bot.wait_for("select_option", check=check)
                author_class = result.values[0]
                msg = await interaction.channel.fetch_message(interaction.message.id)
                clone_embed = editEmbed(embed=msg.embeds[0], author_name=interaction.author.display_name, author_class=author_class, index=1)
                await edit_message_embed(interaction.message, clone_embed)
            else:
                event_message = interaction.message
                clone_embed = editEmbed(embed=event_message.embeds[0], author_name=interaction.author.display_name, index=1)
                try:
                    await interaction.edit_origin(embed=clone_embed)
                except:
                    print("Erro ao tentar editar mensagem do evento!")

        if custom_id == "Recusar":
            event_message = interaction.message
            clone_embed = editEmbed(embed=event_message.embeds[0], author_name=interaction.author.display_name, index=2)
            await interaction.edit_origin(embed=clone_embed)
            
        if custom_id == "Tentativa":
            event_message = interaction.message
            clone_embed = editEmbed(embed=event_message.embeds[0], author_name=interaction.author.display_name, index=3)
            await interaction.edit_origin(embed=clone_embed)
            
        if custom_id == "AnotherDay":
            event_message = interaction.message
            clone_embed = editEmbed(embed=event_message.embeds[0], author_name=interaction.author.display_name, index=4)
            await interaction.edit_origin(embed=clone_embed)

@bot.event
async def on_select_option(interaction):
    if interaction.responded: return
    try:
        await asyncio.sleep(0.75)
        await interaction.edit_origin(content='Boa sorte! :hearts:', components=[], delete_after=10)
    except:
        print("Erro ao tentar finalizar interação!")
        
@bot.event
async def edit_message_embed(msg, new_embed):
    await msg.edit(embed=new_embed)
    await asyncio.sleep(0.75)

def editEmbed(embed, author_name, index, author_class=None):
    # 1 - Participar
    # 2 - Recusar
    # 3 - Tentativa
    clone_embed = embed
    
    participation_text = clone_embed.fields[1].value
    refusal_text = clone_embed.fields[2].value
    tentative_text = clone_embed.fields[3].value
    anotherday_text = clone_embed.fields[4].value
    # _, participation_text, refusal_text, tentative_text, anotherday_text = [field.value for field in clone_embed.fields]
    
    participation_list = participation_text.split("\n")
    refusal_list = refusal_text.split("\n")
    tentative_list = tentative_text.split("\n")
    anotherday_list = anotherday_text.split("\n")
    
    filtered_list = []
    filtered_str = ''
    
    for i in range(1, 5):
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
        if i == 4:
            edit_list = anotherday_list
            item_name = "\📆 Marcar outro dia"
        
        if index is not i:             
            for member in edit_list:
                if member.find(f" {author_name}") == -1: filtered_list.append("\n"+member)
            filtered_str = ''.join(filtered_list)
            if filtered_str == "": filtered_str = "-"
            
        if index is i:
            if author_class is None: author_string = f"{author_name}"
            else: author_string = f"{author_name} ({author_class})"
            
            if any(f" {author_string}" in name for name in edit_list): # se existe, remove
                for member in edit_list:
                    if member.find(f" {author_string}") == -1: filtered_list.append("\n"+member)
                filtered_str = ''.join(filtered_list)
                if filtered_str == "": filtered_str = "-"
            else: # se não, adiciona
                filtered_str = '\n'.join(edit_list)
                if filtered_str == '-': filtered_str = ''
                
                if len(filtered_str + f"\n> {author_string}") > 1023:
                    embed.add_field(name="Mais participantes!", value=filtered_str, inline=True)
                    filtered_str = f"\n> {author_string}"
                else: 
                    filtered_str = filtered_str + f"\n> {author_string}"
        
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