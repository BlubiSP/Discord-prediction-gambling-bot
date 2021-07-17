#####################################
## Read the readme before anything##
#####################################
# Imports
import asyncio
import json
import os
import random
from datetime import datetime
import discord
from discord.ext import commands
from time import sleep

# Get your token here: https://discord.com/developers/applications
### Your bot token goes here. Don't forget the "" at the beginning and the end.
BOT_TOKEN = "Your token"
### Decides the prefix of the bot. Default is "!". So for example to type the help command you would type !help.
bot = commands.Bot(command_prefix='!')
### Bad words go in here. If users type these words in any message the message will be deleted and they lose 100 coins.
bad_words = ("example1", "example2")
### Slurs go in here. If users type these words in any message the message will be deleted and they lose all their coins.
slurs     = ("example1", "example2")
### If you have a meme channel type it here. Users who post links or files in this channel have a chance to get some coins.
meme_channelname = "channel_name"
### If set to true, there is no cooldown on games, which means you can farm an infinite amount of coins.
infinite_games = False

## Initializing variables

# Tells the bot if there is an active minigame.
active_minigame = False
# Tells the bot if there is an active prediction.
active_prediction = False
# Sets current_directory to the one this file is in.
current_directory = os.getcwd()

# Sets the location of the data.json file. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/data.json"
jsonfile = current_directory + '/data.json'
# Sets the location of the questions.txt file. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/questions.txt"
questions = current_directory + "/Game1/questions.txt"
# Sets the location of the Game2 folder. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/Game2"
game2images = os.listdir(current_directory + "/Game2")
# Sets the location of the nums folder. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/Game3/nums"
game3nums = os.listdir(current_directory + "/Game3/nums")
# Sets the location of the images folder. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/Game3/images"
game3images = os.listdir(current_directory + "/Game3/images")

## These functions are code which is used often inside other functions, so i don't have to write the same code multiple times.

# Loads coins from file.
def load_coins():
    global coinsd, data
    # reads data.json
    with open(jsonfile) as file:
            data = json.load(file)
            coinsd = data["coins"]

# Changes coins of a user.
def coinchange(user, amount):
    # Reloads coins from file.
    load_coins()
    # Can subtract aswell by simply making the amount negative.
    coinsd[user] = coinsd[user] + amount
    # Checks if the coins are below 0 after changing them.
    if coinsd[user] < 0:
    # If they are, this will set them to 0.
        coinsd[user] = 0
    # Saves coins to data.json
    with open(jsonfile, "w") as file:
        json.dump(data, file)

# Checks if the user is already signed up
def signed_up(author):
    # Reloads coins from file.
    load_coins()
    if author in coinsd:
        return True

# Checks if the user has enough coins
def enough_coins(author, amount):
    # Reloads coins from file.
    load_coins()
    if coinsd[author] >= int(amount):
        return True

# Loads the times users have last played a minigame
def check_times():
    global timesd
    # Reads data.json
    with open(jsonfile) as file:
        data = json.load(file)
        timesd = data["play_times"]

# Updates the users last played time.
def update_last_played(user):
    check_times()
    timesd[user] = str(datetime.now())
    data["play_times"] = timesd
    # Saves last played to data.json
    with open(jsonfile, "w") as file:
        json.dump(data, file)

# Checks if a user has already played a game in the last 24hrs or day.
def Already_played(author):
    # This method lets you play once a calender day
    check_times()
    # Gets current time as string.
    current_time = str(datetime.now())
    try:
    # Gets last played time as string.
        last_played = timesd[author]
    except KeyError:
    # Sets it to the year 2000 if user has never played.
        last_played = "2000-06-29 20:14:54.391623"
    # Checks year.
    if int(last_played[:4] )< int(current_time[:4]):
        return False
    # Checks month.
    if int(last_played[5:7]) < int(current_time[5:7]):
        return False
    # Checks day.
    if int(last_played[8:10]) < int(current_time[8:10]):
        return False
    return True
    # This method lets you play once every 24 hours
    """
    check_times()
    try:
        timeobj = datetime.strptime(timesd[author],"%Y-%m-%d %H:%M:%S.%f")
    except KeyError:
        timeobj = datetime.strptime("2000-06-29 20:14:54.391623","%Y-%m-%d %H:%M:%S.%f")
    if (((datetime.now() - timeobj).total_seconds() / 60) / 60) < 24:
        return False
    return True
    """

