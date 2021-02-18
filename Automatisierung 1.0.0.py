import os, discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks
from dotenv import load_dotenv

#Load the .env file
load_dotenv()
#Get the bots token
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

#Enable events:
intents = discord.Intents.all()
#Create a function to do things:
bot = commands.Bot(command_prefix = "TNSS ", intents = intents)
Guild = get(bot.guilds, name = GUILD)

@bot.event
async def on_ready():
    global Guild
    Guild = get(bot.guilds, name = GUILD)
    #Confirm its ready:
    print("Up and running")
  
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
        await Channel.send(User.mention + " Requests the rank of: " + str(RequestedRole))
    else:
        await discord.Message.delete(Message)
        Channel.send("Incorrect channel. Message has been deleted. Please only use this command in #throne-room and only when it's open. Thanks")

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
        ctx.send("Incorrect channel. Message has been deleted. Please only use this command in #throne-room and only when it's open. Thanks")

@bot.listen("on_message")
async def Responder(message):
    if message.content == "E":
        await message.channel.send("Oh?")

@tasks.loop(seconds = 5)
async def ThroneRoomLoop():
    pass

ThroneRoomLoop.start()

bot.run(TOKEN)  