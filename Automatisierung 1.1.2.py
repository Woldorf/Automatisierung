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

async def RoleGetter(Member):
    Cleared = False
    for role in Member.roles:
        if role.name != "Regent":
            Cleared = False
        else:
            Cleared = True
            break
    return Cleared

@bot.event
async def on_ready():
    global Guild, ThroneRoom, Announcements
    Guild = get(bot.guilds, name = GUILD)
    Channels = await Guild.fetch_channels()

    for channel in Channels:
        if channel.name == "throne-room":
            ThroneRoom = channel
        elif channel.name == "announcements":
            Announcements = channel

    StatusChangeLoop.start()

@tasks.loop(hours = 196)
async def ThroneRoomLoop():
    global ThroneRoomActive
    Active = True
    if ThroneRoomLoop.current_loop == 0:
        Active = True
    elif (ThroneRoomLoop.current_loop % 2) == 0:
        Active = True
    else:
        Active = False

    for Role in Guild.roles:
        if Role.name == RoleHeigherarchy[0]:
            Citizenry = Role

    if Active:
        MessageList = await ThroneRoom.history().flatten()
        for message in MessageList:
            await message.delete()

        await ThroneRoom.set_permissions(Citizenry, view_channel = True)
        await ThroneRoom.send("Use the command `Fish Title` to automatically request the rank higher than you are currently at. You must have the Good Lad/Lady rank to request higher ranks.")
        #MessageToDelete = await Announcements.send(ThroneRoom.mention + " is now open all yall!")

    else:
        await ThroneRoom.set_permissions(Citizenry, view_channel = False)
        #MessageToDelete = await Announcements.send(ThroneRoom.mention + " has closed. Voting will be held and results will be announced soon.")
        
        for member in  Guild.members:
            if member.top_role.name == "Citizenry":
                Message = await  ThroneRoom.send("Grant " + member.mention + " the Good Lad/Lady role?")
                Data = {"Message":Message,"Role":Citizenry}
                MessageListImportant.append(Data)

        for message in MessageListImportant:
            await message["Message"].add_reaction("👍")
            await message["Message"].add_reaction("👎")

    #await MessageToDelete.delete(delay = 345600)
    ThroneRoomActive = Active

@tasks.loop(hours = 96)
async def StatusChangeLoop():
    Options = ["I spent way too much time on this","I should get a life","Why do I do all the grunt work?","Pedro for president 2024!","Minecraft"]
    Status = random.choice(Options)
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = Status))

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
    Cleared = await RoleGetter(Member)
            
    if not Cleared:    
        await ctx.send("You do not have permission to access this command.")

    else:
        if arg == "Restart":
            ThroneRoomLoop()
            await ctx.send("The #throne-room open/close cycle has been restarted. The current loop time is: " + str(ThroneRoomLoop.next_iteration))
            await ThroneRoomLoop.restart()

        elif arg == "Start":
            if ThroneRoomLoop.is_running():
                if  ThroneRoomActive:
                    await ctx.send("The #throne-room loop is already running. #throne-room is currently open and will close on: " + str(ThroneRoomLoop.next_iteration))
                else:
                    await ctx.send("The #throne-room loop is already running. #throne-room is currently closed and will open on: " + str(ThroneRoomLoop.next_iteration))
            else:
                await ctx.send("The #throne-room loop has been started")
                await ThroneRoomLoop.start()
    
        elif arg == "Stop":
            if not ThroneRoomLoop.is_running():
                await ctx.send("The #throne-room loop is not running.")
            else:
                await ctx.send("The #throne-room loop has been stopped.")
                #await Announcements.send(ThroneRoom.mention + " has closed. Voting will be held and results will be announced soon.")
                ThroneRoomLoop.cancel()

@bot.command(help = "Change interval of #throne-room cycle in hours.")
async def LoopInterval(ctx, arg):
    Member = ctx.message.author
    Cleared = False
    Cleared = await RoleGetter(Member)
            
    if not Cleared:    
        await ctx.send("You do not have permission to access this command.")

    else:
        ThroneRoomLoop.change_interval(hours = int(arg))
        ThroneRoomLoop.restart()
        await ctx.send("Interval changed to: " + str(arg) + " hours and restarted.")

@bot.command(help = "Shows available commands")
async def Commands(ctx):
    Help = discord.Embed()
    Help.add_field(name = "BOT PREFIX", value = "Fish")
    Help.add_field(name = "COMMANDS", value = "Title")
    Help.add_field(name = "Title:", value = "Only available when the Throne Room is available and if you have the Good Lad/Lady Title")
    Help.add_field(name = "EXAMPLE:", value = "Ex: Fish Title")
    await ctx.send(embed = Help)

@bot.command(help = "None")
async def Password(ctx):
    Member = ctx.message.author
    Cleared = False
    Cleared = await RoleGetter(Member)
            
    if not Cleared:    
        await ctx.send("You do not have permission to access this command.")

    else:
        Help = discord.Embed()
        Help.add_field(name = "BOT PREFIX", value = "Fish")
        Help.add_field(name = "HIDDEN COMMANDS", value = "LoopSettings and LoopInterval")
        Help.add_field(name = "LoopSettings", value = "Has 3 sub-commands: Restart, Start and Stop. They will each do that to the Throne Room loop. EX: Fish LoopSettings Start/Stop/Restart")
        Help.add_field(name = "LoopInterval", value = "Has 1 function: Time. It will change the Throne Room loop interval to Time amount of hours. EX: Fish LoopInterval 56")
        await ctx.send(embed = Help)

@bot.event
async def on_raw_reaction_add(payload):
    User = Guild.get_member(payload.member.id)
    if (payload.channel_id ==  ThroneRoom.id):
        for message in MessageListImportant:
            for role in User.roles:
                if role.name != message["Role"] and User != bot.user:
                    Cleared = False
                else:
                    Cleared = True
            if not Cleared:
                await message["Message"].remove_reaction(payload.emoji,payload.member)

@bot.listen("on_message")
async def Responder(message):
    if message.content == "E":  
        await message.channel.send("Oh?")

bot.run(TOKEN)