# loads any open prediction from data.json
def load_prediction():
    global data, sum_of_bets_per_option, both, total, active_prediction, closed_prediction, options, prediction_starter, prediction_name
    with open(jsonfile) as file:
            data = json.load(file)
            sum_of_bets_per_option = data["prediction"]["sum_of_bets_per_option"]
            both = data["prediction"]["both"]
            total = data["prediction"]["total"]
            active_prediction = data["prediction"]["status"]["active_prediction"]
            closed_prediction = data["prediction"]["status"]["closed_prediction"]
            options = data["prediction"]["options"]
            prediction_starter = data["prediction"]["prediction_starter"]
            prediction_name = data["prediction"]["prediction_name"]

# saves a open prediction to data.json.
# This makes predictions persist even if the bot goes offline
# if statements basically checks if there is prediction active
def save_prediction():
    with open(jsonfile, "w") as file:
        if sum_of_bets_per_option:
            data["prediction"]["sum_of_bets_per_option"] = sum_of_bets_per_option
        if both:
            data["prediction"]["both"] = both
        if total:
            data["prediction"]["total"] = total
        if active_prediction :
            data["prediction"]["status"]["active_prediction"] = active_prediction
        if closed_prediction :
            data["prediction"]["status"]["closed_prediction"] = closed_prediction
        if options:
            data["prediction"]["options"] = options
        if prediction_starter:
            data["prediction"]["prediction_starter"] = prediction_starter
        if prediction_name:
            data["prediction"]["prediction_name"] = prediction_name
        json.dump(data, file)

# resets prediction and all variables
def reset_prediction():
    global data, sum_of_bets_per_option, both, total, active_prediction, closed_prediction
# Loads a active prediction from data.json, if there is one.
    load_prediction()
    both = {}
    sum_of_bets_per_option = {}
    active_prediction = False
    closed_prediction = False
    total = 0
    options = []
    prediction_starter = ""
    with open(jsonfile, "w") as file:
        data["prediction"]["sum_of_bets_per_option"] = sum_of_bets_per_option
        data["prediction"]["both"] = both
        data["prediction"]["total"] = total
        data["prediction"]["status"]["active_prediction"] = active_prediction
        data["prediction"]["status"]["closed_prediction"] = closed_prediction
        data["prediction"]["options"] = options
        data["prediction"]["prediction_starter"] = prediction_starter
        json.dump(data, file)



## Bot commands

@bot.command(brief= "Registers you and gives you 500 coins to start.")
async def signup(ctx):
    author = ctx.message.author.mention
    global coinsd
    # Checks if the author of the command is signed up and refreshes coins from data.json.
    if signed_up(author):
        await ctx.send("You already signed up, you have %s coins" %coinsd[author])
        return
    # Creates dictionary entry with userid as key and the amount of coins as value.
    coinsd[author] = 500
    with open(jsonfile, "w") as file:
        # Saves it to data.json.
        json.dump(data, file)
    await ctx.send('%s is now signed up and has %d coins ' % (str(author), coinsd[author]))

@bot.command(brief = "Shows how many coins you have.")
async def coins(ctx):
    author = ctx.message.author.mention
    # Checks if the author of the command is signed up and refreshes coins from data.json.
    if not signed_up(author):
        await ctx.send("You are not signed up! Sign up with !signup")
        return
    # Grammar correction: when you only have 1 coin it says "1 coin" instead of "1 coins".
    if coinsd[author] == 1:
        await ctx.send(f"You have {coinsd[author]} coin!")
        return
    await ctx.send(f"You have {coinsd[author]} coins!")

