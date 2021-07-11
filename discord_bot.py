#####################################
## Read the readme before anything ##
#####################################
# Imports
import asyncio
from discord.ext import commands
import os
import random
import discord
from datetime import datetime
import json

# Get your token here: https://discord.com/developers/applications
BOT_TOKEN = "Your token"                                                ### Your bot token goes here. Don't forget the "" at the beginning and the end.
bot = commands.Bot(command_prefix='!')                                  ### Decides the prefix of the bot. Default is "!". So for example to type the help command you would type !help.
bad_words = ("example1", "example2")                                    ### Bad words go in here. If users type these words in any message the message will be deleted and they lose 100 coins.
slurs     = ("example1", "example2")                                    ### Slurs go in here. If users type these words in any message the message will be deleted and they lose all their coins.
meme_channelname = "channel_name"                                       ### If you have a meme channel type it here. Users who post links or files in this channel have a chance to get some coins.
infinite_games = False                                                  ### If set to true, there is no cooldown on games, which means you can farm an infinite amount of coins.

# Initializing variables
active_minigame = False                                                                                     # Tells the bot if there is an active minigame.
active_prediction = False                                                                                   # Tells the bot if there is an active prediction.
current_directory = os.getcwd()                                                                             # Sets current_directory to the one this file is in.

jsonfile = current_directory + '/data.json'                                                                 # Sets the location of the data.json file. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/data.json"
questions = current_directory + "/Game1/questions.txt"                                                      # Sets the location of the questions.txt file. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/questions.txt"
game2images = os.listdir(current_directory + "/Game2")                                                      # Sets the location of the Game2 folder. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/Game2"
game3nums = os.listdir(current_directory + "/Game3/nums")                                                   # Sets the location of the nums folder. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/Game3/nums"
game3images = os.listdir(current_directory + "/Game3/images")                                               # Sets the location of the images folder. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/Game3/images"

## These functions are code which is used often inside other functions, so i don't have to write the same code multiple times.
# Loads coins from file.
def load_coins():                                                                                           # Reloads coins from file.
    global coinsd, data
    with open(jsonfile) as file:                                                                            # reads data.json
            data = json.load(file)
            coinsd = data["coins"]

# Changes coins of a user.
def coinchange(user, amount):
    load_coins()                                                                                            # Reloads coins from file.                            
    coinsd[user] = coinsd[user] + amount                                                                    # Can subtract aswell by simply making the amount negative.
    if coinsd[user] < 0:                                                                                    # Checks if the coins are below 0 after changing them.
        coinsd[user] = 0                                                                                    # If they are, this will set them to 0.
    with open(jsonfile, "w") as file:                                                                       # Saves coins to data.json
        json.dump(data, file)

# Checks if the user is already signed up
def signed_up(author):                                                                                      # Checks if the author of the command is signed up and refreshes coins from file.  
    load_coins()                                                                                            # Reloads coins from file.
    if author in coinsd:
        return True

# Checks if the user has enough coins
def enough_coins(author, amount):
    load_coins()                                                                                            # Reloads coins from file.
    if coinsd[author] >= int(amount):
        return True

# Loads the times users have last played a minigame
def check_times():
    global timesd
    with open(jsonfile) as file:                                                                            # Reads data.json
        data = json.load(file)
        timesd = data["play_times"]

# Updates the users last played time.
def update_last_played(user):
    check_times()
    timesd[user] = str(datetime.now())
    data["play_times"] = timesd
    with open(jsonfile, "w") as file:                                                                       # Saves last played to data.json
        json.dump(data, file)

