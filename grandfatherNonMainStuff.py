from discord.ext import commands
from json import dumps, load
from random import shuffle
from aiofiles import open as aiopen
from io import StringIO
import traceback
import discord
import sys

class ReactiveBot(commands.Bot):
    async def process_commands(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)

    async def on_message_edit(self, _, message: discord.message.Message):
        await self.on_message(message)

    async def on_command_error(self, context, exception):
        if self.extra_events.get('on_command_error', None):
            return
        if hasattr(context.command, 'on_error'):
            return
        cog = context.cog
        if cog and cog.Cog._get_overridden_method(cog.cog_command_error) is not None:
            return
        if isinstance(exception, commands.errors.MissingRequiredArgument):
            await context.send("Wrong sonny.")
            return
        print("Ignoring exception in command {}:".format(context.command), file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

class Card:
    def __init__(self, value, suit: str = None):
        if not suit:
            value, suit = value[:-1], value[-1]
        self.value = value
        self.suit = suit
        self.string = ("%2s " % (value, )) + {
            'c': ":clubs:",
            'd': ":diamonds:",
            'h': ":hearts:",
            's': ":spades:"
        }[suit]

    def __str__(self):
        return self.string

def blackjack_get_hand_value(hand):
    soft = None
    value = 0
    for card in hand:
        if card.value == 'A':
            value += 1
            soft = True
        elif card.value in {'J', 'Q', 'K'}:
            value += 10
        else:
            value += int(card.value)
    if soft:
        if value > 11:
            soft = False
        else:
            value += 10
    return value, soft

def blackjack_get_hand_str_value(handValue):
    handVal, soft = handValue
    if soft:
        handType = "Soft "
    elif soft is None:
        handType = ''
    else:
        handType = "Soft "
    return handType + str(handVal)

def remove_start_space(text: str):
    count = 0
    while count < len(text):
        letter = text[count]
        if letter != ' ' and letter != '\n':
            break
        count += 1
    return text[count:]

def split_next_word(text: str):
    text = remove_start_space(text)
    count = 0
    while count < len(text):
        letter = text[count]
        if letter == ' ' or letter == '\n':
            break
        count += 1
    if count == len(text):
        return text, ''
    return text[:count], remove_start_space(text[count:])

def extract_id(idWord: str):
    start = 0
    end = len(idWord) - 1
    while start < len(idWord):
        if idWord[start].isdigit():
            break
        start += 1
    while end >= 0:
        if idWord[end].isdigit():
            break
        end -= 1
    return int(idWord[start:end + 1])

# For sorting for leaderboard
def get_total(manTuple): return manTuple[1]

# exports local data to discord message
async def export_data(data, syncChannel: discord.TextChannel):
    async with aiopen("grandfatherdata.json", 'w') as dataFile:
        await dataFile.write(dumps(data, indent=2))
    await syncChannel.send(file=discord.File(fp="grandfatherdata.json"))

# imports local data from discord message
async def import_data(syncChannel: discord.TextChannel):
    dataMessage = ''
    async for message in syncChannel.history(limit=1):
        dataMessage = message
    fileObject = dataMessage.attachments[0]
    await fileObject.save(fp="grandfatherdata.json")
    with open("grandfatherdata.json", 'r') as dataFile:
        dataContent = dataFile.read()
    return load(StringIO(dataContent))

def generate_blackjack_deck(numDecks: int):
    deck = []
    for suit in ['c', 'd', 'h', 's']:
        for value in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
            deck.append(value + suit)
    deck *= numDecks
    shuffle(deck)
    return deck
