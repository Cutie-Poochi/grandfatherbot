# from discord.ext import commands
from grandfatherNonMainStuff import *
from json import load, decoder
from datetime import timedelta
# from PIL import ImageFont
from io import StringIO
from time import time
import discord
import asyncio
import random
import math
import sys

def main():

    prefix = {'g!'}
    client = ReactiveBot(command_prefix=prefix, case_insensitive=True)
    grandfatherToken = sys.argv[1]
    syncChannelId = 912385336737406997
    syncChannel: discord.TextChannel
    data = {}
    bootyUrl = "https://cdn.discordapp.com/emojis/912671147961749544.png"
    blackjack_messages = {}
    emojis = {
        'pepega': "<:pepega:885174483906867200>",
        'booty': "<:booty:917377961789915146>",
        'hit': "👋",
        'stand': "🤚",
        'double down': "👐",
        'surrender': "🏳",
        'split': "✌️"
    }
    # maxMessageLength = 2000
    # embedSpace = "<:embedspace:917379175663435776>" # "<:white:917384444594237441>"
    # font = ImageFont.truetype('Assets/DejaVuSans.ttf', 512)
    # fontBold = ImageFont.truetype('Assets/DejaVuSans-Bold.ttf', 512)

    """
    cases where people have used a command wrongly are just called "# SYNTAXERROR", saving it for the roasts
    naice I know
    """

    def check_admin(man): return str(man.id) in data['admins']

    def draw_blackjack_card():
        if len(data['blackjackDeck']) == 0:
            data['blackjackDeck'] = generate_blackjack_deck(int(data['settings']['blackjackDecks']))
        return Card(data['blackjackDeck'].pop(0))

    def generate_blackjack_embed(desc: str, man: discord.member.Member, manHand, dealerHand, result=''):
        embed = discord.Embed(description=desc, colour=discord.Colour.from_rgb(128, 128, 128)) \
            .set_footer(text="Cards Remaining: {}.\n\n".format(len(data['blackjackDeck']))) \
            .set_author(name=man.display_name, icon_url=man.avatar_url)
        manHandValue = blackjack_get_hand_value(manHand)
        manHandDesc = ", ".join(str(card) for card in manHand) + "\n"
        if manHandValue[0] == 21 and len(manHand) == 2:
            manHandDesc += "Value: Blackjack\n"
        else:
            manHandDesc += "Value: " + blackjack_get_hand_str_value(manHandValue) + "\n"
        if result:
            manHandDesc += "Result: " + result + "\n"
        embed.add_field(name="Your Hand", value=manHandDesc)
        dealerHandValue = blackjack_get_hand_value(dealerHand)
        showDealerResult = len(dealerHand) > 1
        if showDealerResult:
            dealerHandDesc = "Dealer Hand: " + ", ".join(str(card) for card in dealerHand) + "\n"
            if dealerHandValue[0] == 21 and len(dealerHand) == 2:
                dealerHandDesc += "Value: Blackjack\n"
            else:
                dealerHandDesc += "Value: " + str(blackjack_get_hand_str_value(dealerHandValue)) + "\n"
        else:
            dealerHandDesc = str(dealerHand[0]) + ", XX\nValue: " + blackjack_get_hand_str_value(dealerHandValue) + "\n"
        embed.add_field(name="Dealer's Hand: ", value=dealerHandDesc)
        return embed

    # incase we gotta modify data ourselves
    @client.command(aliases=('manual', 'md'))
    async def manual_data(ctx: commands.Context):
        nonlocal data
        if not check_admin(ctx.author):
            return
        if len(ctx.message.attachments) == 0:
            await export_data(data, syncChannel)
            return
        fileObject = ctx.message.attachments[0]
        await fileObject.save(fp="grandfatherdata.json")
        with open("grandfatherdata.json", 'r') as dataFile:
            dataContent = dataFile.read()
        try:
            data = load(StringIO(dataContent))
        except decoder.JSONDecodeError:
            await ctx.send("File not recognized as json.")
            return
        await export_data(data, syncChannel)
        await ctx.send("Done.")

    async def set_stat(man: discord.member.Member, stat, value, save):
        manId = str(man.id)
        men = data['men']
        defaultValues = men['default']
        if stat not in defaultValues:
            return "{} is an invalid stat.".format(stat)
        if manId not in men:
            data['men'][manId] = defaultValues.copy()
        data['men'][manId][stat] = value
        if save:
            await export_data(data, syncChannel)
        return "Set {} of {} to {}.".format(stat, man.display_name, value)

    @client.command(aliases=['pn'])
    async def ping(ctx: commands.Context): await ctx.send("{}ms.".format(round(client.latency * 1000)))

    @client.command(aliases=('say', 's'))
    async def echo(ctx: commands.Context, *args):
        await ctx.send(' '.join(args))

    @client.command(aliases=('admins', 'ad'))
    async def admin(ctx: commands.Context, operation, targetMan):
        if not check_admin(ctx.author):
            return
        man = ctx.guild.get_member_named(targetMan)
        if not man:
            try:
                man = await ctx.guild.fetch_member(extract_id(targetMan))
            except ValueError:
                # SYNTAXERROR
                return
        if operation in {'add', 'a'}:
            if man:
                if check_admin(man):
                    await ctx.send("{} is already an admin.".format(man.name))
                    return
                data['admins'].append(str(man.id))
                await export_data(data, syncChannel)
                await ctx.send("{} is now an admin.".format(man.name))
        elif operation in {'remove', 'r'}:
            if man:
                if not check_admin(man):
                    await ctx.send("{} was not an admin.".format(man.name))
                    return
                data['admins'].remove(str(man.id))
                await export_data(data, syncChannel)
                await ctx.send("{} is no longer an admin.".format(man.name))
        else:
            # SyntaxError
            return
        if not man:
            await ctx.send("Man not found.")

    @client.command(aliases=('set', 'stat', 'ss'))
    async def setstat(ctx: commands.Context, man, stat, value):
        if not check_admin(ctx.author):
            return
        if len(value) == 0:
            # SYNTAXERROR
            return
        if ctx.guild.get_member_named(man):
            man = ctx.guild.get_member_named(man)
        else:
            try:
                man = await ctx.guild.fetch_member(extract_id(man))
            except ValueError:
                # SYNTAXERROR
                return
        await ctx.channel.send(await set_stat(man, stat, value, True))

    @client.command(aliases=['pl'])
    async def plunder(ctx: commands.Context):
        runTime = math.floor(time())
        man = ctx.author
        manId = str(man.id)
        booty, totalBooty = 0, 0
        if manId in data['men']:
            booty = int(data['men'][manId]['booty'])
            totalBooty = booty + int(data['men'][manId]['vault'])
            lastPlunderTime = int(data['men'][manId]['lastPlunder'])
            plunderCooldown = int(data['settings']['plunderCooldown'])
            if runTime - lastPlunderTime < plunderCooldown:
                timeLeft = math.ceil(plunderCooldown - runTime + lastPlunderTime)
                embed = discord.Embed(colour=discord.Colour.from_rgb(80, 22, 110)) \
                    .set_footer(text="To:" + man.display_name) \
                    .add_field(name="You already plundered.",
                               value="You can plunder in {}.".format(timedelta(seconds=timeLeft)))
                await ctx.channel.send(embed=embed)
                return
        await set_stat(man, 'lastPlunder', runTime, False)
        variance = 175 * (random.random() - 0.5)
        if totalBooty >= 0:
            plundered = math.floor(variance + 1.1 ** (60 - 0.1 * totalBooty) / 2 - 75)
        else:
            variance += (0.135 + (random.random() - 0.5) * 0.07) * totalBooty
            plundered = math.floor(variance + 500 / (totalBooty - 20) - totalBooty / 5 + 102.24)
        await set_stat(man, "booty", booty + plundered, True)
        if plundered > 0:
            title = "You plundered {:,}{} boy.".format(plundered, emojis['booty'])
            embed = discord.Embed(colour=discord.Colour.from_rgb(72, 219, 156))
        elif plundered < 0:
            title = "You lost {:,}{} to the aristocrats.".format(plundered, emojis['booty'])
            embed = discord.Embed(colour=discord.Colour.from_rgb(230, 69, 128))
        else:
            title = "Congrats, You're a blige-sucking parasite, you didn't even lose any {}.".format(emojis['booty'])
            embed = discord.Embed(colour=discord.Colour.from_rgb(150, 150, 150))
        embed.set_footer(text="To:{}".format(man.display_name))\
            .add_field(name=title, value="You currently have {:,}{}.".format(booty + plundered, emojis['booty']))
        await ctx.channel.send(embed=embed)

    @client.command(aliases=['dep'])
    async def deposit(ctx: commands.Context, depositAmount):
        man = ctx.author
        manId = str(man.id)
        if manId not in data['men']:
            await ctx.send("You don't even have anything.")
            return
        booty = int(data['men'][manId]['booty'])
        vault = int(data['men'][manId]['vault'])
        if depositAmount in {'all', 'a'}:
            amountToDeposit = booty
        elif depositAmount in {'half', 'h'}:
            amountToDeposit = booty // 2
        elif depositAmount[-1] == "%":
            try:
                percentage = int(depositAmount[:-1])
                if percentage <= 0 or percentage > 100:
                    await ctx.send("A percentage must be between 0 and 100.")
                    return
                amountToDeposit = (booty * percentage) // 100
            except ValueError:
                await ctx.send("Not an integre percentage sonny.")
                return
        else:
            try:
                amountToDeposit = int(depositAmount)
            except ValueError:
                await ctx.send("Not an amount of {} sonny.".format(emojis['booty']))
                return
        if amountToDeposit <= 0:
            await ctx.send("You can't deposit {:,}{} fuckling.".format(amountToDeposit, emojis['booty']))
            return
        if amountToDeposit > booty:
            await ctx.send("That's more than you have.")
            return
        depositPrice = math.ceil(amountToDeposit * float(data['settings']['depositPricePercentage']))
        amountToDeposit -= depositPrice
        if amountToDeposit <= 0:
            await ctx.send("You won't have nothing to deposit after paying the price of depositing.")
            return
        await set_stat(man, 'booty', booty - amountToDeposit - depositPrice, False)
        await set_stat(man, 'vault', vault + amountToDeposit, True)
        embed = discord.Embed(colour=discord.Colour.from_rgb(160, 176, 12))\
            .set_footer(text="To: {}".format(man.display_name))\
            .add_field(name="Yourself", value="You have {:,}{}"
                       .format(booty - amountToDeposit - depositPrice, emojis['booty']), inline=False)\
            .add_field(name="Vault", value="You have {:,}{}"
                       .format(vault + amountToDeposit, emojis['booty']), inline=False)
        await ctx.send("You paid {0:,}{1} to deposit {2:,}{1}"
                       .format(depositPrice, emojis['booty'], amountToDeposit), embed=embed)

    @client.command(aliases=['wd'])
    async def withdraw(ctx: commands.Context, withdrawAmount):
        man = ctx.author
        manId = str(man.id)
        if manId not in data['men']:
            await ctx.send("You don't even have anything.")
            return
        booty = int(data['men'][manId]['booty'])
        vault = int(data['men'][manId]['vault'])
        if withdrawAmount in {'all', 'a'}:
            amountToWithdraw = vault
        elif withdrawAmount in {'half', 'h'}:
            amountToWithdraw = vault // 2
        elif withdrawAmount[-1] == "%":
            try:
                percentage = int(withdrawAmount[:-1])
                if percentage <= 0 or percentage > 100:
                    await ctx.send("A percentage must be between 0 and 100.")
                    return
                amountToWithdraw = (vault * percentage) // 100
            except ValueError:
                await ctx.send("Not a integre percentage sonny.")
                return
        else:
            try:
                amountToWithdraw = int(withdrawAmount)
            except ValueError:
                await ctx.send("Not an amount of {} sonny.".format(emojis['booty']))
                return
        if amountToWithdraw <= 0:
            await ctx.send("You can't withdraw {:,}{} fuckling.".format(amountToWithdraw, emojis['booty']))
            return
        if amountToWithdraw > vault:
            await ctx.send("That's more than you have in the vault.")
            return
        await set_stat(man, 'booty', booty + amountToWithdraw, False)
        await set_stat(man, 'vault', vault - amountToWithdraw, True)
        embed = discord.Embed(colour=discord.Colour.from_rgb(160, 176, 12))\
            .set_footer(text="To: {}".format(man.display_name))\
            .add_field(name="Yourself", value="You have {:,}{}"
                       .format(booty + amountToWithdraw, emojis['booty']), inline=False)\
            .add_field(name="Vault", value="You have {:,}{}"
                       .format(vault - amountToWithdraw, emojis['booty']), inline=False)
        await ctx.send("You withdrew {:,}{}".format(amountToWithdraw, emojis['booty']), embed=embed)

    @client.command(aliases=['bal'])
    async def balance(ctx: commands.Context):
        man = ctx.author
        manId = str(man.id)
        if manId not in data['men']:
            await ctx.send("You don't even have anything.")
            return
        booty = int(data['men'][manId]['booty'])
        vault = int(data['men'][manId]['vault'])
        embed = discord.Embed(colour=discord.Colour.from_rgb(50, 180, 250))\
            .set_author(name=man.display_name, icon_url=man.avatar_url)\
            .add_field(name="Yourself", value="{:,}{}".format(booty, emojis['booty']), inline=False)\
            .add_field(name="Vault", value="{:,}{}".format(vault, emojis['booty']), inline=False)\
            .add_field(name="Total", value="{:,}{}".format(booty + vault, emojis['booty']), inline=False)
        await ctx.send(embed=embed)

    @client.command(aliases=['lb'])
    async def leaderboard(ctx: commands.Context):
        brownieHub = await client.fetch_guild(621651744144752640)
        men = data['men'].copy()
        men.pop('default')
        menleaderboard = []
        for man in men:
            menleaderboard.append(((await brownieHub.fetch_member(int(man))).display_name,
                                   int(data['men'][man]['vault']) + int(data['men'][man]['booty'])))
        menleaderboard.sort(key=get_total, reverse=True)
        longestNetworthLen = 0
        for man in menleaderboard:
            networthLen = len(str(man[1]))
            if networthLen > longestNetworthLen:
                longestNetworthLen = networthLen

        menDisplay = ''
        for pos, man in enumerate(menleaderboard):
            menDisplay += "**{}.** {} - {}{}\n".format(str(pos), man[0], emojis['booty'], str(man[1]))
        embed = discord.Embed(description=menDisplay).set_author(name="Leaderboard", icon_url=bootyUrl)
        await ctx.send(embed=embed)

    @client.command(aliases=('rob', 'r'))
    async def raid(ctx: commands.Context, man):
        targetMan = ctx.guild.get_member_named(man)
        if not targetMan:
            try:
                targetMan = await ctx.guild.fetch_member(extract_id(man))
            except ValueError:
                # SYNTAXERROR
                return
        targetManId = str(targetMan.id)
        man = ctx.author
        manId = str(man.id)
        if targetManId == manId:
            await ctx.send("You can't rob yourself. " + emojis['pepega'])
            return
        manBooty = 0
        if manId in data['men']:
            manBooty = int(data['men'][manId]['booty'])
        if targetManId not in data['men']:
            await ctx.send("You can't raid someone who doesn't have anything.")
            return
        targetBooty = int(data['men'][targetManId]['booty'])
        if targetBooty <= 0:
            await ctx.send("{} doesn't have anything on him.".format(targetMan.display_name))
            return
        variance = float(data['settings']['raidPercentageVariance'])
        offset = float(data['settings']['raidPercentageOffset'])
        punishment = int(data['settings']['raidCaughtPunishment'])
        randomNum = random.random()
        percentageRaided = 1
        if randomNum < offset - variance / 2:
            percentageRaided = 0
        elif offset - variance / 2 <= randomNum < offset + variance / 2:
            percentageRaided = (math.sin(math.pi * (randomNum - offset) / variance) + 1) / 2
        if percentageRaided == 0:
            await set_stat(man, 'booty', manBooty - punishment, True)
            embed = discord.Embed(colour=discord.Colour.from_rgb(230, 69, 128)) \
                .add_field(name="You lost {:,}{}".format(punishment, emojis['booty']),
                           value="You were caught in {}'s trap.".format(targetMan.display_name))
        elif percentageRaided == 1:
            await set_stat(man, 'booty', manBooty + targetBooty, False)
            await set_stat(targetMan, 'booty', 0, True)
            embed = discord.Embed(colour=discord.Colour.from_rgb(72, 219, 156)) \
                .add_field(name="You raided {:,}{}".format(targetBooty, emojis['booty']),
                           value="You raided all of {}'s booty".format(targetMan.display_name))
        else:
            raidedBooty = math.ceil(percentageRaided * targetBooty)
            await set_stat(man, 'booty', manBooty + raidedBooty, False)
            await set_stat(targetMan, 'booty', targetBooty - raidedBooty, True)
            embed = discord.Embed(colour=discord.Colour.from_rgb(72, 219, 156)) \
                .add_field(name="You raided {:,}{}".format(raidedBooty, emojis['booty']),
                           value="{} has {:,}{} left on him."
                           .format(targetMan.display_name, targetBooty - raidedBooty, emojis['booty']))
        await ctx.send(embed=embed.set_footer(text="To: {}".format(man.display_name)))
        return

    @client.command(aliases=['bj'])
    async def blackjack(ctx: commands.Context, bet):
        nonlocal emojis
        man = ctx.author
        manId = str(man.id)
        if manId not in data['men']:
            await ctx.send("You don't even have anything.")
            return
        booty = int(data['men'][manId]['booty'])
        if bet in {'all', 'a'}:
            bet = booty
        elif bet in {'half', 'h'}:
            bet = booty // 2
        elif bet[-1] == "%":
            try:
                percentage = int(bet[:-1])
                if percentage <= 0 or percentage > 100:
                    await ctx.send("A percentage must be between 0 and 100.")
                    return
                bet = (booty * percentage) // 100
            except ValueError:
                await ctx.send("Not a integre percentage sonny.")
                return
        else:
            try:
                bet = int(bet)
            except ValueError:
                await ctx.send("Not an amount of {} sonny.".format(emojis['booty']))
                return
        if bet <= 0:
            await ctx.send("You can't bet {:,}{} fuckling.".format(bet, emojis['booty']))
            return
        if bet > booty:
            await ctx.send("That's more than you have.")
            return
        await set_stat(man, 'booty', booty - bet, False)

        manHand = [draw_blackjack_card(), draw_blackjack_card()]
        dealerHand = [draw_blackjack_card(), draw_blackjack_card()]
        messageContent = "Blackjack round with a bet of {:,}{}".format(bet, emojis['booty'])
        if blackjack_get_hand_value(manHand)[0] == 21:
            if blackjack_get_hand_value(dealerHand)[0] == 21:
                embed = generate_blackjack_embed("You broke even.", man, manHand,
                                                 dealerHand, "Push, {} back".format(emojis['booty']))
                await set_stat(man, 'booty', booty, True)
            else:
                embed = generate_blackjack_embed("You won {}{:,}.".format(emojis['booty'], bet), man, manHand,
                                                 dealerHand, "Win, {}{:,}.".format(emojis['booty'], bet))
                await set_stat(man, 'booty', booty + int(bet * 1.5), True)
            await ctx.send(messageContent, embed=embed)
            return
        embed = generate_blackjack_embed("sesy", man, manHand, [dealerHand[0]])

        message = await ctx.send(messageContent, embed=embed)
        blackjack_messages[message.id] = (man, manHand, dealerHand, bet)
        reactionEmojis = [emojis['hit'], emojis['stand'], emojis['surrender']]
        if blackjack_get_hand_value([manHand[0]])[0] == blackjack_get_hand_value([manHand[1]])[0]:
            reactionEmojis.append(emojis['split'])
        if 2 * bet <= booty:
            reactionEmojis.append(emojis['double down'])
        for emoji in reactionEmojis:
            await message.add_reaction(emoji)

        await asyncio.sleep(int(data['settings']['blackjackTimeout']))
        if message.id in blackjack_messages:
            blackjack_messages.pop(message.id)
            await ctx.send("Timeout bitch.")

    @client.event
    async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
        message = reaction.message
        if message.id in blackjack_messages:
            man, manHand, dealerHand, bet = blackjack_messages[message.id]
            if user.id != man.id:
                return
            emoji = reaction.emoji
            manBooty = int(data['men'][str(man.id)]['booty'])
            if emoji == emojis['hit']:
                blackjack_messages.pop(message.id)
                manHand.append(draw_blackjack_card())
                manHandValue = blackjack_get_hand_value(manHand)[0]
                if manHandValue > 21:
                    embed = generate_blackjack_embed("You lost {}{:,}.".format(emojis['booty'], bet), man, manHand,
                                                     [dealerHand[0]], "Bust, -{}{:,}.".format(emojis['booty'], bet))
                    await message.channel.send(embed=embed)
                    await export_data(data, syncChannel)
                    return
                elif blackjack_get_hand_value(manHand)[0] == 21:
                    dealerHandValue, dealerHandSoft = blackjack_get_hand_value(dealerHand)
                    while dealerHandValue < 17 or (dealerHandSoft and dealerHandValue != 21):
                        dealerHand.append(draw_blackjack_card())
                        dealerHandValue, dealerHandSoft = blackjack_get_hand_value(dealerHand)
                    if dealerHandValue > 21:
                        embed = generate_blackjack_embed("You won {}{:,}.".format(emojis['booty'], bet), man, manHand,
                                                         dealerHand, "Dealer Bust, {}{:,}.".format(emojis['booty'],
                                                                                                   bet))
                        await message.channel.send(embed=embed)
                        await set_stat(man, 'booty', manBooty + 2 * bet, True)
                        return
                    elif dealerHandValue > manHandValue:
                        embed = generate_blackjack_embed("You lost {}{:,}.".format(emojis['booty'], bet), man, manHand,
                                                         dealerHand, "Loss, -{}{:,}.".format(emojis['booty'], bet))
                        await message.channel.send(embed=embed)
                        await export_data(data, syncChannel)
                        return
                    elif dealerHandValue == manHandValue:
                        embed = generate_blackjack_embed("You broke even.", man, manHand,
                                                         dealerHand, "Push, {} back.".format(emojis['booty']))
                        await message.channel.send(embed=embed)
                        await set_stat(man, 'booty', manBooty + bet, True)
                        return
                    else:
                        embed = generate_blackjack_embed("You won {}{:,}.".format(emojis['booty'], bet), man, manHand,
                                                         dealerHand, "Win, {}{:,}.".format(emojis['booty'], bet))
                        await message.channel.send(embed=embed)
                        await set_stat(man, 'booty', manBooty + 2 * bet, True)
                        return
                embed = generate_blackjack_embed("sesy", man, manHand, [dealerHand[0]])
                message = await message.channel.send(embed=embed)
                blackjack_messages[message.id] = (man, manHand, dealerHand, bet)
                await message.add_reaction(emojis['hit'])
                await message.add_reaction(emojis['stand'])
                await asyncio.sleep(int(data['settings']['blackjackTimeout']))
                if message.id in blackjack_messages:
                    blackjack_messages.pop(message.id)
                    await message.channel.send("Timeout bitch.")

            elif emoji == emojis['stand']:
                blackjack_messages.pop(message.id)
                manHandValue = blackjack_get_hand_value(manHand)[0]
                dealerHandValue, dealerHandSoft = blackjack_get_hand_value(dealerHand)
                while dealerHandValue < 17 or (dealerHandSoft and dealerHandValue != 21):
                    dealerHand.append(draw_blackjack_card())
                    dealerHandValue, dealerHandSoft = blackjack_get_hand_value(dealerHand)
                if dealerHandValue > 21:
                    embed = generate_blackjack_embed("You won {}{:,}.".format(emojis['booty'], bet), man, manHand,
                                                     dealerHand, "Dealer Bust, {}{:,}.".format(emojis['booty'], bet))
                    await message.channel.send(embed=embed)
                    await set_stat(man, 'booty', manBooty + 2 * bet, True)
                    return
                elif dealerHandValue > manHandValue:
                    embed = generate_blackjack_embed("You lost {}{:,}.".format(emojis['booty'], bet), man, manHand,
                                                     dealerHand, "Loss, -{}{:,}.".format(emojis['booty'], bet))
                    await message.channel.send(embed=embed)
                    await export_data(data, syncChannel)
                    return
                elif dealerHandValue == manHandValue:
                    embed = generate_blackjack_embed("You broke even.", man, manHand,
                                                     dealerHand, "Push, {} back.".format(emojis['booty']))
                    await message.channel.send(embed=embed)
                    await set_stat(man, 'booty', manBooty + bet, True)
                    return
                else:
                    embed = generate_blackjack_embed("You won {}{:,}.".format(emojis['booty'], bet), man, manHand,
                                                     dealerHand, "Win, {}{:,}.".format(emojis['booty'], bet))
                    await message.channel.send(embed=embed)
                    await set_stat(man, 'booty', manBooty + 2 * bet, True)
                    return

            elif len(manHand) == 2:
                if emoji == emojis['surrender']:
                    blackjack_messages.pop(message.id)
                    bet //= 2
                    embed = generate_blackjack_embed("Got back {}{:,}.".format(emojis['booty'], bet), man, manHand,
                                                     [dealerHand[0]], "Surrender, {}{:,}.".format(emojis['booty'], bet))
                    await message.channel.send(embed=embed)
                    await set_stat(man, 'booty', manBooty + bet, True)

                elif manBooty > bet:
                    if emoji == emojis['double down']:
                        blackjack_messages.pop(message.id)
                        manHand.append(draw_blackjack_card())
                        manHandValue = blackjack_get_hand_value(manHand)[0]
                        if manHandValue > 21:
                            embed = generate_blackjack_embed("You lost {}{:,}.".format(emojis['booty'], bet), man,
                                                             manHand, [dealerHand[0]],
                                                             "Bust, -{}{:,}.".format(emojis['booty'], bet))
                            await message.channel.send(embed=embed)
                            await export_data(data, syncChannel)
                            return
                        dealerHandValue, dealerHandSoft = blackjack_get_hand_value(dealerHand)
                        while dealerHandValue < 17 or (dealerHandSoft and dealerHandValue != 21):
                            dealerHand.append(draw_blackjack_card())
                            dealerHandValue, dealerHandSoft = blackjack_get_hand_value(dealerHand)
                        if dealerHandValue > 21:
                            embed = generate_blackjack_embed("You won {}{:,}.".format(emojis['booty'], bet), man,
                                                             manHand, dealerHand,
                                                             "Dealer Bust, {}{:,}.".format(emojis['booty'], bet))
                            await message.channel.send(embed=embed)
                            await set_stat(man, 'booty', manBooty + 2 * bet, True)
                            return
                        elif dealerHandValue > manHandValue:
                            embed = generate_blackjack_embed("You lost {}{:,}.".format(emojis['booty'], bet), man,
                                                             manHand,
                                                             dealerHand, "Loss, -{}{:,}.".format(emojis['booty'], bet))
                            await message.channel.send(embed=embed)
                            await export_data(data, syncChannel)
                            return
                        elif dealerHandValue == manHandValue:
                            embed = generate_blackjack_embed("You broke even.", man, manHand,
                                                             dealerHand, "Push, {} back.".format(emojis['booty']))
                            await message.channel.send(embed=embed)
                            await set_stat(man, 'booty', manBooty + bet, True)
                            return
                        else:
                            embed = generate_blackjack_embed("You won {}{:,}.".format(emojis['booty'], bet), man,
                                                             manHand,
                                                             dealerHand, "Win, {}{:,}.".format(emojis['booty'], bet))
                            await message.channel.send(embed=embed)
                            await set_stat(man, 'booty', manBooty + 2 * bet, True)
                            return

                    elif emoji == emojis['split']\
                            and blackjack_get_hand_value([manHand[0]])[0] == blackjack_get_hand_value([manHand[1]])[0]:
                        blackjack_messages.pop(message.id)
                        await set_stat(man, 'booty', manBooty - bet, False)
                        manHand1 = [manHand[0], draw_blackjack_card()]
                        manHand2 = [manHand[0], draw_blackjack_card()]
                        for manHand in [manHand1, manHand2]:
                            pass

    @client.command(aliases=('setting', 'st'))
    async def settings(ctx: commands.Context, operation, setting, value=''):
        if not check_admin(ctx.author):
            return
        if (len(value) == 0 and operation not in {'remove', 'r'})\
                or operation not in {'add', 'edit', 'remove', 'a', 'e', 'r'}:
            # SYNTAXERROR
            return
        if operation in {'add', 'a'}:
            if setting in data['settings']:
                await ctx.send("Setting already exists, didn't change value.")
                return
            data['settings'][setting] = value
            await ctx.send("Added {} as {}.".format(setting, value))
        elif operation in {'edit', 'e'}:
            if setting not in data['settings']:
                await ctx.send("Setting doesn't exist.")
                return
            data['settings'][setting] = value
            await ctx.send("Edited {} as {}.".format(setting, value))
        else:
            if setting not in data['settings']:
                await ctx.send("Setting doesn't exist.")
                return
            data['settings'].pop(setting)
            await ctx.send("Removed {}.".format(setting))
        await export_data(data, syncChannel)

    @client.event
    async def on_ready():
        nonlocal data, syncChannel
        syncChannel = await client.fetch_channel(syncChannelId)
        data = await import_data(syncChannel)
        defaultValues = data['men']['default']
        # checking sure all the user follow the proper format
        for manId in data['men']:
            stats = data['men'][manId]
            for defaultStat in defaultValues:
                if defaultStat not in stats:
                    data['men'][manId][defaultStat] = defaultValues[defaultStat]
            uselessStats = []
            for stat in data['men'][manId]:
                if stat not in defaultValues:
                    uselessStats.append(stat)
            for uselessStat in uselessStats:
                data['men'][manId].pop(uselessStat)

        await client.change_presence(status=discord.Status.idle,
                                     activity=discord.Game("girls and drinking booze."))
        print("My back hurts.")

    client.run(grandfatherToken)


if __name__ == "__main__":
    main()