# Checks if a user has already played a game in the last 24hrs or day.
def Already_played(author):                                                                                 # Checks if user has played a game recently.
    # This method lets you play once a calender day
    check_times()
    current_time = str(datetime.now())                                                                      # Gets current time as string.
    try:
        last_played = timesd[author]                                                                        # Gets last played time as string.
    except KeyError:
        last_played = "2000-06-29 20:14:54.391623"                                                          # Sets it to the year 2000 if user has never played.
    if int(last_played[:4] )< int(current_time[:4]):                                                        # Checks year.
        return False
    if int(last_played[5:7]) < int(current_time[5:7]):                                                      # Checks month.
        return False
    if int(last_played[8:10]) < int(current_time[8:10]):                                                    # Checks day.
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
def load_prediction():                                                                                      # Loads a active prediction from data.json, if there is one.
    global data, sum_of_bets_per_option, both, total, active_prediction, closed_prediction, options, prediction_starter
    with open(jsonfile) as file:
            data = json.load(file)
            sum_of_bets_per_option = data["prediction"]["sum_of_bets_per_option"]
            both = data["prediction"]["both"]
            total = data["prediction"]["total"]
            active_prediction = data["prediction"]["status"]["active_prediction"]
            closed_prediction = data["prediction"]["status"]["closed_prediction"] 
            options = data["prediction"]["options"]
            prediction_starter = data["prediction"]["prediction_starter"]

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
        json.dump(data, file)

# resets prediction and all variables
def reset_prediction():
    global data, sum_of_bets_per_option, both, total, active_prediction, closed_prediction
    load_prediction()                                                                                       # Loads a active prediction from data.json, if there is one.
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
    if signed_up(author):                                                                                   # Checks if the author of the command is signed up and refreshes coins from data.json.
        await ctx.send("You already signed up, you have %s coins" %coinsd[author])  
        return  
    coinsd[author] = 500                                                                                    # Creates dictionary entry with userid as key and the amount of coins as value.
    with open(jsonfile, "w") as file:
        json.dump(data, file)                                                                               # Saves it to data.json.
    await ctx.send('%s is now signed up and has %d coins ' % (str(author), coinsd[author]))

@bot.command(brief = "Shows how many coins you have.")
async def coins(ctx):
    author = ctx.message.author.mention
    if not signed_up(author):                                                                               # Checks if the author of the command is signed up and refreshes coins from data.json.
        await ctx.send("You are not signed up! Sign up with !signup")
        return
    if coinsd[author] == 1:                                                                                 # Grammar correction: when you only have 1 coin it says "1 coin" instead of "1 coins".
        await ctx.send(f"You have {coinsd[author]} coin!")
        return
    await ctx.send(f"You have {coinsd[author]} coins!")
          
@bot.command(brief= "Give coins to someone. !givecoins <@user> <amount>")
async def givecoins(ctx, receiver, amount):
    try:                                                                                                    # Lazy way to catch wrong inputs and send "Wrong input"
        author = ctx.message.author.mention
        if not enough_coins(author, int(amount)):                                                           # Checks if Author has enough coins.
            await ctx.send("You don't have enough coins.")
            return
    except ValueError:
        await ctx.send("Wrong input")
        return
    amount = int(amount)
    if not signed_up(author):                                                                               # Checks if the author of the command is signed up and refreshes coins from file.
        await ctx.send("Sign up first!")
        return
    if receiver not in coinsd:                                                                              # Checks if the receiver is signed up.
        await ctx.send("User has not signed up yet!")
        return
    coinchange(author, -amount)                                                                             # Adds/Removes Coins to/from author.
    coinchange(receiver, amount)                                                                            # Gives coins to receiver.
    if amount == 1:                                                                                         # Grammar correction: when you only have 1 coin it says "1 coin" instead of "1 coins".
        await ctx.send(f"{author} has given {amount} coin to {receiver}!")
        return
    await ctx.send(f"{author} has given {amount} coins to {receiver}!")