@bot.command(brief= "Give coins to someone. !givecoins <@user> <amount>")
async def givecoins(ctx, receiver, amount):
    # Lazy way to catch wrong inputs and send "Wrong input"
    try:
        author = ctx.message.author.mention
        # Checks if Author has enough coins.
        if not enough_coins(author, int(amount)):
            await ctx.send("You don't have enough coins.")
            return
    except ValueError:
        await ctx.send("Wrong input")
        return
    amount = int(amount)
    # Checks if the author of the command is signed up and refreshes coins from file.
    if not signed_up(author):
        await ctx.send("Sign up first!")
        return
    # Checks if the receiver is signed up.
    if receiver not in coinsd:
        await ctx.send("User has not signed up yet!")
        return
    # Adds/Removes Coins to/from author.
    coinchange(author, -amount)
    # Gives coins to receiver.
    coinchange(receiver, amount)
    # Grammar correction: when you only have 1 coin it says "1 coin" instead of "1 coins".
    if amount == 1:
        await ctx.send(f"{author} has given {amount} coin to {receiver}!")
        return
    await ctx.send(f"{author} has given {amount} coins to {receiver}!")


# Simple Trivia game. You can add your own Questions in the questions.txt file
@bot.command(brief="Easy difficulty, you can play one game a day.")
async def game1(ctx):
    author = ctx.message.author.mention
    global active_minigame
    # Checks if the author of the command is signed up and refreshes coins from file.
    if not signed_up(author):
        await ctx.send("You are not signed up! Type !signup to start playing!")
        return
    # Checks if user has played a game recently.
    if Already_played(author) and not infinite_games:
        await ctx.send(f"You already played today.")
        return
    else:
        update_last_played(author)
    if active_minigame:
        await ctx.send('Game already started, you can stop it with !stop')
        return
    # Makes sure the bot only accepts answers from the user that started it.
    def check(m):
        return ctx.author == m.author
    gstart = await ctx.send('Game starting in 5 seconds. You have 10 seconds to solve the game')
    # Opens questions.txt
    with open(questions, "r", encoding="utf8") as file:
        # Saves lines in a list.
        lines = file.readlines()
    question_and_answers = {}
    curq = None
    # Itterates over each line.
    for l in lines:
        if l.startswith("Q: ") and curq == None:
            # Temporarily saves questions.
            curq = l[3:].strip()
        # If there is a question temporarily saved.
        if l.startswith("A: ") and curq != None:
            # Adds saved question as key to dictionary with the answer as value.
            question_and_answers[curq] = l[3:].strip()
            # Clears temporary save to get next question.
            curq = None
    active_minigame = True
    await asyncio.sleep(5)
    await gstart.delete()
    # Selects random question.
    q = random.choice(list(question_and_answers.keys()))
    a = question_and_answers[q]
    # Continues only if game was not stopped.
    if active_minigame == True:
        # Sends question.
        await ctx.send(q)
        try:
            # Listens for the next message of the author for 10 seconds.
            msg = await bot.wait_for('message', timeout=10.0, check=check)
            # If the next message(lowercase) is the same as the answer(lowercase) you win.
            if msg.content.lower() == a.lower():
                await ctx.send("Correct! You won 50 Coins!")
                # Adds/Removes Coins to/from author.
                coinchange(author, 50)
                active_minigame = False
            else:
                # Continues only if game was not stopped.
                if active_minigame == True:
                    await ctx.send("Wrong")
                active_minigame = False
        # Sends a message if you time out.
        except asyncio.TimeoutError:
            # Continues only if game was not stopped.
            if active_minigame == True:
                await ctx.send("Too slow!")
            active_minigame = False

