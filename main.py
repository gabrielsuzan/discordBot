# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime
import os

from discord import app_commands
from discord.app_commands import Choice
import discord
from discord.ui import Button, View, Modal, TextInput

from discord.ext import commands

#REMOVER DEPOIS
# from dotenv import load_dotenv
# load_dotenv()

# Configs do Discord
intents = discord.Intents.all()
discord.member = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Variaveis do environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 949037784230920223

# Inicializando listas e dicts
channels = {'visitante': 950761107251953707, 'regras': 950769476192833558, 'identifique-se': 950741476873240636, 'classes': 1004115103169400892, 'raids': 1004114683919355954, 'eventos': 1004115290071765013}
classes = ['Sorceress', 'Bard', 'Arcanist', 'Berserker', 'Destroyer', 'Gunlancer', 'Paladin', 'Artillerist', 'Deadeye', 'Gunslinger', 'Sharpshooter', 'Glaivier', 'Scrapper', 'Soulfist', 'Striker', 'Wardancer', 'Deathblade', 'Shadowhunter', 'Machinist']
roles = {'Guildmate': 950772292638617610, 'Guild Officer': 0, 'Guild Deputy': 0, 'Guild Master': 0, 'Visitante': 981541136084631553}
admin_roles = ['Guild Officer', 'Guild Deputy', 'Guild Master']

# Presets
presets =  {'Warrior': ['Warrior', '', 'https://cdn-longterm.mee6.xyz/plugins/reaction_roles/images/212635560596996097/91c18dece3b14bf906395f40a21baa9b33dacc53f0722ccf4808a5218e2403e0.png', 'Berserker-null-Berserker/Destroyer-null-Destroyer/Gunlancer-null-Gunlancer/Paladin-null-Paladin', 'Escolha sua sub-classe'],
            'Martial_Artist': ['Martial Artist', '', 'https://cdn-longterm.mee6.xyz/plugins/reaction_roles/images/212635560596996097/9a08669735eb456ea4738fc486c061cac8566b9a1ce1294cd98a8a3bd83a313c.png', 'Glaivier-null-Glaivier/Scrapper-null-Scrapper/Soulfist-null-Soulfist/Striker-null-Striker/Wardancer-null-Wardancer', 'Escolha sua sub-classe'],
            'Assassin': ['Assassin', '', 'https://cdn-longterm.mee6.xyz/plugins/reaction_roles/images/212635560596996097/b31d8909eca2aff39d0294c8afb0f84d9aebe70b624ef5ab06e7be41ded8c3c6.png', 'Deathblade-null-Deathblade/Shadowhunter-null-Shadowhunter', 'Escolha sua sub-classe'],
            'Mage': ['Mage', '', 'https://cdn-longterm.mee6.xyz/plugins/reaction_roles/images/212635560596996097/6768226af5747fe5ae5d15f415ec1fefe37932b87396253f05549b6809f0b8c8.png', 'Arcanist-null-Arcanist/Bard-null-Bard/Sorceress-null-Sorceress', 'Escolha sua sub-classe'],
            'Gunner': ['Gunner', 'Gunner', '', 'https://cdn-longterm.mee6.xyz/plugins/reaction_roles/images/212635560596996097/281fe2951cb45fdc9f1ca237c16530eac0c3b8f6895e535fd66d6129df2c3b2d.png', 'Artillerist-null-Artillerist/Deadeye-null-Deadeye/Gunslinger-null-Gunslinger/Sharpshooter-null-Sharpshooter/Machinist-null-Machinist', 'Escolha sua sub-classe'],
            'Argos': ['Abyss Raid - Argos', 'https://lost-ark.maxroll.gg/abyss-raids/argos-phase-1', 'https://mmos.com/wp-content/uploads/2022/03/lost-ark-abyss-raid-guardian-argos-banner.jpg', 'Phase 1-1370-ARGOS_P1/Phase 2-1385-ARGOS_P2/Phase 3-1400-ARGOS_P3', ' '],
            'Valtan': ['Legion Raid - Valtan', 'https://lost-ark.maxroll.gg/legion-raids/valtan-phase-1', 'https://i.postimg.cc/1XpYdN7f/valtan-hard.jpg', 'Normal Mode-1415-VALTAN_NM/Hard Mode-1445-VALTAN_HM/Inferno Mode-1445-VALTAN_HELL', ' '],
            'Vykas': ['Legion Raid - Vykas', 'https://lost-ark.maxroll.gg/legion-raids/vykas-phase-1', 'https://i.postimg.cc/W4GjMhTb/vykas-hard.jpg', 'Normal Mode-1430-VYKAS_NM/Hard Mode-1460-VYKAS_HM', ' '],
            'Kakul-Saydon': ['Legion Raid - Kakul-Saydon', 'https://lost-ark.maxroll.gg/legion-raids/kakul-saydon-gate-1', 'https://i.postimg.cc/V6XRsPqh/kakulsaydon-hard.jpg', 'Normal Mode (Rehearsal)-1385-KAKULSAYDON_NM/Hard Mode-1475-KAKULSAYDON_HM', ' ']}