# Simple Trivia game. You can add your own Questions in the questions.txt file
@bot.command(brief="Easy difficulty, you can play one game a day.")
async def game1(ctx):
    author = ctx.message.author.mention
    global active_minigame
    if not signed_up(author):                                                                               # Checks if the author of the command is signed up and refreshes coins from file.
        await ctx.send("You are not signed up! Type !signup to start playing!")
        return
    if Already_played(author) and not infinite_games:                                                       # Checks if user has played a game recently.
        await ctx.send(f"You already played today.")
        return
    else:
        update_last_played(author)
    if active_minigame:
        await ctx.send('Game already started, you can stop it with !stop')
        return
    def check(m):                                                                                           # Makes sure the bot only accepts answers from the user that started it.
        return ctx.author == m.author
    gstart = await ctx.send('Game starting in 5 seconds. You have 10 seconds to solve the game')
    with open(questions, "r", encoding="utf8") as file:                                                     # Opens questions.txt
        lines = file.readlines()                                                                            # Saves lines in a list.
    question_and_answers = {}
    curq = None
    for l in lines:                                                                                         # Itterates over each line.
        if l.startswith("Q: ") and curq == None:
            curq = l[3:].strip()                                                                            # Temporarily saves questions.
        if l.startswith("A: ") and curq != None:                                                            # If there is a question temporarily saved.
            question_and_answers[curq] = l[3:].strip()                                                      # Adds saved question as key to dictionary with the answer as value.
            curq = None                                                                                     # Clears temporary save to get next question.
    active_minigame = True
    await asyncio.sleep(5)
    await gstart.delete()
    q = random.choice(list(question_and_answers.keys()))                                                    # Selects random question.
    a = question_and_answers[q]
    if active_minigame == True:                                                                             # Continues only if game was not stopped.
        await ctx.send(q)                                                                                   # Sends question.
        try:
            msg = await bot.wait_for('message', timeout=10.0, check=check)                                  # Listens for the next message of the author for 10 seconds.
            if msg.content.lower() == a.lower():                                                            # If the next message(lowercase) is the same as the answer(lowercase) you win.
                await ctx.send("Correct! You won 50 Coins!")
                coinchange(author, 50)                                                                      # Adds/Removes Coins to/from author.
                active_minigame = False
            else:
                if active_minigame == True:                                                                 # Continues only if game was not stopped.
                    await ctx.send("Wrong")
                active_minigame = False
        except asyncio.TimeoutError:                                                                        # Sends a message if you time out.
            if active_minigame == True:                                                                     # Continues only if game was not stopped.
                await ctx.send("Too slow!")
            active_minigame = False

# You have 2 seconds to remember 8 digits. Seems hard at first but gets easier the more you try it.
@bot.command(brief="Medium difficulty, you can play one game a day.")
async def game2(ctx):
    author = ctx.message.author.mention
    global active_minigame
    if not signed_up(author):                                                                               # Checks if the author of the command is signed up and refreshes coins from file.
        await ctx.send("You are not signed up! Type !signup to start playing!")
        return
    if Already_played(author) and not infinite_games:                                                       # Checks if user has played a game recently.
        await ctx.send(f"You already played today.")
        return
    else:
        update_last_played(author)
    if active_minigame:
        await ctx.send('Game already started, you can stop it with !stop')
        return
    def check(m):                                                                                           # Makes sure the bot only accepts answers from the user that started it.
        return ctx.author == m.author
    gstart = await ctx.send('Game starting in 3 seconds. You have 10 seconds to solve the game')
    active_minigame = True
    await asyncio.sleep(3)
    q = "/" + random.choice(game2images)                                                                    # Selects random image.
    a = q[:q.find(".png")]                                                                                  # Gets anwer from filename.
    if active_minigame == True:                                                                             # Continues only if game was not stopped.
        await gstart.delete()
        rem = await ctx.send("Remember the number")
        await asyncio.sleep(1)
        await rem.delete()
        id = await ctx.send(file=discord.File(current_directory + "/Game2/" + q))                           # Posts image of numbers.
        await asyncio.sleep(2)                                                                              # Deletes it after 2 seconds.
        await id.delete()
        ent = await ctx.send("Enter the number:")
        try:
            msg = await bot.wait_for('message', timeout=10.0, check=check)                                  # Listens for the next message of the author for 10 seconds.
            if msg.content == a:                                                                            # If the next message is the same as the answer you win.
                await ctx.send("Correct! You won 150 Coins!")
                coinchange(author, 150)                                                                     # Adds/Removes Coins to/from author.             
                active_minigame = False
                await ent.delete()
            else:
                if active_minigame == True:                                                                 # Continues only if game was not stopped.
                    await ent.delete()
                    await ctx.send("Wrong")
                active_minigame = False
        except asyncio.TimeoutError:                                                                        # Sends a message if you time out.
            if active_minigame == True:                                                                     # Continues only if game was not stopped.
                await ent.delete()
                await ctx.send("Too slow!")
            active_minigame = False

