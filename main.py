import discord
import os
import time

import random

import discord.ext
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, check

intents = discord.Intents().all()

bot = commands.Bot(command_prefix='!',
                   intents=intents)  #put your own prefix here


list_participant = []

msg_lobby = None
msg_radi = None
msg_dire = None
msg_inst = None
msg_role_radi = None
msg_role_dire = None

list_radi = []
list_dire = []

fix_pos_radi = {1: [], 2: [], 3: [], 4: [], 5: []}
fix_pos_dire = {1: [], 2: [], 3: [], 4: [], 5: []}

lobby_id = None



def init_all():
    global list_participant, msg_lobby, msg_radi, msg_dire, msg_inst, msg_role_radi, msg_role_dire, list_radi, list_dire, fix_pos_radi, fix_pos_dire, lobby_id
    list_participant = []
    msg_lobby = None
    msg_radi = None
    msg_dire = None
    msg_inst = None
    msg_role_radi = None
    msg_role_dire = None

    list_radi = []
    list_dire = []

    fix_pos_radi = {1: [], 2: [], 3: [], 4: [], 5: []}
    fix_pos_dire = {1: [], 2: [], 3: [], 4: [], 5: []}

    lobby_id = None

    return

async def update_participant_list(reaction, user, check_emoji="👍"):
    if user.bot == True:
        return

    global list_participant

    if reaction.message.id == msg_lobby.id:
        list_participant = []
        for reaction in reaction.message.reactions:
            if reaction.emoji != check_emoji:
                continue
            async for user in reaction.users():
                if not user.bot:
                    list_participant.append(user.name)

        print(list_participant)

        number_lp = [
            f"{i+1}. {name}"
            for i, name in zip(range(len(list_participant)), list_participant)
        ]

        if len(number_lp) == 10:
            suffix = "\n\n=== Lobby is ready. Type !go to proceed ===\n```"
        else:
            suffix = "\n```"

        await reaction.message.edit(content=f"```\nLobby ID: {msg_lobby.id} \nList of participants:\n" +
                                    ('\n').join(number_lp) + suffix)


async def update_role_selection(reaction, user):
    if user.bot == True:
        return

    global fix_pos_radi, fix_pos_dire, list_radi, list_dire

    mapping_emoji_pos = {"1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5}
    if msg_radi is not None and reaction.message.id == msg_radi.id:
        fix_pos_radi = {1: [], 2: [], 3: [], 4: [], 5: []}
        print('\nreset radi dict\n')
        print(fix_pos_radi)
        for reaction in reaction.message.reactions:
            if mapping_emoji_pos.get(reaction.emoji, 0) > 0:
                async for user in reaction.users():
                    if not user.bot and user.name in list_radi:
                        fix_pos_radi[mapping_emoji_pos.get(reaction.emoji, 0)].append(user.name)

        print("radiant: " + str(fix_pos_radi))

    if msg_dire is not None and reaction.message.id == msg_dire.id:
        fix_pos_dire = {1: [], 2: [], 3: [], 4: [], 5: []}
        for reaction in reaction.message.reactions:
            if mapping_emoji_pos.get(reaction.emoji, 0) > 0:
                async for user in reaction.users():
                    if not user.bot and user.name in list_dire:
                        fix_pos_dire[mapping_emoji_pos.get(reaction.emoji, 0)].append(user.name)

        print("dire: " + str(fix_pos_dire))


async def show_team_assignment(ctx):
    global list_participant, msg_radi, msg_dire, msg_inst, list_radi, list_dire, fix_pos_radi, fix_pos_dire

    number_lp = [
        f"{i+1}. {name}"
        for i, name in zip(range(len(list_participant)), list_participant)
    ]

    print(list_participant)
    if msg_radi is not None:
        await msg_radi.delete()
    if msg_dire is not None:
        await msg_dire.delete()
    if msg_inst is not None:
        await msg_inst.delete()

    msg_radi = await ctx.send("```\n=== Radiant ===\n" +
                              ('\n').join(number_lp[0:5]) + 
                              "\n```")
    msg_dire = await ctx.send("```\n===  Dire  ===\n" +
                              ('\n').join(number_lp[5:10]) + 
                              "\n```")

    for msg in [msg_radi, msg_dire]:
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]:
            await msg.add_reaction(emoji)

    msg_inst = await ctx.send("```\nUse !shuffle again to reroll. !swap a b to switch player.\n\nOnce everyone is done selecting role, press !go to proceed\n```")

    list_radi = list_participant[0:5]
    list_dire = list_participant[5:10]

    fix_pos_radi = {1: [], 2: [], 3: [], 4: [], 5: []}
    fix_pos_dire = {1: [], 2: [], 3: [], 4: [], 5: []}