presets_eventos =  {'Vykas_Normal': ['Vykas_NM', 'Legion Raid - Vykas (NORMAL)', 'Gate 1, 2 e 3 (1430+)', 'https://i.postimg.cc/LXS97jN1/vykas-normal.jpg', True, 8], 
                    'Vykas_Hard': ['Vykas_HM', 'Legion Raid - Vykas (HARD)', 'Gate 1, 2 e 3 (1460+)', 'https://i.postimg.cc/W4GjMhTb/vykas-hard.jpg', True, 8],
                    'Vykas_Inferno': ['Vykas_HELL', 'Legion Raid - Vykas (INFERNO)', 'Gate 1, 2 e 3 (1460)', 'https://i.postimg.cc/Bbr4TDLb/vykas-inferno.jpg', True, 8],
                    'Argos_P1': ['Argos_P1', 'Abyss Raid - Argos (P1)', 'Apenas P1 (1370)', 'https://i.postimg.cc/6pWTxJhM/argos-p1.jpg', True, 8],
                    'Argos_P2': ['Argos_P2', 'Abyss Raid - Argos (P2)', 'Apenas P1 e P2 (1385)', 'https://i.postimg.cc/d1yVjqqV/argos-p2.jpg', True, 8],
                    'Argos_P3': ['Argos_P3', 'Abyss Raid - Argos (P3)', 'Clear completo P1, P2 e P3 (1400)', 'https://i.postimg.cc/sDyg5db3/argos-p3.jpg', True, 8],
                    'Valtan_Normal': ['Valtan_NM', 'Legion Raid - Valtan (NORMAL)', 'Gate 1 e 2 (1415+)', 'https://i.postimg.cc/3RkstNHv/valtan-normal.jpg', True, 8],
                    'Valtan_Hard': ['Valtan_HM', 'Legion Raid - Valtan (HARD)', 'Gate 1 e 2 (1445+)', 'https://i.postimg.cc/1XpYdN7f/valtan-hard.jpg', True, 8],
                    'Valtan_Inferno': ['Valtan_HELL', 'Legion Raid - Valtan (INFERNO)', 'Gate 1 e 2 (1445)', 'https://i.postimg.cc/B6hvKXBP/valtan-inferno.jpg', True, 8],
                    'Kakul-Saydon_Normal': ['KakulSaydon_NM', 'Legion Raid - Kakul-Saydon (NORMAL)', 'Gate 1, 2 e 3 (1385+)', 'https://i.postimg.cc/ZKXCHvtr/kakulsaydon-normal.jpg', True, 4],
                    'Kakul-Saydon_Hard': ['KakulSaydon_HM', 'Legion Raid - Kakul-Saydon (HARD)', 'Gate 1, 2 e 3 (1475+)', 'https://i.postimg.cc/V6XRsPqh/kakulsaydon-hard.jpg', True, 4],
                    'Kakul-Saydon_Inferno': ['KakulSaydon_HELL', 'Legion Raid - Kakul-Saydon (INFERNO)', 'Gate 1, 2 e 3 (1475)', 'https://i.postimg.cc/rsmN1R6B/kakulsaydon-inferno.jpg', True, 4],
                    'GVG': ['everyone', 'GvG', 'Raid Match & Siege', 'https://assets.maxroll.gg/wordpress/Resources_PvP.jpg', False, 50]}

# Emojis
morango = '<:morango:1017552083362258975>'

