#!/usr/bin/python3
import discord,random
from discord.ext import commands, tasks
from discord.utils import get

TOKEN = "Nzg5ODc2NDg2Njk3NjQ4MTY5.X94bzQ.mjYt_9zm3fa5CQ7ZzG-L0NE_vu8"
GUILD = "The New Server Server"

#Enable events:
intents = discord.Intents.all()
#Create a function to do things:
bot = commands.Bot(command_prefix = "Fish ", intents = intents)
global MessageListImportant, ThroneRoomActive
MessageListImportant = []
RoleHeigherarchy = ["Citizenry","Good Lad","Count","Duke","Regent","Head Regent","King"]
RoleHeigherarchy2 = ["Citizenry","Good Lady","Countess","Duchess","Regent","Head Regent","King"]
ThroneRoomActive = False

async def RoleGetter(Member,RoleNeeded):
    Cleared = False
    for role in Member.roles:
        if role.name != RoleNeeded:
            Cleared = False
        else:
            Cleared = True
            break
    return Cleared

@bot.event
async def on_ready():
    global Guild, ThroneRoom, Announcements, AdminBotChannel
    Guild = get(bot.guilds, name = GUILD)
    Channels = await Guild.fetch_channels()

    for channel in Channels:
        if channel.name == "throne-room":
            ThroneRoom = channel
        elif channel.name == "announcements":
            Announcements = channel
        elif channel.name == "admin-bots":
            AdminBotChannel = channel

    StatusChangeLoop.start()

@tasks.loop(hours = 196)
async def ThroneRoomLoop():
    Active = True
    if ThroneRoomLoop.current_loop == 0:
        Active = True
        ThroneRoomLoop.change_interval(72)
    elif (ThroneRoomLoop.current_loop % 2) == 0:
        Active = True
        ThroneRoomLoop.change_interval(72)
    else:
        Active = False
        ThroneRoomLoop.change_interval(196)

    for Role in Guild.roles:
        if Role.name == RoleHeigherarchy[0]:
            Citizenry = Role

    if Active:
        await ThroneRoom.purge()
        await ThroneRoom.set_permissions(Citizenry, view_channel = True)
        await ThroneRoom.send("Use the command `Fish Title` to automatically request the rank higher than you are currently at. You must have the Good Lad/Lady rank to request higher ranks.")
        MessageToDelete = await Announcements.send(ThroneRoom.mention + " is now open all yall!")
    else:
        await ThroneRoom.set_permissions(Citizenry, view_channel = False)
        MessageToDelete = await Announcements.send(ThroneRoom.mention + " has closed. Voting will be held and results will be announced soon.")
        
        for member in  Guild.members:
            if member.top_role.name == "Citizenry":
                Message = await  ThroneRoom.send("Grant " + member.mention + " the Good Lad/Lady role?")
                Data = {"Message":Message,"Role":Citizenry}
                MessageListImportant.append(Data)

        for message in MessageListImportant:
            await message["Message"].add_reaction("👍")
            await message["Message"].add_reaction("👎")

    await MessageToDelete.delete(delay = 345600)
    ThroneRoomActive = Active

