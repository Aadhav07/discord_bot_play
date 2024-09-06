import discord
import requests
import logging
import os
import random


logging.basicConfig(level=logging.ERROR)
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await handle_hello(message)
    elif message.content.startswith("$bye") or message.content.startswith("$goodbye"):
        await handle_goodbye(message)
    elif message.content.startswith("$help"):
        await handle_help(message)
    elif message.content.startswith("$poem"):
        await handle_poem(message)
    elif message.content.lower().startswith("$afl"):
        await handle_afl(message)
    elif message.content.startswith("$dice"):
        await handle_dice(message)


async def handle_hello(message):
    await message.channel.send("Hello Legend!")


async def handle_goodbye(message):
    await message.channel.send("Goodbye Legend!")


async def handle_help(message):
    help_message = "Available commands: $hello, $goodbye, $help, $poem, $afl"
    await message.channel.send(help_message)


async def handle_poem(message):
    try:
        response = requests.get("https://poetrydb.org/random")
        response.raise_for_status()
        poem = response.json()[0]
        title = poem["title"]
        author = poem["author"]
        lines = poem["lines"]
        await message.channel.send(f"**{title}** by *{author}*")
        for line in lines[:20]:
            if len(line) > 0:
                await message.channel.send(line)
            else:
                await message.channel.send("...")
        if len(lines) > 20:
            await message.channel.send("... (truncated)")
    except Exception as e:
        logging.error(f"Error fetching poem: {e}")
        await message.channel.send("Sorry, I could not fetch a poem at this time.")


async def handle_afl(message):
    try:
        response = requests.get(
            "https://api.squiggle.com.au/?q=games;year=2023;round=1"
        )
        response.raise_for_status()
        games = response.json()["games"]
        live_games = [game for game in games if game["is_live"]]
        if not live_games:
            await message.channel.send("No live AFL games at the moment.")
            return
        for game in live_games:
            home_team = game["hteam"]
            away_team = game["ateam"]
            home_score = game["hscore"]
            away_score = game["ascore"]
            last_update = game["updated"]
            await message.channel.send(
                f"{home_team} {home_score} - {away_team} {away_score} (Last updated: {last_update})"
            )
    except Exception as e:
        logging.error(f"Error fetching AFL scores: {e}")
        await message.channel.send(
            "Sorry, I could not fetch the AFL scores at this time."
        )


async def handle_dice(message):
    try:
        dice = message.content.split(" ")[1:]
        if not dice:
            num_dice = 1
            num_sides = 6
        else:
            num_dice = int(dice[0])
            if len(dice) == 1:
                num_sides = 6
            else:
                num_sides = int(dice[1])
    except ValueError:
        await message.channel.send("Unsure of how many dice or sides you want. Defaulting to 1d6.")
        num_dice = 1
        num_sides = 6

    try:
        if num_dice > 100 or num_sides > 100:
            await message.channel.send(
                "Please keep the number of dice and sides on each die less than 100."
            )
            return
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total = sum(rolls)
        if num_dice == 1:
            await message.channel.send(f"Roll: {rolls[0]}")
        else:
            await message.channel.send(f"Rolls: {rolls}\nTotal: {total}")
    except Exception as e:
        logging.error(f"Error rolling dice: {e}")
        await message.channel.send("Sorry, I could not roll the dice at this time.")


# Retrieve the token from the environment variable
token = os.getenv("DISCORD_BOT_TOKEN")
if token is None:
    raise ValueError("No Discord bot token found in environment variables")

client.run(token)