# You have 2 seconds to remember 8 digits. Seems hard at first but gets easier the more you try it.
@bot.command(brief="Medium difficulty, you can play one game a day.")
async def game2(ctx):
    author = ctx.message.author.mention
    global active_minigame
    # Checks if the author of the command is signed up and refreshes coins from file.
    if not signed_up(author):
        await ctx.send("You are not signed up! Type !signup to start playing!")
        return
    # Checks if user has played a game recently.
    if Already_played(author) and not infinite_games:
        await ctx.send(f"You already played today.")
        return
    else:
        update_last_played(author)
    if active_minigame:
        await ctx.send('Game already started, you can stop it with !stop')
        return
    # Makes sure the bot only accepts answers from the user that started it.
    def check(m):
        return ctx.author == m.author
    gstart = await ctx.send('Game starting in 3 seconds. You have 10 seconds to solve the game')
    active_minigame = True
    await asyncio.sleep(3)
    # Selects random image.
    q = "/" + random.choice(game2images)
    # Gets anwer from filename.
    a = q[:q.find(".png")]
    # Continues only if game was not stopped.
    if active_minigame == True:
        await gstart.delete()
        rem = await ctx.send("Remember the number")
        await asyncio.sleep(1)
        await rem.delete()
        # Posts image of numbers.
        id = await ctx.send(file=discord.File(current_directory + "/Game2/" + q))
        # Deletes it after 2 seconds.
        await asyncio.sleep(2)
        await id.delete()
        ent = await ctx.send("Enter the number:")
        try:
            # Listens for the next message of the author for 10 seconds.
            msg = await bot.wait_for('message', timeout=10.0, check=check)
            # If the next message is the same as the answer you win.
            if msg.content == a:
                await ctx.send("Correct! You won 150 Coins!")
                # Adds/Removes Coins to/from author.
                coinchange(author, 150)
                active_minigame = False
                await ent.delete()
            else:
                # Continues only if game was not stopped.
                if active_minigame == True:
                    await ent.delete()
                    await ctx.send("Wrong")
                active_minigame = False
        # Sends a message if you time out.
        except asyncio.TimeoutError:
            # Continues only if game was not stopped.
            if active_minigame == True:
                await ent.delete()
                await ctx.send("Too slow!")
            active_minigame = False

# Shitty version of the Fleeca minigame from NoPixel
# You can try the real game here: https://sharkiller.ddns.net/nopixel_minigame/fleeca/
@bot.command(brief="Hard difficulty, you can play one game a day. Type !help for more info", description="Fleeca minigame from NoPixel. You can practice here: https://sharkiller.ddns.net/nopixel_minigame/fleeca/")
async def game3(ctx):
    author = ctx.message.author.mention
    global active_minigame
    # Checks if the author of the command is signed up and refreshes coins from file.
    if not signed_up(author):
        await ctx.send("You are not signed up! Type !signup to start playing!")
        return
    # Checks if user has played a game recently.
    if Already_played(author) and not infinite_games:
        await ctx.send(f"You already played today.")
        return
    update_last_played(author)
    if active_minigame:
        await ctx.send('Game already started, you can stop it with !stop')
        return
    # Makes sure the bot only accepts answers from the user that started it.
    def check(m):
        return ctx.author == m.author
    gstart = await ctx.send('Game starting in 3 seconds.')
    active_minigame = True
    await asyncio.sleep(3)
    # Picks random picture from nums.
    q1 = random.choice(game3nums)
    a1 = str(q1[:q1.find(".JPG")]).strip()
    # Picks random picture from images.
    q2 = random.choice(game3images)
    a2 = str(q2[:q2.find(".JPG")]).strip()
    # For error handling if answer2 is none
    answer2 = "1234567890asdfghjkl"
    # You have to write out every possible solution with the correct answer, so it's alot of work to add more variety.
    # It's sometimes hard to see the difference between red and purple or white and yellow, so i added both as correct answers.
    if a1 == "2314":
        if a2 == "1":
            answer = "purple yellow"
            answer2 = "red yellow"
        elif a2 == "2":
            answer = "blue blue"
        elif a2 == "3":
            answer = "yellow rectangle"
            answer2 = "white rectangle"
        elif a2 == "4":
            answer = "square white"
        elif a2 == "5":
            answer = "circle blue"
    elif a1 == "4213":
        if a2 == "1":
            answer = "red purple"
            answer2 = "purple purple"
        elif a2 == "2":
            answer = "purple green"
            answer2 = "purple blue"
        elif a2 == "3":
            answer = "white triangle"
        elif a2 == "4":
            answer = "square black"
        elif a2 == "5":
            answer = "triangle blue"
    # Continues only if game was not stopped.
    if active_minigame == True:
        await gstart.delete()
        first_image = await ctx.send(file=discord.File(current_directory + "/Game3/nums/" + q1))
        # Shows inital numbers for 3 seconds.
        await asyncio.sleep(3)
        await first_image.delete()
        second_image = await ctx.send(file=discord.File(current_directory +  "/Game3/images/" + q2))
        try:
            # Listens for the next message of the author for 8 seconds.
            msg = await bot.wait_for('message', timeout=8.0, check=check)
            # If the next message(lowercase) is the same as the answer(lowercase) you win.
            if msg.content.lower() == answer or msg.content.lower() == answer2:
                await ctx.send("Correct! You won 300 Coins!")
                # Adds/Removes Coins to/from author.
                coinchange(author, 300)
                active_minigame = False
                await second_image.delete()
            else:
                # Continues only if game was not stopped.
                if active_minigame == True:
                    await second_image.delete()
                    await ctx.send("Wrong")
                    active_minigame = False
        # Sends a message if you time out.
        except asyncio.TimeoutError:
            # Continues only if game was not stopped.
            if active_minigame == True:
                await second_image.delete()
                await ctx.send("Too slow!")
            active_minigame = False