@bot.command()
async def createlobby(ctx):
    global msg_lobby, lobby_id
    role = get(ctx.guild.roles, name="Dota Lobby Notification")
    print(role)
    await ctx.send(f"Dota lobby has been created! Press 👍 to join {role.mention}")
    msg_lobby = await ctx.send(f"```\nLobby ID: ... \nList of participants:\n```")
    await msg_lobby.add_reaction("👍")
    lobby_id = msg_lobby.id


@bot.command()
async def shuffle(ctx, arg=""):
    global list_participant, msg_lobby
    if arg == '--force':
        list_participant = list_participant + [
            f"dummy{i+1}" for i in range(10 - len(list_participant))
        ]

    if len(list_participant) != 10:
        await ctx.send(f"Invalid number of player: {len(list_participant)}")
        return

    await msg_lobby.delete()

    random.shuffle(list_participant)
    await show_team_assignment(ctx)


@bot.command()
async def swap(ctx, arg1, arg2):
    global list_participant

    temp = list_participant[int(arg1) - 1]
    list_participant[int(arg1) - 1] = list_participant[int(arg2) - 1]
    list_participant[int(arg2) - 1] = temp

    await show_team_assignment(ctx)

@bot.command()
async def go(ctx):
    global msg_lobby, msg_radi, msg_dire, msg_inst, list_radi, list_dire, fix_pos_radi, fix_pos_dire, msg_role_radi, msg_role_dire, lobby_id

    await msg_radi.delete()
    await msg_dire.delete()
    await msg_inst.delete()

    print('rad:' + str(fix_pos_radi))
    print('dir:' + str(fix_pos_dire))

    random.shuffle(list_radi)
    random.shuffle(list_dire)

    fix_pos_radi_transpose = {nm: [] for nm in list_radi}
    fix_pos_dire_transpose = {nm: [] for nm in list_dire}

    for (pos, list_nm) in fix_pos_radi.items():
        list_nm = list(set(list_nm))
        for nm in list_nm:
            fix_pos_radi_transpose[nm].append(pos)

    for (pos, list_nm) in fix_pos_dire.items():
        list_nm = list(set(list_nm))
        for nm in list_nm:
            fix_pos_dire_transpose[nm].append(pos)

    list_radi_role = [None, None, None, None, None]
    list_dire_role = [None, None, None, None, None]

    print('trans radi: ' + str(fix_pos_radi_transpose))
    print('trans dire: ' + str(fix_pos_dire_transpose))

    ####radi assign ###
    recheck = True
    num_assigned = 0
    free_agent_radi = []
    while recheck:
        recheck = False
        for (nm, list_pos) in fix_pos_radi_transpose.items():
            if len(list_pos) == 0:
                free_agent_radi.append(nm)
                print(f"assigned {nm} to free agent")
                del fix_pos_radi_transpose[nm]
                recheck = True
                break
            if len(list_pos) == 1:
                pos = list_pos[0]
                if list_radi_role[pos-1] is None:
                    list_radi_role[pos-1] = nm
                    print(f"assigned {nm} to {pos}")
                    num_assigned = num_assigned+1
                    for (nm_2, list_pos_2) in fix_pos_radi_transpose.items():
                        if pos in list_pos_2:
                            list_pos_2.remove(pos)
                    del fix_pos_radi_transpose[nm]
                    recheck = True
                    break

        if num_assigned + len(free_agent_radi) == 5:
            break

        if not recheck:
            (nm, list_pos) = list(fix_pos_radi_transpose.items())[0]
            list_radi_role[list_pos[0]-1] = nm
            print(f"assigned2 {nm} to {list_pos[0]}")
            num_assigned = num_assigned+1
            for (nm, list_pos) in fix_pos_radi_transpose.items():
                list_pos.remove(list_pos[0])
            del fix_pos_radi_transpose[nm]
            recheck = True

    print(str(list_radi_role) + str(free_agent_radi))

    if len(free_agent_radi) > 0:
        random.shuffle(free_agent_radi)
        ind = 0
        for i in range(5):
            if list_radi_role[i] is None:
                list_radi_role[i] = free_agent_radi[ind]
                ind = ind+1
    print('radi: ' + str(list_radi_role))


    ####dire assign ###
    recheck = True
    num_assigned = 0
    free_agent_dire = []
    while recheck:
        recheck = False
        for (nm, list_pos) in fix_pos_dire_transpose.items():
            if len(list_pos) == 0:
                free_agent_dire.append(nm)
                print(f"assigned {nm} to free agent")
                del fix_pos_dire_transpose[nm]
                recheck = True
                break
            if len(list_pos) == 1:
                pos = list_pos[0]
                if list_dire_role[pos-1] is None:
                    list_dire_role[pos-1] = nm
                    print(f"assigned {nm} to {pos}")
                    num_assigned = num_assigned+1
                    for (nm_2, list_pos_2) in fix_pos_dire_transpose.items():
                        if pos in list_pos_2:
                            list_pos_2.remove(pos)
                    del fix_pos_dire_transpose[nm]
                    recheck = True
                    break

        if num_assigned + len(free_agent_dire) == 5:
            break

        if not recheck:
            (nm, list_pos) = list(fix_pos_dire_transpose.items())[0]
            list_dire_role[list_pos[0]-1] = nm
            print(f"assigned2 {nm} to {list_pos[0]}")
            num_assigned = num_assigned+1
            for (nm, list_pos) in fix_pos_dire_transpose.items():
                list_pos.remove(list_pos[0])
            del fix_pos_dire_transpose[nm]
            recheck = True

    print(str(list_dire_role) + str(free_agent_dire))

    if len(free_agent_dire) > 0:
        random.shuffle(free_agent_dire)
        ind = 0
        for i in range(5):
            if list_dire_role[i] is None:
                list_dire_role[i] = free_agent_dire[ind]
                ind = ind+1
    print('dire: ' + str(list_dire_role))


    list_name_position = ['Carry', 'Mid', 'Offlane', 'Soft support', 'Hard support']
    
    role_radi = [f"`{posnm:>13}:` ||`{nm:^40}`||" for (posnm, nm) in zip(list_name_position, list_radi_role)]
    role_dire = [f"`{posnm:>13}:` ||`{nm:^40}`||" for (posnm, nm) in zip(list_name_position, list_dire_role)]

    str_radi = "```\n=== Radiant roles === " + str(list_participant[0:5]) + "\n```" + ('\n').join(role_radi) + "\n"
    str_dire = "```\n===   Dire  roles === " + str(list_participant[5:10]) + "\n```" + ('\n').join(role_dire) + "\n"
    str_end = f"```\nLobby ID: {lobby_id} GLHF!\n```"

    msg_role_radi = await ctx.send(str_radi + str_dire + str_end)

    init_all()




@bot.event
async def on_ready():
    init_all()
    print("bot online")


@bot.event
async def on_reaction_add(reaction, user):
    await update_participant_list(reaction, user, check_emoji="👍")
    await update_role_selection(reaction, user)


@bot.event
async def on_reaction_remove(reaction, user):
    await update_participant_list(reaction, user, check_emoji="👍")
    await update_role_selection(reaction, user)

    # await reaction.message.channel.send(f"{user.display_name} reacted to msg id {reaction.message.id} {reaction.emoji}")


bot.run(os.getenv("TOKEN"))