# Shitty version of the Fleeca minigame from NoPixel
# You can try the real game here: https://sharkiller.ddns.net/nopixel_minigame/fleeca/
@bot.command(brief="Hard difficulty, you can play one game a day. Type !help for more info", description="Fleeca minigame from NoPixel. You can practice here: https://sharkiller.ddns.net/nopixel_minigame/fleeca/")
async def game3(ctx):
    author = ctx.message.author.mention
    global active_minigame
    if not signed_up(author):                                                                               # Checks if the author of the command is signed up and refreshes coins from file.
        await ctx.send("You are not signed up! Type !signup to start playing!")
        return
    if Already_played(author) and not infinite_games:                                                       # Checks if user has played a game recently.
        await ctx.send(f"You already played today.")
        return
    update_last_played(author)
    if active_minigame:
        await ctx.send('Game already started, you can stop it with !stop')
        return
    def check(m):                                                                                           # Makes sure the bot only accepts answers from the user that started it.
        return ctx.author == m.author
    gstart = await ctx.send('Game starting in 3 seconds.')
    active_minigame = True
    await asyncio.sleep(3)
    q1 = random.choice(game3nums)                                                                           # Picks random picture from nums.
    a1 = str(q1[:q1.find(".JPG")]).strip()
    q2 = random.choice(game3images)                                                                         # Picks random picture from images.
    a2 = str(q2[:q2.find(".JPG")]).strip()
    # You have to write out every possible solution with the correct answer, so it's alot of work to add more variety.
    # It's sometimes hard to see the difference between red and purple or white and yellow, so i added both as correct answers.
    answer2 = "1234567890asdfghjkl"                                                                         # For error handling if answer2 is none
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
    if active_minigame == True:                                                                             # Continues only if game was not stopped.
        await gstart.delete()
        first_image = await ctx.send(file=discord.File(current_directory + "/Game3/nums/" + q1))
        await asyncio.sleep(3)                                                                              # Shows inital numbers for 3 seconds.
        await first_image.delete()
        second_image = await ctx.send(file=discord.File(current_directory +  "/Game3/images/" + q2))
        try:
            msg = await bot.wait_for('message', timeout=8.0, check=check)                                   # Listens for the next message of the author for 8 seconds.            
            if msg.content.lower() == answer or msg.content.lower() == answer2:                             # If the next message(lowercase) is the same as the answer(lowercase) you win.
                await ctx.send("Correct! You won 300 Coins!")
                coinchange(author, 300)                                                                     # Adds/Removes Coins to/from author.
                active_minigame = False
                await second_image.delete()
            else:
                if active_minigame == True:                                                                 # Continues only if game was not stopped.
                    await second_image.delete()
                    await ctx.send("Wrong")
                    active_minigame = False
        except asyncio.TimeoutError:                                                                        # Sends a message if you time out.
            if active_minigame == True:                                                                     # Continues only if game was not stopped.
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
    load_prediction()                                                                                       # Loads a active prediction from data.json, if there is one.
    if active_prediction:
        await ctx.send("There is already a Prediction active.")
        return
    if len(ctx.message.content.split()) < 2:                                                                # Checks if the user typed the prediction name after !prediction.
        await ctx.send("Enter the name of the Prediction after !prediction\n**Prediction not started!**")
        reset_prediction()
        return
    def check(m):                                                                                           # Makes sure the bot only accepts answers from the user that started it.
        return ctx.author == m.author
    await ctx.send("Enter bet Option seperated by ,\nExample: First, Second, Third")
    msg = await bot.wait_for('message', check=check, timeout=60.0)
    options = msg.content.split(",")                                                                        # Puts all options into a list seperated by ",".
    options = [i.strip() for i in options]                                                                  # Removes whitespaces at start/end points for each option.
    if len(options) < 2:                                                                                    # Checks if atleast 2 options were given.
        await ctx.send("Need atleast 2 options\n**Prediction not started!**")
        reset_prediction()
        return
    prediction_starter = ctx.message.author.mention
    prediction_name = " ".join(name)
    await ctx.send(f"@everyone\n{prediction_starter} has started a Prediction!\nYou can bet using\n!bet (number of the choice you want to pick) (amount of coins you want to bet)\nWithout the ( )\n**{prediction_name}**\nOptions:")
    active_prediction = True
    closed_prediction = False
    save_prediction()
    for n, i in enumerate(options):                                                                         # Sends the given options back in one list for better viewability.
        await ctx.send(f"**{n+1}**. {i}")