class SeletorClasse(Modal):
    def __init__(self, custom_id):
        super().__init__(title='Selecione sua classe:')
        self.custom_id = custom_id
        self.message_id = None
        self.text = TextInput(label="Digite com quais classes você participará:", required=True, min_length=1)
        self.add_item(self.text)
        self.index_to_add = 1
        
    def check(self, msg):
        if msg.author.id == self.custom_id: return True
        else: return False
        
    async def on_submit(self, interaction: discord.Interaction):
        if str(interaction.user.id) == str(self.custom_id):
            try:
                classes = self.text.value.replace(' ','').split(',')
                if '' in classes: classes.remove('')
                if ' ' in classes: classes.remove(' ')
            except:
                print("Erro.")    
            else:
                msg = await interaction.channel.fetch_message(self.message_id)
                clone_embed = editEmbed(embed=msg.embeds[0], author_name=interaction.user.display_name, author_class=classes, index=self.index_to_add)
                await edit_message_embed(msg, clone_embed)
                
                if self.index_to_add == 1: message = f"Boa sorte! {morango}"
                elif self.index_to_add == 4: message = f"O time está cheio, portanto você foi adicionado aos reservas. Boa sorte! {morango}"
                await interaction.response.send_message(message, ephemeral=True)

@bot.event
async def on_ready():   
    print(f"Logged in as {bot.user.name}({bot.user.id})")
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))

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

@bot.command(
    help="!criar_embed canal preset\n\nExemplo: !criar_embed raids Valtan",
    brief="Cria uma embed com base na tabela presets."
    )
async def criar_embed(ctx, canal, titulo_preset):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        result = presets[titulo_preset]
        if result is not None and channels[canal] is not None:
            embed=discord.Embed(title=result[0], description=result[4], url=result[1], color=0xFF5733)
            embed.set_image(url=result[2])
            
            view = View()
            view.is_persistent()
            for item in result[3].split('/'):
                mode, ilevel, role_id = item.split('-')
                if ilevel != 'null': embed.add_field(name = mode.upper(), value=ilevel, inline=True)
                view.add_item(Button(custom_id=role_id, label=mode, style=discord.ButtonStyle.blurple))

            channel = discord.utils.get(ctx.guild.channels, id = channels[canal])
            await channel.send(embed=embed, view=view)
        else:
            await ctx.send("Não há nenhum preset com este nome e/ou canal está errado! :slight_frown:")
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")

@bot.hybrid_command(brief="Cria uma nova party para uma raid")
@app_commands.describe(
    nome_raid='Qual raid será feita, selecione uma das opções na lista',
    data_hora='Data e hora da raid (siga o formato do exemplo: 30/12/2000 14:00) (se não tiver um horário definido digite 0)',
    num_vagas_reservadas='Número de vagas reservadas (opcional)',
    descricao='Descrição customizada (opcional)'
    )
@app_commands.choices(nome_raid= [
    Choice(name='Argos (P1)', value='Argos_P1'),
    Choice(name='Argos (P2)', value='Argos_P2'),
    Choice(name='Argos (P3)', value='Argos_P3'),
    Choice(name='Valtan (Normal)', value='Valtan_Normal'),
    Choice(name='Valtan (Hard)', value='Valtan_Hard'),
    Choice(name='Valtan (Inferno)', value='Valtan_Inferno'),
    Choice(name='Vykas (Normal)', value='Vykas_Normal'),
    Choice(name='Vykas (Hard)', value='Vykas_Hard'),
    Choice(name='Kakul-Saydon (Rehearsal)', value='Kakul-Saydon_Normal'),
    Choice(name='Kakul-Saydon (Hard)', value='Kakul-Saydon_Hard')
    ])
@app_commands.choices(num_vagas_reservadas=[
    Choice(name=0, value=0),
    Choice(name=1, value=1),
    Choice(name=2, value=2),
    Choice(name=3, value=3),
    Choice(name=4, value=4),
    Choice(name=5, value=5),
    Choice(name=6, value=6),
    Choice(name=7, value=7)
    ])
