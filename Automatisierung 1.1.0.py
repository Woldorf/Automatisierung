import discord
from discord.ext import commands, tasks
from discord.utils import get

TOKEN = "Nzg5ODc2NDg2Njk3NjQ4MTY5.X94bzQ.mjYt_9zm3fa5CQ7ZzG-L0NE_vu8"
GUILD = "Bot test server"

#Enable events:
intents = discord.Intents.all()
#Create a function to do things:
bot = commands.Bot(command_prefix = "TNSS ", intents = intents)
global Messages, Results
Messages = []
Results = []

@bot.event
async def on_ready():
    global Guild, ThroneRoom, Announcements
    Guild = get(bot.guilds, name = GUILD)
    ThroneRoom = Guild.get_channel(794271850964189204)
    Announcements = Guild.get_channel(794668206119190539)
    #Confirm its ready:
    print("Up and running")

@tasks.loop(seconds = 10)
async def ThroneRoomLoop():
    global ThroneRoomActive
    if (ThroneRoomLoop.current_loop % 2) == 0:
        Active = False
    else:
        Active = True

    for Role in Guild.roles:
        if Role.name == "TEst Admin":
            Citizenry = Role
            
    if Active:
        for message in Messages:
            await message["Message"].delete()

        await ThroneRoom.set_permissions(Citizenry, view_channel = True)
        await Announcements.send("#throne-room is now open all yall!")
    else:
        await ThroneRoom.set_permissions(Citizenry, view_channel = False)
        await Announcements.send("#throne-room has closed. Voting will be held and results will be announced soon.")
        
        for message in Messages:
            await message["Message"].add_reaction("👍")
            await message["Message"].add_reaction("👎")

    ThroneRoomActive = Active

@bot.command()
async def RequestRank(ctx):
    Channel = ctx.channel
    Message = ctx.message

    if Channel.name == "snake-pit":
        User = Message.author

        Placement = 0
        for Role in Guild.roles[1:]:
            if Role == User.top_role:
                if Placement != (len(Guild.roles)):
                    RequestedRole = Guild.roles[Placement + 1]
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
        Channel.send("Incorrect channel. Message has been deleted. Please only use this command in #throne-room and only when it's open. Thanks")

#Stuff that is...Extra and may not be needed:
"""
@bot.command()
async def RequestRole(ctx, arg):
    Channel = ctx.channel
    Message = ctx.message

    if Channel.name == "snake-pit":
        User = Message.author

        for Role in Guild.roles[1:]:
            for UserRole in User.roles[1:]:
                if UserRole == Role:
                    await Channel.send(User.mention + "You already have that role.")
                else:
                    await discord.Message.delete(Message)
                    await Channel.send(User.mention + " Requests the personal role of: " + arg)
    else:
        discord.Message.delete(Message)
        ctx.send("Incorrect channel. Message has been deleted. Please only use this command in #throne-room and only when it's open. Thanks")"""

@bot.event()
async def on_raw_reaction_add(payload):
    ThroneRoom = Guild.get_channel(794271850964189204)
    Placement = 0
    #ReactionCount = get(payload.message.reactions, emoji=payload.emoji.name).count
    if (payload.channel_id == ThroneRoom.id) and not ThroneRoomActive:
        for message in Messages:
            if message["Message"] == payload.message and Messages[Placement]["Role"].name == "Regent":
                if payload.member.top_role.name != "Regent":
                    await message["Message"].remove_reaction(payload.emoji,payload.member)

@bot.command()
async def LoopSettings():
    async def Restart(ctx):
        Member = ctx.message.member
        if Member.top_role.name != "Regent":
            await ctx.send("You do not have permission to access this command.")
        else:
            ThroneRoomLoop()
            await ctx.send("The #throne-room open/close cycle has been restarted. The current loop time is: " + str(ThroneRoomLoop.next_iteration))
            await ThroneRoomLoop.restart()

    async def Start(ctx):
        Member = ctx.message.member
        if Member.top_role.name != "Regent":
            await ctx.send("You do not have permission to access this command.")
        else:
            if ThroneRoomLoop.running():
                if ThroneRoomActive:
                    await ctx.send("The #throne-room loop is already running. #throne-room is already open and will close on: " + str(ThroneRoomLoop.next_iteration))
                else:
                    await ctx.send("The #throne-room loop has been started")
                    await ThroneRoomLoop.start()
    
    async def Stop(ctx):
        Member = ctx.message.member
        if Member.top_role.name != "Regent":
            await ctx.send("You do not have permission to access this command.")
        else:
            if not ThroneRoomLoop.running():
                await ctx.send("The #throne-room loop is not running.")
            else:
                await ctx.send("The #throne-room loop has been stopped.")
                await ThroneRoomLoop.cancel()


@bot.listen("on_message")
async def Responder(message):
    if message.content == "E":
        await message.channel.send("Oh?")



bot.run(TOKEN)  