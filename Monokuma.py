import random
import asyncio
import aiohttp
import json
import os
import discord
from discord.ext import commands
from itertools import cycle
from  datetime import datetime



client = commands.Bot(command_prefix="/")
client.remove_command('help')
idParticipants = []
nameParticipants = []
date=datetime.now()
team1=[]
team2=[]
votes = {}
temps_avant_delete = 10
chanPlayers = {}
game_end = True
maxVote = {}

@client.event
async def on_ready():
   await client.change_presence(game=discord.Game(name='pas grand chose'))
   print('Logged in as ' + client.user.name)

@client.command(pass_context=True)
async def liftoff(ctx):
    if ctx.message.author.server_permissions.administrator:

        await client.change_presence(game=discord.Game(name='préparer le prochain jeu'))

        nbJoueurs = 4
        waitForPlayers = 0

        channel=ctx.message.channel
        chr = await client.send_message(channel, 'Chargement du prochain jeu de la mort...')
        message = ctx.message
        await client.delete_message(message)
        msg = await client.send_message(channel, 'Pupupu bonjour @everyone, une fois de plus votre jeu de la mort favori ouvre ses portes! Cette nouvelle partie possèdera de nouvelles règles et accueillera {} joueurs. Vous pouvez déjà vous inscrire en cliquant sur le dé, ne vous poussez pas pour prendre vos places, je vous attends à l\'intérieur pupupu....'.format(nbJoueurs))
        await client.delete_message(chr)

        await client.add_reaction(msg,'🎲')
        await client.pin_message(msg)
        await asyncio.sleep(0.1)
        while waitForPlayers < nbJoueurs:
            res = await client.wait_for_reaction(['🎲'], message=msg)
            if res.user.id not in idParticipants:
                responses = ['{0.user.mention} va participer, vous n\'êtes pas prêts !'.format(res), 'Pupupu {0.user.mention} s\'est inscrit, je parie sur lui !'.format(res), '{0.user.mention} a décidé de jouer? J\'espère qu\'il sait ce qu\'il fait...'.format(res), 'Oh non pas {0.user.mention}, j\'espère qu\'il mourra en premier...'.format(res), 'Finalement {0.user.mention} s\'est inscrit, il a pris son temps pour décider.'.format(res), 'Félicitez {0.user.mention}, il a décidé de participer !'.format(res), 'C\'est la première partie de {0.user.mention} soyez cléments... Je rigole pupupu!'.format(res), '{0.user.mention} s\'est inscrit, ne lui faites pas confiance.'.format(res)]
                await client.send_message(channel, random.choice(responses))
                idParticipants.append(res.user.id)
                nameParticipants.append(res.user)
                votes[res.user]=0
                maxVote[res.user]=False
                waitForPlayers +=1
            else :
                await client.say('Pu ? Tu es déjà inscrit toi.')

        await client.send_message(channel,'Tous les participants sont inscrits ! Le jeu commencera à 21H !')
        await client.unpin_message(msg)
        await client.delete_message(msg)


        actualDate = datetime.now()
        remainingSeconds = (21*60*60) - ((actualDate.hour*60*60) + (actualDate.minute*60))                      #Attente de 21h, le début de la partie et arrivée de tous les joueurs\ Point de départ en cas de plantage
        if actualDate.hour >= 21 :
            remainingSeconds += 24*60*60
        #wait asyncio.sleep(remainingSeconds)
        await asyncio.sleep(10)


        role = await client.create_role(message.server, name = 'Participant', colour = discord.Colour(0xeb3136), create_instant_invite = False, send_tts_messages=False,change_nickname=False,embed_links=False,attach_files=False,mention_everyone=False)
        spec_role= await client.create_role(message.server, name = 'Spectateur', colour = discord.Colour(0xcbebfd), create_instant_invite = False, send_tts_messages=False,change_nickname=False,embed_links=False,attach_files=False,mention_everyone=False)
        await asyncio.sleep(1)
        role = discord.utils.get(message.server.roles, name='Participant')
        await asyncio.sleep(1)

        everyone_perms = discord.PermissionOverwrite(read_messages=False)
        player_perms = discord.PermissionOverwrite(read_messages=True)
        spec_perms = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        everyone = discord.ChannelPermissions(target=message.server.default_role, overwrite=everyone_perms)
        joueurs = discord.ChannelPermissions(target = role , overwrite =player_perms)
        spec = discord.ChannelPermissions(target = spec_role, overwrite=spec_perms)

        await asyncio.sleep(1)
        main_chan = await client.create_channel(message.server, 'general', everyone, joueurs,spec)

        players_chans = []
        for player in nameParticipants :
            await client.add_roles(player, role)
            name = str(player)
            name = name[0:-4]
            player_chan_perms = discord.ChannelPermissions(target=player, overwrite=player_perms)
            player_chan = await client.create_channel(message.server, name,everyone, player_chan_perms)
            await asyncio.sleep(1)
            chanPlayers[player.id] = player_chan.name
            players_chans.append(player_chan)
            await client.send_message(ctx.message.author, player_chan.name)

        participants_trash = list(nameParticipants)
        team = '1'
        teamAdv = '2'
        responses = ['Tu es dans l\'équipe {}. Pupupu bonne chance pour trouver tes alliés et te débarrasser de l\'équipe {}. Je peux t\'aider à les battre, j\'ai jamais aimé l\'équipe {}. Je rigole pupupu je veux juste vous voir vous entretuer.'.format(team, teamAdv, teamAdv), 'T\'es dans l\'équipe {} t\'as intérêt à botter les fesses de l\'équipe {} sinon je vais m\'ennuyer'.format(team, teamAdv)]
        for player in range(nbJoueurs//2):
            trash_player = random.choice(participants_trash)
            participants_trash.remove(trash_player)
            team1.append(trash_player)
            await client.send_message(trash_player, random.choice(responses))

        team = '2'
        teamAdv = '1'
        responses = ['Tu es dans l\'équipe {}. Pupupu bonne chance pour trouver tes alliés et te débarrasser de l\'équipe {}. Je peux t\'aider à les battre, j\'ai jamais aimé l\'équipe {}. Je rigole pupupu je veux juste vous voir vous entretuer.'.format(team, teamAdv, teamAdv), 'T\'es dans l\'équipe {} t\'as intérêt à botter les fesses de l\'équipe {} sinon je vais m\'ennuyer'.format(team, teamAdv)]
        for player in range(nbJoueurs//2):
            trash_player = random.choice(participants_trash)
            participants_trash.remove(trash_player)
            team2.append(trash_player)
            await client.send_message(trash_player, random.choice(responses))

        await client.change_presence(game=discord.Game(name='tuer des gens. Principalement.'))


        game_end = False
        while not game_end:

            date_start = datetime.now()

            for joueur in votes.keys():
                votes[joueur]=0
                maxVote[joueur]=False

            await asyncio.sleep(86400)
            #await asyncio.sleep(60)

            master_voted = None
            nbMaxVote = 0
            for joueur in votes.keys():
                if nbMaxVote < votes.get(joueur):
                    master_voted = joueur
                    nbMaxVote = votes.get(joueur)

                elif nbMaxVote == votes.get(joueur):
                    master_voted=None

            if master_voted != None:

                if nbMaxVote ==1:
                    await client.send_message(main_chan, '{} a été éliminé. {} joueur a souhaité sa mort.'.format(master_voted.mention, nbMaxVote))
                else :
                    await client.send_message(main_chan, '{} a été éliminé. {} joueurs ont souhaité sa mort.'.format(master_voted.mention, nbMaxVote))

                if master_voted in team1:
                    team1.remove(master_voted)

                elif master_voted in team2:
                    team2.remove(master_voted)

                nameParticipants.remove(master_voted)
                idParticipants.remove(master_voted.id)
                nbJoueurs -= 1
                del votes[master_voted]

                member_voted = discord.utils.get(message.server.members, name=master_voted.name)
                role = discord.utils.get(message.server.roles, name='Participant')
                for salon in players_chans:
                    await client.delete_channel_permissions(salon,member_voted)
                await client.remove_roles(member_voted, role)
                name_voted = master_voted.name
                channel_del = discord.utils.get(message.server.channels, name=name_voted.lower())
                await client.delete_channel(channel_del)
                await client.add_roles(member_voted, spec_role)
                del chanPlayers[member_voted.id]
                players_chans.remove(channel_del)

                if team1 == []:
                    await client.send_message(main_chan, 'L\'équipe 1 a été exterminée. L\'équipe 2 remporte le jeu.')
                    game_end = True

                if team2 == []:
                    await client.send_message(main_chan, 'L\'équipe 1 a été exterminée. L\'équipe 2 remporte le jeu.')
                    game_end = True

            else:
                await client.send_message(main_chan, 'Personne n\'est mort aujourd\'hui')

        client.remove_command('vote')
        await client.send_message(main_chan, 'Merci d\'avoir joué ! (et merci Moky)')
        await client.send_message(main_chan, 'Toute trace de la partie sera effacée dans 2h')

        await asyncio.sleep(temps_avant_delete)

        role = discord.utils.get(message.server.roles, name='Participant')
        await client.delete_role(ctx.message.server, role)
        await client.delete_role(ctx.message.server,spec_role)
        await client.delete_channel(main_chan)
        for channels in players_chans:
            await client.delete_channel(channels)

        await client.change_presence(game=discord.Game(name='pas grand chose'))

    else :
        await client.say('Vous n\'êtes pas autorisé à utiliser cette commande')

@client.command(pass_context=True)
async def vote(ctx, vote):
    if ctx.message.channel.name == chanPlayers.get(ctx.message.author.id):
        if not maxVote.get(ctx.message.author):
            try:
                id= vote[2:-1]
                vote = await client.get_user_info(id)
                votes[vote] += 1
                maxVote[ctx.message.author]=True
                await client.send_message(ctx.message.channel, 'Votre vote contre {} a été enregistré'.format(vote.mention))
            except :
                await client.send_message(ctx.message.channel, 'nom invalide')
        else :
            await client.send_message(ctx.message.channel, 'Vous avez déjà voté ce tour')
    else:
        await client.send_message(ctx.message.channel, 'Tu nous fais quoi la {} ? Tu dois écrire ça sur ton salon privé !'.format(ctx.message.author.mention))


@client.command(pass_context=True)
async def team(ctx):
    if ctx.message.channel.name == chanPlayers.get(ctx.message.author.id):
        if ctx.message.author in team1:
            await client.send_message(ctx.message.author,'Vous êtes dans l\'équipe 1.')

        elif ctx.message.author in team2:
            await client.send_message(ctx.message.author,'Vous êtes dans l\'équipe 2.')

    else :
        await client.say('Tu nous fais quoi la {} ? Tu dois écrire ça sur ton salon privé !'.format(ctx.message.author.mention))



@client.command(pass_context=True)
async def invite(ctx, invited):
    if ctx.message.channel.name == chanPlayers.get(ctx.message.author.id):
        try:
            id= invited[2:-1]
            invited = await client.get_user_info(id)
            invited_chan_name = str(invited)[0:-5].lower()
            chan = discord.utils.get(ctx.message.server.channels, name=invited_chan_name)
            await client.send_message(chan, '{} vous a invité à converser'.format(ctx.message.author.mention))
            await client.say('{} a bien été invité à vous rejoindre'.format(invited.mention))
        except:
            await client.say('nom d\'invité invalide')
        response=False
        while not response:
            repB= await client.wait_for_message(channel=chan)
            rep=repB.content
            if repB.author.name.lower()==chan.name:
                if rep=='/accept {}'.format(ctx.message.author.mention):
                    response=True
                    overwrite = discord.PermissionOverwrite()
                    overwrite.read_messages=True
                    await client.edit_channel_permissions(ctx.message.channel,repB.author, overwrite)
                    await client.send_message(ctx.message.channel,'{} est arrivé'.format(invited.mention))

                elif rep=='/reject {}'.format(ctx.message.author.mention):
                    response=True
                    await client.send_message(chan, 'Vous avez refusé l\'invitation de {}'.format(ctx.message.author.mention))
                    await client.send_message(ctx.message.channel, '{} a refusé votre invitation'.format(invited.mention))

    else :
        await client.say('Tu nous fais quoi la {} ? Tu dois écrire ça sur ton salon privé !'.format(ctx.message.author.mention))


@client.command(pass_context=True)
async def eject(ctx, invited):
    if ctx.message.channel.name == chanPlayers.get(ctx.message.author.id):
        try:
            id= invited[2:-1]
            invited = discord.utils.get(ctx.message.server.members, id=id)
            invited_chan_name=str(invited)[0:-5].lower()
            chan=discord.utils.get(ctx.message.server.channels, name=invited_chan_name)
        except:
            await client.say('nom invalide')

        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages=False
        await client.edit_channel_permissions(ctx.message.channel,invited, overwrite)
        await client.send_message(ctx.message.channel,'{} a été expulsé'.format(invited.mention))
        await client.send_message(chan, '{} vous a expulsé'.format(ctx.message.author.mention))

    else :
        await client.say('Tu nous fais quoi la {} ? Tu dois écrire ça sur ton salon privé !'.format(ctx.message.author.mention))

@client.command(pass_context = True)
async def clear(ctx, amount=10000):
    if ctx.message.channel.name == chanPlayers.get(ctx.message.author.id):
        channel=ctx.message.channel
        messages=[]
        async for message in client.logs_from(channel,limit=int(amount)+1):
            messages.append(message)
        await client.delete_messages(messages)
        msg = await client.say("Hop j'ai effacé tous tes messages pupupu !")
        await asyncio.sleep(2)
        await client.delete_message(msg)

    else :
        await client.say('Tu nous fais quoi la {} ? Tu dois écrire ça sur ton salon privé !'.format(ctx.message.author.mention))

@client.command(pass_context = True)
async def backup(ctx, backup_name):
    if ctx.message.channel.name == chanPlayers.get(ctx.message.author.id):
        channel=ctx.message.channel
        await client.delete_message(ctx.message)
        messages=[]
        messages_content=[]
        async for message in client.logs_from(channel):
            messages.append(message)
            messages_content.append(message.content)
        await client.purge_from(channel)
        await client.say('Tes messages ont été enregistrés sous "{}"'.format(backup_name))
        msg = await client.wait_for_message(content = '/load {}'.format(backup_name))
        for message in messages_content:
            await client.send_message(msg.channel, message)
        await client.send_message(msg.channel, 'Profite de ces messages !')


    else :
        await client.say('Tu nous fais quoi la {} ? Tu dois écrire ça sur ton salon privé !'.format(ctx.message.author.mention))

@client.command(pass_context=True)
async def players(ctx):
    if ctx.message.author.server_permissions.administrator:
        for _ in range(len(idParticipants)):
            await client.say('<@{}>'.format(idParticipants[_]))
    else :
        await client.say('Vous n\'êtes pas autorisé à utiliser cette commande')

client.run(os.getenv('TOKEN'))