@bot.command(brief= "Stops an active Minigame.")
async def stop(ctx):
    global active_minigame, question_and_answers
    if active_minigame:
        await ctx.send('Game stopping.')
        active_minigame = False
    else:
        await ctx.send('No game active_minigame, start one with !game')


@bot.command(brief='Starts a prediction,!prediction <name of prediction>')
async def prediction(ctx, *name):
    global options, prediction_starter, active_prediction, closed_prediction, prediction_name
    # Loads a active prediction from data.json, if there is one.
    load_prediction()
    if active_prediction:
        await ctx.send("There is already a Prediction active.")
        return
    # Checks if the user typed the prediction name after !prediction.
    if len(ctx.message.content.split()) < 2:
        await ctx.send("Enter the name of the Prediction after !prediction\n**Prediction not started!**")
        reset_prediction()
        return
    # Makes sure the bot only accepts answers from the user that started it.
    def check(m):
        return ctx.author == m.author
    await ctx.send("Enter bet Option seperated by ,\nExample: First, Second, Third")
    msg = await bot.wait_for('message', check=check, timeout=60.0)
    # Puts all options into a list seperated by ",".
    options = msg.content.split(",")
    # Removes whitespaces at start/end points for each option.
    options = [i.strip() for i in options]
    # Checks if atleast 2 options were given.
    if len(options) < 2:
        await ctx.send("Need atleast 2 options\n**Prediction not started!**")
        reset_prediction()
        return
    prediction_starter = ctx.message.author.mention
    prediction_name = " ".join(name)
    await ctx.send(f"@everyone\n{prediction_starter} has started a Prediction!\nYou can bet using\n!bet (number of the choice you want to pick) (amount of coins you want to bet)\nWithout the ( )\n**{prediction_name}**\nOptions:")
    active_prediction = True
    closed_prediction = False
    save_prediction()
    # Sends the given options back in one list for better viewability.
    for n, i in enumerate(options):
        await ctx.send(f"**{n+1}**. {i}")

