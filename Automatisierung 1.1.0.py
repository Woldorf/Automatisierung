import discord,random
from discord.ext import commands, tasks
from discord.utils import get

TOKEN = "Nzg5ODc2NDg2Njk3NjQ4MTY5.X94bzQ.mjYt_9zm3fa5CQ7ZzG-L0NE_vu8"
GUILD = "Bot test server"

#Enable events:
intents = discord.Intents.all()
#Create a function to do things:
bot = commands.Bot(command_prefix = "TNSS ", intents = intents)
global Messages
Messages = []

@bot.event
async def on_ready():
    global Guild, ThroneRoom, Announcements
    Guild = get(bot.guilds, name = GUILD)
    ThroneRoom = Guild.get_channel(813135696801038407)
    Announcements = Guild.get_channel(813135672901894154)
    #BTS Anouncements - 813135672901894154
    #BTS Throne Room - 813135696801038407
    #TNSS Anouncements - 698267492480712743
    #TNSS Throne Room - 757391765845180416

    StatusChangeLoop.start()

    #Confirm its ready:
    print("Up and running")

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
        if Role.name == "TEST ADMIN":
            Citizenry = Role
            
    if Active:
        MessageList= await ThroneRoom.history().flatten()
        for message in MessageList:
            await message.delete()

        await ThroneRoom.set_permissions(Citizenry, view_channel = True)
        await ThroneRoom.send("Use the command `TNSS RequestRank` to automatically request the rank higher than you are currently at. You must have the Good Lad/Lady rank to request higher ranks.")
        await Announcements.send(ThroneRoom.mention + " is now open all yall!")

    else:
        await  ThroneRoom.set_permissions(Citizenry, view_channel = False)
        await  Announcements.send(ThroneRoom.mention + " has closed. Voting will be held and results will be announced soon.")
        
        for member in  Guild.members:
            if member.top_role.name == "Citizenry":
                Message = await  ThroneRoom.send("Grant " + member.mention + " the Good Lad/Lady role")
                Data = {"Message":Message,"Role":Citizenry}
                Messages.append(Data)

        for message in Messages:
            await message["Message"].add_reaction("👍")
            await message["Message"].add_reaction("👎")

    ThroneRoomActive = Active

@tasks.loop(hours = 96)
async def StatusChangeLoop():
    Options = ["I spent way too much time on this","I should get a life","Why do I do all the grunt work?","Pedro for president 2024!","Your commands",]
    Status = random.choice(Options)
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = Status))

@bot.command(help = "Request 1 rank higher than you currently have.")
async def RequestRank(ctx):
    Channel = ctx.channel
    Message = ctx.message

    if Channel.name == "snake-pit":
        User = Message.author

        if User.top_role.name == "Citizenry":
            ctx.send("You need a higher rank to be able to request ranks.")
        else:
            Placement = 0
            for Role in  Guild.roles[1:]:
                if Role == User.top_role:
                    if Placement != (len( Guild.roles)):
                        RequestedRole =  Guild.roles[Placement + 1]
                Placement += 1

            await discord.Message.delete(Message)

            if RequestedRole.name == "Head Regent":
                NewMessage = await Channel.send(User.mention + " That role is not requestable.")
            else:
                NewMessage = await Channel.send(User.mention + " Requests the rank of: " + str(RequestedRole))
            NewData = {"Message": NewMessage,"Role":RequestedRole}
            Messages.appened(NewData)
    else:
        await discord.Message.delete(Message)
        Message = await Channel.send("Incorrect channel. Message has been deleted. Please only use this command in #throne-room and only when it's open.")
        await Message.delete(delay=10)

@bot.event
async def on_raw_reaction_add(payload):
    Placement = 0
    if (payload.channel_id ==  ThroneRoom.id) and not ThroneRoomActive:
        for message in Messages:
            if message["Message"] == payload.message and Messages[Placement]["Role"].name == "Regent":
                if payload.member.top_role.name != "Regent":
                    await message["Message"].remove_reaction(payload.emoji,payload.member)
            Placement += 1

@bot.command(help = "Commands available only to Regents to change whats up with the #throne-room loop settings.")
async def LoopSettings(ctx, arg):
    Member = ctx.message.author
    if Member.top_role.name != "Regent":
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
                await ThroneRoomLoop.cancel()

@bot.command(help = "Change interval of #throne-room cycle in hours.")
async def LoopInterval(ctx, arg):
    Member = ctx.message.author
    if Member.top_role.name != "Regent":
        await ctx.send("You do not have permission to access this command.")
    else:
        ThroneRoomLoop.change_interval(hours = int(arg))
        ThroneRoomLoop.restart()
        await ctx.send("Interval changed to: " + str(arg) + " hours and restarted.")

@bot.command(help = "Shows available commands")
async def Commands(ctx):
    Help = discord.Embed()
    Help.add_field(name = "BOT PREFIX", value = "TNSS")
    Help.add_field(name = "COMMANDS", value = "RequestRank")
    Help.add_field(name = "RequestRank", value = "Ex: TNSS RequestRank. Only available when the Throne Room is available and if you have the Good Lad/Lady role")

    await ctx.send(embed = Help)

@bot.listen("on_message")
async def Responder(message):
    if message.content == "E":
        await message.channel.send("Oh?")

bot.run(TOKEN)  