@bot.command(brief= "Lets you bet on an active prediction.")
async def bet(ctx, choice, amount):
    author = ctx.message.author.mention
    global both, total
    load_prediction()                                                                                       # Loads a active prediction from data.json, if there is one.
    if active_prediction == False:
        await ctx.send(f"No Prediction active. Start one with !prediction")
        return
    if closed_prediction == True:
        await ctx.send(f"Bets are closed!")
        return
    choicenr = int(choice)
    try:
        if choicenr > len(options):                                                                         # If users choose a number higher then the available options, they get an error message.
            await ctx.send(f"You chose number {choicenr} but there is only {len(options)} options.")
            return
    except ValueError:
        await ctx.send('Wrong format use !bet "number of choice" "coin amount"')
        return
    bet = int(amount)
    if not enough_coins(author, bet):                                                                       # Checks if the user has enough coins.
        await ctx.send("You don't have enough coins.")
        return
    choice = options[choicenr- 1]
    both[author] = [bet,choice]
    coinchange(author, -bet)                                                                                # Adds/Removes Coins to/from author.
    await ctx.send(f"{author} bet {bet} coins on {choice}\n")
    for n, i in enumerate(options):                                                                         # Sends the given options back in one list for better viewability.
        coins_on_i = 0                                                                              
        for bet, choice in both.values():                                                                   # Itterates over a list wich has the amount of what a user bet(index 0) and the name of the option(index 1).
            if choice == i:                                                                                 # If the name of what a user bet on matches the name of an option.
                coins_on_i += int(bet)                                                             
        sum_of_bets_per_option[i] = coins_on_i                                                              # I do it this way instead of writing directly to the dictionary to avoid KeyErrors when there is no value set to an option.
        await ctx.send(f"**{n+1} {i}**\nTotal: {sum_of_bets_per_option[i]}")
    save_prediction()

@bot.command(brief = "Closes an open prediction. Meaning no more bets allowed.")
async def close(ctx):
    global closed_prediction, active_prediction, total
    load_prediction()                                                                                       # Loads a active prediction from data.json, if there is one.
    if active_prediction == False:
        await ctx.send("No Prediction active")
        return
    if prediction_starter != ctx.message.author.mention:
        await ctx.send("Only the person that started the Prediction can close it!")
        return
    total = sum([int(f) for f in sum_of_bets_per_option.values()])                                          # Gets total by summing up all bets.
    closed_prediction = True
    await ctx.send("Bets are now closed!")
    save_prediction()

@bot.command(brief="Shows current prediction and bets")
async def active(ctx):
    if active_prediction or closed_prediction:
        await ctx.send(f"Current Prediction : {prediction_name}\n")
        for n, i in enumerate(options):
            await ctx.send(f"**{n+1} {i}**\nTotal: {sum_of_bets_per_option[i]}")
        return
    await ctx.send("No active prediction.")
 