@bot.command(brief= "Lets you bet on an active prediction.")
async def bet(ctx, choice, amount):
    author = ctx.message.author.mention
    global both, total
    # Loads a active prediction from data.json, if there is one.
    load_prediction()
    if active_prediction == False:
        await ctx.send(f"No Prediction active. Start one with !prediction")
        return
    if closed_prediction == True:
        await ctx.send(f"Bets are closed!")
        return
    choicenr = int(choice)
    try:
        # If users choose a number higher then the available options, they get an error message.
        if choicenr > len(options):
            await ctx.send(f"You chose number {choicenr} but there is only {len(options)} options.")
            return
    except ValueError:
        await ctx.send('Wrong format use !bet "number of choice" "coin amount"')
        return
    bet = int(amount)
    # Checks if the user has enough coins.
    if not enough_coins(author, bet):
        await ctx.send("You don't have enough coins.")
        return
    choice = options[choicenr- 1]
    # If user already has an active bet.
    if author in both:
        # Refund coins.
        coinchange(author, both[author][0])
    # Adds dictionary entry with user id as key and bet amount and choice(in a list) as value.
    both[author] = [bet,choice]
    # Adds/Removes Coins to/from author.
    coinchange(author, -bet)
    await ctx.send(f"{author} bet {bet} coins on {choice}\n")
    # Sends the given options back in one list for better viewability.
    for n, i in enumerate(options):
        coins_on_i = 0
        # Itterates over a list wich has the amount of what a user bet(index 0) and the name of the option(index 1).
        for bet, choice in both.values():
            # If the name of what a user bet on matches the name of an option.
            if choice == i:
                coins_on_i += int(bet)
        sum_of_bets_per_option[i] = coins_on_i# I do it this way instead of writing directly to the dictionary to avoid KeyErrors when there is no value set to an option.
        await ctx.send(f"**{n+1} {i}**\nTotal: {sum_of_bets_per_option[i]}")
    save_prediction()

@bot.command(brief = "Closes an open prediction. Meaning no more bets allowed.")
async def close(ctx):
    global closed_prediction, active_prediction, total
    # Loads a active prediction from data.json, if there is one.
    load_prediction()
    if active_prediction == False:
        await ctx.send("No Prediction active")
        return
    if prediction_starter != ctx.message.author.mention:
        await ctx.send("Only the person that started the Prediction can close it!")
        return
    if closed_prediction:
        await ctx.send("Prediction is already closed!")
        return
    # Gets total by summing up all bets.
    total = sum([int(f) for f in sum_of_bets_per_option.values()])
    closed_prediction = True
    await ctx.send("Bets are now closed!")
    save_prediction()

@bot.command(brief="Shows current prediction and bets")
async def active(ctx):
    load_prediction()
    if active_prediction or closed_prediction:
        await ctx.send(f"Current Prediction : {prediction_name}\n")
        for n, i in enumerate(options):
            await ctx.send(f"**{n+1} {i}**\nTotal: {sum_of_bets_per_option[i]}")
        return
    await ctx.send("No active prediction.")

@bot.command(brief="Lets the person who started the Prediction decide the winner.")
async def winner(ctx, winner):
    global active_prediction
    # Loads a active prediction from data.json, if there is one.
    load_prediction()
    if active_prediction == False:
        await ctx.send("No Prediction active")
        return
    if closed_prediction == False:
        await ctx.send("Prediction is not closed")
        return
    if prediction_starter != ctx.message.author.mention:
        await ctx.send("Only the person that started the Prediction can decide the winner!")
        return
    # decides winner from input. -1 is to correct for the index starting at 0.
    winner = options[int(winner)- 1]
    if winner not in options:
        await ctx.send(f"{winner} was not an Option.\n Available Options:")
        # Sends the given options back in one list for better viewability.
        for n, i in enumerate(options):
            await ctx.send(f"**{n+1}**. {i}")
        return
    # Itterates over options to find winner.
    for i in options:
        if i == winner:
            await ctx.send(f"The result is {winner}")
            # k = discord user v = list[(index 0 = bet amount), (index 1 = choice)].
            for k, v in both.items():
                # If user chose the winning option.
                if v[1] == winner:
                    # Formula to calculate winnings broken down into steps
                    # Step 1: bet amount /  (total bets on that option / 100) = percentage of how much the user bet was compared to all bets on that option
                    # Step 2: result from step 1 / 100 = the multiplier for the percentage
                    # Step 3: result from step 2 * total = payout

                    ## Example bet
                    # user 1 bets 75 on option 1
                    # user 2 bets 25 on option 1
                    # user 3 bets 100 in option 2
                    # option 1 wins

                    # calculation for user1:
                    # 75 / ((75+25) / 100) = 75
                    # 75 / 100 = 0.75
                    # 0.75 * 200 = 150
                    # payout is 150

                    # calculation for user2:
                    # 25 / ((75+25) / 100) = 25
                    # 25 / 100 = 0.25
                    # 0.25 * 200 = 50
                    # payout is 50

                    # calculation for user3:
                    # payout is 0 because they lost
                    winnings = int(round((both[k][0]) / (sum_of_bets_per_option[winner] / 100)) / 100 * int(total))
                    coinchange(k, winnings)
                    await ctx.send(f"{k} won and got {winnings} coins")
                    active_prediction = False
    reset_prediction()