async def raid(ctx, nome_raid:str, data_hora:str, num_vagas_reservadas:int=0, descricao:str=""):
    role = discord.utils.get(ctx.guild.roles, id=roles["Guildmate"])
    if (role in ctx.author.roles) or (set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set()) :
        
        if nome_raid in presets_eventos.keys(): raid = presets_eventos[nome_raid]
        else:
            await ctx.interaction.response.send_message("Nome da raid inexistente!", ephemeral=True)
            return
        
        if data_hora == "": dt_string = "Não definido"
        else:
            try:
                dt = datetime.strptime(data_hora, '%d/%m/%Y %H:%M')
                dt_string = dt.strftime("%A, %d de %B de %Y - %H:%M")
    
                # dias de semana
                dt_string = dt_string.replace("Monday", "Segunda-Feira").replace("Tuesday", "Terça-Feira").replace("Wednesday", "Quarta-Feira").replace("Thursday", "Quinta-Feira").replace("Friday", "Sexta-Feira").replace("Saturday", "Sábado").replace("Sunday", "Domingo")
                # meses
                dt_string = dt_string.replace("January", "Janeiro").replace("February", "Fevereiro").replace("March", "Março").replace("April", "Abril").replace("May", "Maio").replace("June", "Junho").replace("July", "Julho").replace("August", "Agosto").replace("September", "Setembro").replace("October", "Outubro").replace("November", "Novembro").replace("December", "Dezembro")
            except:
                await ctx.interaction.response.send_message("Data/hora inválida! Digite no formato: dd/MM/aaaa hh:mm", ephemeral=True)
                return
   
        role = discord.utils.get(ctx.guild.roles, name=raid[0])
    
        str_reserva = ''
        if num_vagas_reservadas > raid[5]: num_vagas_reservadas = raid[5]
        if num_vagas_reservadas > 0:
            aux = num_vagas_reservadas
            while aux > 0:
                str_reserva = str_reserva + "\n> Reservado"
                aux -= 1
        
        channel = bot.get_channel(channels['eventos'])
        embed=discord.Embed(title=raid[1], description=raid[2] if descricao is None else descricao, color=0x0000FF)
        embed.set_image(url=raid[3])
        embed.add_field(name="Data/Hora", value=dt_string, inline=False)
        embed.add_field(name=f"\✅ Presente ({num_vagas_reservadas}/{raid[5]})", value="-" if num_vagas_reservadas == 0 else str_reserva, inline=True)
        embed.add_field(name="\❌ Recusado", value="-", inline=True)
        embed.add_field(name="\❔ Sem certeza", value="-", inline=True)
        embed.add_field(name="\🪑 Reserva", value="-", inline=True)
        embed.set_footer(text=f"Evento criado por: {ctx.author.display_name}\nHora: ")
        embed.timestamp = datetime.now()
    
        multi_participation = str(raid[4])
        view = View()
        view.is_persistent()
        view.add_item(Button(custom_id=f'Participar_{multi_participation}', label='✅ Participar', style=discord.ButtonStyle.green))
        view.add_item(Button(custom_id=f'Recusar', label='❌ Recusar', style=discord.ButtonStyle.red))
        view.add_item(Button(custom_id=f'Tentativa', label='❔ Talvez', style=discord.ButtonStyle.blurple))
        view.add_item(Button(custom_id=f'Deletar', label='Deletar evento', style=discord.ButtonStyle.grey))
    
        await channel.send(content=f"{role.mention}", embed=embed, view=view)
        
        events = discord.utils.get(ctx.guild.channels, id = channels['eventos'])
        await ctx.interaction.response.send_message(f"Raid criada com sucesso em {events.mention}! Boa sorte! {morango}", ephemeral=True)
    else:
        await ctx.interaction.response.send_message("Você não tem permissão para executar esse comando!", ephemeral=True)
        
@bot.hybrid_command(brief="Cria uma novo evento para o GVG")
@app_commands.describe(
    data_hora='Data e hora da GVG (siga o formato do exemplo: 30/12/2000 14:00) (OBRIGATÓRIO)',
    descricao='Descrição customizada (opcional)'
    )