@tasks.loop(hours = 24)
async def StatusChangeLoop():
    Options = ["I spent way too much time on this","I should get a life","Why do I do all the grunt work?","Pedro for president 2024!",\
                "Minecraft","Can I earn money doing this?","Earth is fine, people are dumb",\
                "Everyone should be able to do one card trick, tell two jokes, and recite three poems, in case they are ever trapped in an elevator",\
                "Bruh","When a bird hits your window have you ever wondered if God is playing angry birds with you?",\
                "When I’m on my death bed, I want my final words to be “I left one million dollars in the…",\
                "My study period = 15 minutes. My break time = 3 hours","Never make eye contact while eating a banana",\
                "C.L.A.S.S- come late and start sleeping","My biggest concern in life is actually how my online friends can be informed of my death!",\
                "How do you know what it’s like to be stupid if you’ve never been smart?","I hate fake people. You know what I’m talking about. Mannequins."\
                "Everything is 10x funnier when you are not supposed to laugh.","It may look like I’m deep in thought, but 99% of the time I’m just thinking about what food to eat later.",\
                "\"Focusing\" on school work","That awkward moment when you realize that dora, who is 5, has more freedom than you.",\
                "That awkward when your eyes assumed “moment” was written after \"awkward\"","Never gonna let you down","Never gonna run around",\
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ","I lost the game","Dont forget to like and subscribe!","Imagine putting in effort",\
                "I put the most effort into these quotes","If you have more status ideas, DM helaugheth#5815","Epsilon SMP!","Psst, is anyone watching these?",\
                "There are 10 types of people, those who understand binary and those who dont","I should focus on college homework","There are 13 lines of quotes for me to choose from.",\
                "Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn","#SupportC'thulu","#LearnParsletoung","I'm adding these during class","lol",\
                "XD","Bro this releaves so much boredom","Shoot, I should do homework","College classes are BORING","All around me are familiar faces...",\
                "What is this...\"Fish Commands\" thing?","Yar dar dar and a hody hody do","https://www.youtube.com/watch?v=Q04Lkw91Gts"]

    Status = random.choice(Options)
    await bot.change_presence(activity = discord.Game(name = Status))

@bot.command(help = "Request 1 title higher than you currently have.")
async def Title(ctx):
    Message = ctx.message

    if ctx.channel == ThroneRoom and ThroneRoomActive:
        User = Message.author
        RoleChosen = False
        Cleared = False
        TitleList = Guild.roles
        RequestedTitle = "TEST"

        for role in User.roles:
            if role.name == RoleHeigherarchy[1]:
                CurrentTitle = {"Role":role,"Rank":1,"H":1}
                Cleared = True
            elif role.name == RoleHeigherarchy2[1]:
                CurrentTitle = {"Role":role,"Rank":1,"H":2}
                Cleared = True

            elif role.name == RoleHeigherarchy[2]:
                CurrentTitle = {"Role":role,"Rank":2,"H":1}
            elif role.name == RoleHeigherarchy2[2]:
                CurrentTitle = {"Role":role,"Rank":2,"H":2}

            elif role.name == RoleHeigherarchy[3]:
                CurrentTitle = {"Role":role,"Rank":3,"H":1}
            elif role.name == RoleHeigherarchy2[3]:
                CurrentTitle = {"Role":role,"Rank":3,"H":2}

            elif role.name == RoleHeigherarchy[4] or role.name == RoleHeigherarchy2[4]:
                CurrentTitle = {"Role":role,"Rank":4,"H":1}
            elif role.name == RoleHeigherarchy[5] or role.name == RoleHeigherarchy2[5]:
                CurrentTitle = {"Role":role,"Rank":5,"H":1}
            elif role.name == RoleHeigherarchy[6] or role.name == RoleHeigherarchy2[6]:
                CurrentTitle = {"Role":role,"Rank":6,"H":1}
                        
        if not Cleared:
            await ctx.send("You need a higher rank to be able to request titles.")
        else:
            for Title in TitleList[1:]:
                if Title == CurrentTitle["Role"]:
                    if CurrentTitle["Rank"] < 4:
                        if CurrentTitle["H"] == 1:
                            RequestedTitle = RoleHeigherarchy[CurrentTitle["Rank"] + 1]
                            RoleChosen = True
                        else:
                            RequestedTitle = RoleHeigherarchy2[CurrentTitle["Rank"] + 1]
                            RoleChosen = True

                    elif CurrentTitle["Rank"] == 4:
                        await ctx.send("That title is granted by the King, you cannot request it")
                        RoleChosen = False

                    elif CurrentTitle["Rank"] == 5:
                        await ctx.send("When the King ~~dies~~ leaves you are given his title. Otherwise you cant request the King title")
                        RoleChosen = False

                    elif CurrentTitle["Rank"] == 6:
                        await ctx.send("You're already top of the ship mate. You cant request any higher")
                        RoleChosen = False
            
                if RoleChosen:
                    if Title.name == RequestedTitle:
                        NewMessage = await ctx.send(User.mention + " Requests the title of: " + str(Title.name))

                        await discord.Message.delete(Message)
                        NewData = {"Message": NewMessage,"Role":Title}
                        MessageListImportant.append(NewData)

    else:
        await discord.Message.delete(Message)
        Message = await ctx.send("Incorrect channel. Message has been deleted. Please only use this command in #throne-room and only when it's open.")
        await Message.delete(delay=10)