@bot.command(brief='Pay to roll 2 6-sided die, choose "seven", "high" or "low"', description= "Costs 50 coins to roll. If you choose high/low correctly you win 100 coins. If you choose seven correctly you win 250 coins.")
async def roll(ctx, choice):
    author = ctx.message.author.mention
    # Checks if user has enough coins.
    if not enough_coins(author, 50):
        await ctx.send("You don't have enough coins.")
        return
    # Rolls dice 1.
    rand1 = random.randint(1, 6)
    # Rolls dice 2.
    rand2 = random.randint(1, 6)
    result = rand1 + rand2# Adds them together.
    # Dictionary to convert numbers to emojis.
    emoji = {1:"1️⃣",2:"2️⃣",3:"3️⃣",4:"4️⃣",5:"5️⃣",6:"6️⃣"}
    # Reloads coins from file.
    load_coins()
    # Adds/Removes Coins to/from author.
    coinchange(author, -50)
    await ctx.send(f"{emoji[rand1]}  {emoji[rand2]}")
    if result == 7 and choice == "seven":
        await ctx.send("**You win 250 Coins!**")
        # Adds/Removes Coins to/from author.
        coinchange(author, 250)
    elif result <= 6 and choice == "low":
        await ctx.send("**You win 100 Coins!**")
        # Adds/Removes Coins to/from author.
        coinchange(author, 100)
    elif result >=8 and choice == "high":
        await ctx.send("**You win 100 Coins!**")
        # Adds/Removes Coins to/from author.
        coinchange(author, 100)
    else:
        await ctx.send("You lost :(")


# on_message triggers on every message.
@bot.event
async def on_message(message):
    author = message.author.mention
    # Returns if the message is from the bot.
    if message.author == bot.user:
        return
    # Checks if any word in the message matches a word on the bad_word list.
    if any(bad_word in message.content.lower().split() for bad_word in bad_words):
        # Deletes message.
        await message.delete()
        await message.channel.send("You can't say that!\n**-100 Coins**")
        # Adds/Removes Coins to/from author.
        coinchange(author, -100)
    # Checks if any word in the message matches a word on the slurs list.
    if any(bad_word in message.content.lower().split() for bad_word in slurs):
        # Deletes message.
        await message.delete()
        await message.channel.send("That word is banned!\n**You lost all your coins!**")
        # Adds/Removes Coins to/from author.
        coinchange(author, -coinsd[author])
    # If message is sent in meme channel.
    if str(message.channel) == meme_channelname:
        # Checks if message has http in it(this can be abused) or is a file.
        if "http" in message.content or message.attachments:
            # Gets random number between 1-100.
            random_number = random.randint(1, 100)
            # If number is lower then 10 (9% chance).
            if random_number < 10:
                await message.channel.send(f"{author} Nice meme!\n**+50 coins!**")
                # Adds/Removes Coins to/from author.
                coinchange(author, 50)
    # Tells the bot to still listen to commands.
    await bot.process_commands(message)

if BOT_TOKEN == "Your token":
    print("You forgot to add your token. Make sure you read the README.md!")
    print("Closing in 10 Seconds")
    sleep(10)
    exit()

# Starts the bot
bot.run(BOT_TOKEN)