async def gvg(ctx, data_hora:str, descricao:str=""):
    if set([role.name for role in ctx.author.roles]).intersection(admin_roles) != set():
        if data_hora is not None: 
            try:
                dt = datetime.strptime(data_hora, '%d/%m/%Y %H:%M')
                dt_string = dt.strftime("%A, %d de %B de %Y - %H:%M")
    
                # dias de semana
                dt_string = dt_string.replace("Monday", "Segunda-Feira").replace("Tuesday", "Terça-Feira").replace("Wednesday", "Quarta-Feira").replace("Thursday", "Quinta-Feira").replace("Friday", "Sexta-Feira").replace("Saturday", "Sábado").replace("Sunday", "Domingo")
                # meses
                dt_string = dt_string.replace("January", "Janeiro").replace("February", "Fevereiro").replace("March", "Março").replace("April", "Abril").replace("May", "Maio").replace("June", "Junho").replace("July", "Julho").replace("August", "Agosto").replace("September", "Setembro").replace("October", "Outubro").replace("November", "Novembro").replace("December", "Dezembro")
            except:
                await ctx.interaction.response.send_message("Data/hora inválida! Digite no formato: dd/MM/aaaa hh:mm", ephemeral=True)
                return
            
        gvg_preset = presets_eventos['GVG']
        role = ctx.guild.default_role
        
        channel = bot.get_channel(channels['eventos'])
        embed=discord.Embed(title=gvg_preset[1], description=gvg_preset[2] if descricao is None else descricao, color=0x0000FF)
        embed.set_image(url=gvg_preset[3])
        embed.add_field(name="Data/Hora", value=dt_string, inline=False)
        embed.add_field(name=f"\✅ Presente (0/{gvg_preset[5]})", value="-", inline=True)
        embed.add_field(name="\❌ Recusado", value="-", inline=True)
        embed.add_field(name="\❔ Sem certeza", value="-", inline=True)
        embed.add_field(name="\🪑 Reserva", value="-", inline=True)
        embed.set_footer(text=f"Evento criado por: {ctx.author}\nHora: ")
        embed.timestamp = datetime.now()
    
        multi_participation = str(gvg_preset[4])
        view = View()
        view.is_persistent()
        view.add_item(Button(custom_id=f'Participar_{multi_participation}', label='✅ Participar', style=discord.ButtonStyle.green))
        view.add_item(Button(custom_id=f'Recusar', label='❌ Recusar', style=discord.ButtonStyle.red))
        view.add_item(Button(custom_id=f'Tentativa', label='❔ Talvez', style=discord.ButtonStyle.blurple))        
        view.add_item(Button(custom_id=f'Deletar', label='Deletar evento', style=discord.ButtonStyle.grey))
        await channel.send(content=f"{role}", embed=embed, view=view)
        
        events = discord.utils.get(ctx.guild.channels, id = channels['eventos'])
        await ctx.interaction.response.send_message(f"Evento de GVG criado com sucesso em {events.mention}! Boa sorte a todos! {morango}", ephemeral=True)
    else:
        await ctx.send("Você não tem permissão para executar esse comando!")

@bot.event
async def on_interaction(interaction):   
    if interaction.channel_id == channels['raids']:
        has_role, role = giveRole(interaction)
    
        if has_role:
            await interaction.user.remove_roles(role) 
            await interaction.response.send_message(content = f"Você não receberá mais avisos de {interaction.data['custom_id']}! :slight_frown:", ephemeral=True) 
        else:
            await interaction.user.add_roles(role)
            events = discord.utils.get(interaction.guild.channels, id = channels['eventos'])
            await interaction.response.send_message(content = f"Você agora receberá avisos de {interaction.data['custom_id']}! Fique de olho em {events.mention} e boa sorte! :hearts:", ephemeral=True) 
      
    elif interaction.channel_id == channels['classes']:
        has_role, role = giveRole(interaction)
        user_roles = [role.name for role in interaction.user.roles]
    
        if has_role: 
            await interaction.user.remove_roles(role) 
            user_roles.remove(role.name)
            roles = set(classes).intersection(user_roles)
            if roles == set(): roles = "Nenhuma"
            await interaction.response.send_message(content = f"Você não tem mais um(a) {interaction.data['custom_id']} cadastrado(a). :slight_frown:\n\nSuas classes cadastradas: {roles}", ephemeral=True)   
        else:
            await interaction.user.add_roles(role)
            user_roles.append(interaction.data['custom_id'])
            await interaction.response.send_message(content = f"Agora você tem um(a) {interaction.data['custom_id']} cadastrado(a)! :hearts:\n\nSuas classes cadastradas: {set(classes).intersection(user_roles)}", ephemeral=True)
    
    elif interaction.channel_id == channels['eventos']: 
        if 'custom_id' in interaction.data.keys(): custom_id = interaction.data['custom_id'].split('_')[0]
        else: custom_id = 'slash_Raid'
        
        if custom_id == 'Participar':
            try: multi_participation = interaction.data['custom_id'].split('_')[1]
            except: multi_participation = "False"
    
            field_name = interaction.message.embeds[0].fields[1].name
            actual_members, max_members = field_name[field_name.find("(")+1:field_name.find(")")].split('/')
            
            if multi_participation == "True":    
                roles = set(classes).intersection([role.name for role in interaction.user.roles])
                if roles == set():
                    canal_classe = discord.utils.get(interaction.guild.channels, id = channels['classes'])
                    await interaction.response.send_message(content = f"Antes de participar de um evento, vá em {canal_classe.mention} e escolha as classes que você joga!", ephemeral=True)
                    return

                modal = SeletorClasse(str(interaction.user.id))
                modal.text.default = ", ".join(roles)

                modal.message_id = interaction.message.id
                if int(actual_members) >= int(max_members): modal.index_to_add = 4
                    
                await interaction.response.send_modal(modal)
            else:
                event_message = interaction.message
                clone_embed = editEmbed(embed=event_message.embeds[0], author_name=interaction.user.display_name, index=1)
                try:
                    await interaction.response.edit_message(embed=clone_embed)
                except:
                    print("Erro ao tentar editar mensagem do evento!")
                    
        elif custom_id == "Recusar":
            event_message = interaction.message
            clone_embed = editEmbed(embed=event_message.embeds[0], author_name=interaction.user.display_name, index=2)
            await interaction.response.edit_message(embed=clone_embed)
    
        elif custom_id == "Tentativa":
            event_message = interaction.message
            clone_embed = editEmbed(embed=event_message.embeds[0], author_name=interaction.user.display_name, index=3)
            await interaction.response.edit_message(embed=clone_embed)
        
        elif custom_id == "Deletar":
            event_message = interaction.message
            event_author=event_message.embeds[0].footer.text.split('\n')[0].replace('Evento criado por: ','')
            if (interaction.user.display_name == event_author) or (set([role.name for role in interaction.user.roles]).intersection(admin_roles)): 
                await interaction.message.delete()
            else: interaction.response.send_message(content = f"Você não foi o criador do evento e/ou não é um admin!", ephemeral=True)
        