@bot.command(help = "None")
async def LoopSettings(ctx, arg):
    Member = ctx.message.author
    Cleared = await RoleGetter(Member,"Regent")
            
    if not Cleared:    
        await ctx.send("You do not have permission to access this command.")

    else:
        if arg == "Restart":
            ThroneRoomLoop()
            await AdminBotChannel.send("The #throne-room open/close cycle has been restarted. The current loop time is: " + str(ThroneRoomLoop.next_iteration))
            await ThroneRoomLoop.restart()

        elif arg == "Start":
            if ThroneRoomLoop.is_running():
                if  ThroneRoomActive:
                    await AdminBotChannel.send("The #throne-room loop is already running. #throne-room is currently open and will close on: " + str(ThroneRoomLoop.next_iteration))
                else:
                    await AdminBotChannel.send("The #throne-room loop is already running. #throne-room is currently closed and will open on: " + str(ThroneRoomLoop.next_iteration))
            else:
                await AdminBotChannel.send("The #throne-room loop has been started")
                await ThroneRoomLoop.start()

        elif arg == "Stop":
            if not ThroneRoomLoop.is_running():
                await AdminBotChannel.send("The #throne-room loop is not running.")
            else:
                await AdminBotChannel.send("The #throne-room loop has been stopped.")
                await Announcements.send(ThroneRoom.mention + " has closed. Voting will be held and results will be announced soon.")
                ThroneRoomLoop.cancel()

@bot.command(help = "Shows available commands")
async def Commands(ctx):
    Help = discord.Embed()
    Help.add_field(name = "BOT PREFIX", value = "Fish")
    Help.add_field(name = "COMMANDS", value = "`Title`")
    Help.add_field(name = "Title:", value = "Only available when the Throne Room is available and if you have the Good Lad/Lady Title. EX: Fish Title")
    await ctx.send(embed = Help)

@bot.command(help = "None")
async def AdminHelp(ctx):
    Member = ctx.message.author
    Cleared = False
    Cleared = await RoleGetter(Member,"Regent")
    if not Cleared:    
        await ctx.send("You do not have permission to access this command.")
    else:
        Help = discord.Embed()
        Help.add_field(name = "BOT PREFIX", value = "Fish")
        Help.add_field(name = "HIDDEN COMMANDS", value = "`LoopSettings`, `Clear`")
        Help.add_field(name = "LoopSettings", value = "Has 3 sub-commands: Restart, Start and Stop. They will each do that to the Throne Room loop. EX: Fish LoopSettings Start/Stop/Restart")
        Help.add_field(name = "Clear", value = "Clear an amount of messages from a channel. EX: Fish Clear 6")
        await AdminBotChannel.send(embed = Help)

@bot.command(help = "None")
async def Clear(ctx,arg):
    Cleared = await RoleGetter(ctx.message.author,"Duke")
    Cleared2 = await RoleGetter(ctx.message.author,"Duchess")

    if not Cleared and not Cleared2:
        await ctx.send("You do not have permission to access this command.")
    else:
        await ctx.channel.purge(limit=int(arg))

@bot.event
async def on_raw_reaction_add(payload):
    User = Guild.get_member(payload.member.id)
    if (payload.channel_id ==  ThroneRoom.id):
        for message in MessageListImportant:
            for role in User.roles:
                if role.name != message["Role"].name and User != bot.user:
                    Cleared = False
                else:
                    Cleared = True
                    break
            if not Cleared:
                await message["Message"].remove_reaction(payload.emoji,payload.member)

@bot.listen("on_message")
async def Responder(message):
    if message.content == "E":  
        Message2 = await message.channel.send("Oh?")
        await message.delete(delay = 5)
        await Message2.delete(delay = 5)

bot.run(TOKEN)