@bot.command(brief="Lets the person who started the Prediction decide the winner.")
async def winner(ctx, winner):
    global active_prediction
    load_prediction()                                                                                       # Loads a active prediction from data.json, if there is one.
    if active_prediction == False:
        await ctx.send("No Prediction active")
        return
    if closed_prediction == False:
        await ctx.send("Prediction is not closed")
        return
    if prediction_starter != ctx.message.author.mention:
        await ctx.send("Only the person that started the Prediction can decide the winner!")
        return
    winner = options[int(winner)- 1]                                                                        # decides winner from input. -1 is to correct for the index starting at 0.
    if winner not in options:
        await ctx.send(f"{winner} was not an Option.\n Available Options:")
        for n, i in enumerate(options):                                                                     # Sends the given options back in one list for better viewability.
            await ctx.send(f"**{n+1}**. {i}")
        return
    for i in options:                                                                                       # Itterates over options to find winner.
        if i == winner:
            await ctx.send(f"The result is {winner}")
            for k, v in both.items():                                                                       # k = discord user v = list[(index 0 = bet amount), (index 1 = choice)].
                if v[1] == winner:                                                                          # If user chose the winning option.
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
    if not enough_coins(author, 50):                                                                        # Checks if user has enough coins.
        await ctx.send("You don't have enough coins.")
        return
    rand1 = random.randint(1, 6)                                                                            # Rolls dice 1.
    rand2 = random.randint(1, 6)                                                                            # Rolls dice 2.
    result = rand1 + rand2                                                                                  # Adds them together.
    emoji = {1:"1️⃣",2:"2️⃣",3:"3️⃣",4:"4️⃣",5:"5️⃣",6:"6️⃣"}                                                  # Dictionary to convert numbers to emojis.
    load_coins()                                                                                            # Reloads coins from file.
    coinchange(author, -50)                                                                                 # Adds/Removes Coins to/from author.
    await ctx.send(f"{emoji[rand1]}  {emoji[rand2]}")
    if result == 7 and choice == "seven":
        await ctx.send("**You win 250 Coins!**")
        coinchange(author, 250)                                                                             # Adds/Removes Coins to/from author.
    elif result <= 6 and choice == "low":
        await ctx.send("**You win 100 Coins!**")
        coinchange(author, 100)                                                                             # Adds/Removes Coins to/from author.
    elif result >=8 and choice == "high":
        await ctx.send("**You win 100 Coins!**")
        coinchange(author, 100)                                                                             # Adds/Removes Coins to/from author.
    else:
        await ctx.send("You lost :(")

# on_message triggers on every message
@bot.event
async def on_message(message):
    author = message.author.mention
    if message.author == bot.user:                                                                          # Returns if the message is from the bot.
        return
    if any(bad_word in message.content.lower().split() for bad_word in bad_words):                          # Checks if any word in the message matches a word on the bad_word list.
        await message.delete()                                                                              # Deletes message.
        await message.channel.send("You can't say that!\n**-100 Coins**")
        coinchange(author, -100)                                                                            # Adds/Removes Coins to/from author.
    if any(bad_word in message.content.lower().split() for bad_word in slurs):                              # Checks if any word in the message matches a word on the slurs list.
        await message.delete()                                                                              # Deletes message.
        await message.channel.send("That word is banned!\n**You lost all your coins!**")
        coinchange(author, -coinsd[author])                                                                 # Adds/Removes Coins to/from author.
    if str(message.channel) == meme_channelname:                                                            # If message is sent in meme channel.
        if "http" in message.content or message.attachments:                                                # Checks if message has http in it(this can be abused) or is a file.
            random_number = random.randint(1, 100)                                                          # Gets random number between 1-100.
            if random_number < 10:                                                                          # If number is lower then 10 (9% chance).
                await message.channel.send(f"{author} Nice meme!\n**+50 coins!**")
                coinchange(author, 50)                                                                      # Adds/Removes Coins to/from author.
    await bot.process_commands(message)                                                                     # Tells the bot to still listen to commands.

# Starts the bot
bot.run(BOT_TOKEN)