@bot.event
async def edit_message_embed(msg, new_embed):
    await msg.edit(embed=new_embed)
    await asyncio.sleep(0.75)

def editEmbed(embed, author_name, index, author_class=[]):
    # 1 - Participar
    # 2 - Recusar
    # 3 - Tentativa
    # 4 - Reserva
    clone_embed = embed
    
    _, participation_text, refusal_text, tentative_text, reserve_text = [field.value for field in clone_embed.fields]
    
    participation_list = participation_text.split("\n")
    refusal_list = refusal_text.split("\n")
    tentative_list = tentative_text.split("\n")
    reserve_list = reserve_text.split("\n")
    
    filtered_list = []
    filtered_str = ''
    
    for i in range(1, 5):
        filtered_list.clear()
        filtered_str = ''
        if i == 1:
            edit_list = participation_list
        if i == 2:
            edit_list = refusal_list
            item_name = "\❌ Recusado"
        if i == 3:
            edit_list = tentative_list
            item_name = "\❔ Sem certeza"
        if i == 4:
            edit_list = reserve_list
            item_name = "\🪑 Reserva"
        
        if index is not i:             
            for member in edit_list:
                if member.find(f" {author_name}") == -1: filtered_list.append("\n"+member)
            filtered_str = ''.join(filtered_list)
            if filtered_str == "": filtered_str = "-"
            
        if index is i:
            if author_class == []: author_string = f"{author_name}"
            else: author_string = f"{author_name} ({', '.join(author_class)})"
            
            if any(f" {author_name}" in name for name in edit_list): # se existe, substitui as classes
                for member in edit_list:
                    if member.find(f" {author_name}") == -1: filtered_list.append("\n"+member)
                    else: 
                        if index in (1, 4):
                            member_classes = member[member.find("(")+1:member.find(")")].split(',')
                            filtered_list.append(f"\n> {author_name} ({','.join(list(set(member_classes)|set(author_class)))})")     
                filtered_str = ''.join(filtered_list)
                if filtered_str == "": filtered_str = "-"
            else: # se não, adiciona
                filtered_str = '\n'.join(edit_list)
                if filtered_str == '-': filtered_str = ''
                filtered_str = filtered_str + f"\n> {author_string}"
        
        if i == 1:
            member_count = filtered_str.count('> ')
            max_member_count = embed.fields[1].name.split('/')[-1].replace(')', '')
            item_name = f"\✅ Presente ({member_count}/{max_member_count})"
        clone_embed.set_field_at(i, name=item_name, value=filtered_str, inline=True)
    return clone_embed

def giveRole(interaction):
    has_role = False
    for roles in interaction.user.roles:
        if interaction.data['custom_id'].upper() == roles.name.upper(): has_role = True
    
    role_id = None
    for roles in interaction.user.guild.roles:
        if roles.name.upper() == interaction.data['custom_id'].upper(): 
            role_id = int(roles.id)
            break
    role = discord.utils.get(interaction.user.guild.roles, id=role_id)
    return has_role, role

if __name__ == "__main__":
    bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
    bot.run(DISCORD_TOKEN)