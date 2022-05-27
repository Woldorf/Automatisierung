#!/usr/bin/python3.8
#import the libraries:
import asyncio,discord,random,requests,mctools,time,logging,json
from datetime import datetime
from bs4 import BeautifulSoup as bs4
from datetime import datetime
from discord.ext import commands, tasks
from discord.utils import get

format = logging.Formatter('%(name)s @ [%(asctime)s] - %(message)s', datefmt='%m/%d/%Y %I:%M %p')
logger = logging.getLogger('The Butler')
file = logging.FileHandler(filename='./ERRORS.log',mode='a')
file.setFormatter(format)
logger.addHandler(file)

DATAPATH = './data.json'

#WORKING ON
#Theoretically optimizing the throne room loop - Not a pressing issue though

"""
Functions verified to work as expected:
getJSONfile
writeJSONFile
ReactionCheck
serverCheck
Loops verified to work as expected:
StatusChangeLoop
"""

#Bot Token:
TOKEN = ""
#Guild name:
GUILD = "Bot test server"
#Rcon setup stuff:
#ANYTHING WITH A 2 AFTER IT REFERS TO THE SECONDARY SERVER
"""
RCONPORT = '25575'
PINGPORT='25565'  #Same port the server is hosted on
RCONPORT2= '25579'
PINGPORT2='25578' #Same port the secondary server is hosted on
RCONPASS = 'Spghtt'
RCONHOST = '192.168.29.39'
"""
#SQL_DB = 'db.sqlite3'

#Enable events:
intents = discord.Intents.all()
#Create a function to do things:
prefixes = ['$']
bot = commands.Bot(command_prefix = prefixes, intents = intents)

#Global variables needed across functions:
global ThroneRoomActive, Guild
ThroneRoomActive = False
RoleHeigherarchy = ["Citizenry","Good Lad","Count","Duke","Regent","Head Regent","King"]
RoleHeigherarchy2 = ["Citizenry","Good Lady","Countess","Duchess","Regent","Head Regent","King"]
GoodLadCheck = ['Good Lad','Good Lady','Count','Countess','Duke','Duchess','Regent','Head Regent','King']
CountCheck = ['Count','Countess','Duke','Duchess','Regent','Head Regent','King']
DukeCheck =['Duke','Duchess','Regent','Head Regent','King']
RegentCheck = ['Regent','Head Regent','King']

#Default responces:
#Timeout:
TIMEOUTR=['Mate, you timed out','Try typing like lightning next time buckaroo','My grandma can type faster than you and she\'s dead','Type faster...Please...']
BADCOMMANDR=["Bruh, that aint a valid command", "Try that command again buckaroo",'My guy...You failed your one task of entering a valid command',\
            'Dont worry, that might not be a valid command but I\'m sure your next one will be', 'If you spent as much time on entering the right command as I do on these messages you might get them correct']

def getJSONFile():
    with open(DATAPATH,'r') as F:
        temp = json.load(F)
    return temp

def writeJSONFile(new):
    with open(DATAPATH,'w') as F:
        F.write(json.dumps(new,indent=2))

def opCommand(Command,User,server):
    # TODO what if any of these function calls fail?
    jsonData = getJSONFile()
    if server == 'main' or server == 'secondary':
        rconClient = mctools.mclient.RCONClient(host=jsonData['RCON']['ip'],
                                                port=jsonData['RCON'][server]['rconport'], 
                                                format_method=1,
                                                timeout=60)
        rconClient.authenticate(jsonData['RCON']['password'])  # TODO is this really just a plain-text password stored in RAM? THEN STORED IN A FILE?
        textData = rconClient.command(Command).replace('[0m','')  # TODO why are we removing this? What's significant about it?
        rconClient.stop()
    else:
        textData = '' # Server is not main or secondary, but we still need this string. TODO should this log this?
    jsonData['RCONLogs'].append({
        'user':str(User.display_name),
        'date':str(datetime()),
        'command':str(Command),
        'return':str(textData)
    })
    writeJSONFile(jsonData)
    return textData

def ReactionCheck(Message,left,right):
    def check(reaction, user):
        if reaction.message.id != Message.id or user == bot.user:
            return False
        if left and reaction.emoji == "⏪":
            return True
        if right and reaction.emoji == "⏩":
            return True
        return False
    return check

async def serverCheck(ctx):
    embed = discord.Embed(color=discord.Color.dark_gold(),description='Which server would you like to run it on?')
    embed.add_field(name='Standard',value='The standard minecraft server')
    embed.add_field(name='Event',value='Minecraft server that minigames are run on')
    embed.set_footer(text='[1/2] is what you should put in the chat')
    message = await ctx.channel.send(embed=embed)
    try:
        response = await bot.wait_for("message",check=lambda i: i.author == ctx.message.author,timeout=60)
        await message.delete()
        await response.delete()
    except asyncio.TimeoutError:
        temp=await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR)))
        await message.delete()
        await temp.delete(delay=15)
        return 'FAIL'
    else:
        if response.content == '1':
            return 'main'
        elif response.content == '2':
            return 'secondary'
        else:
            temp=await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=random.choice(BADCOMMANDR)))
            return 'FAIL'

async def statUpdate(Port,cleared,server,event,message=None):
    try:
        ping = mctools.PINGClient(host=jsonData['RCON']['ip'],port=int(Port))
        stats = ping.get_stats()
        ping.stop()
    except:
        if server == 'main':
            embed = discord.Embed(color=discord.Color.dark_gold(),title='Main server')
        elif server == 'secondary':
            embed = discord.Embed(color=discord.Color.dark_gold(),title='Minigame server')
        embed.add_field(name='Server IP',value=('OFFLINE'),inline=False)
        embed.add_field(name='Status',value='OFFLINE')
        embed.add_field(name='Minecraft Version',value='OFFLINE')
        embed.add_field(name='Server TPS',value='OFFLINE',inline=False)
        embed.add_field(name='Server Uptime',value='OFFLINE',inline=False)
        embed.add_field(name='Player Stats',value='OFFLINE',inline=False)
        embed.add_field(name='Players Online',value='OFFLINE',inline=False)
        embed.add_field(name='Upcoming event',value='\u200b'+event)
        embed.add_field(name='Next Scheduled Restart',value='OFFLINE',inline=False)
        message = await importantChannels['serverstats'].send(embed=embed)
        return
    serverVersion=stats['version']['name']
    maxP=stats['players']['max']
    onlineCountP=stats['players']['online']
    pList = ''
    try:
        for index,i in enumerate(stats['players']['sample']):
            if index < len(stats['players']['sample'])-1:
                temp = i[0].replace('\x1b','')
                temp = temp.replace('[0m','')
                pList += (temp+', ')
            else:
                temp = i[0].replace('\x1b','')
                temp = temp.replace('[0m','')
                pList += (temp)
    except Exception as E:
        pList='NONE'
    jsonData=getJSONFile()
    if server == 'main':
        rconClient = mctools.mclient.RCONClient(host=jsonData['RCON']['ip'],port=jsonData['RCON']['main']['rconport'],format_method=1,timeout=60)
    else:
        rconClient = mctools.mclient.RCONClient(host=jsonData['RCON']['ip'],port=jsonData['RCON']['secondary']['rconport'],format_method=1,timeout=60)
    rconClient.authenticate(jsonData['RCON']['password'])
    tpsData = rconClient.command('tps')
    tpsData = tpsData.replace('[0m','')
    daysData = rconClient.command('time query day')
    daysData = daysData.replace('[0m','')
    rconClient.stop()

    tps = 0
    for i,char in enumerate(tpsData):
        if char == '*':
            tps += int(tpsData[i+1:i+3])
    tps = tps/3
    
    for i,char in enumerate(daysData):
        if i != len(daysData)-1:
            if char + daysData[i+1] == 's ':
                days = daysData[i+2:]
                break

    #formatting output for the standard server:
    if server == 'main':
        embed = discord.Embed(color=discord.Color.dark_gold(),title='Main server')
    elif server == 'secondary':
        embed = discord.Embed(color=discord.Color.dark_gold(),title='Minigame server')
    jsonData = getJSONFile()
    embed.add_field(name='Server IP',value=(jsonData['RCON']['ip']+':'),inline=False)
    embed.add_field(name='Status',value='Online')
    embed.add_field(name='Minecraft Version',value='\u200b'+str(serverVersion),inline=False)
    embed.add_field(name='Server TPS',value='\u200b'+str(tps),inline=False)
    embed.add_field(name='Server Uptime',value='\u200b'+(str(days)+' days'),inline=False)
    embed.add_field(name='Player Stats',value='\u200b'+(str(onlineCountP)+'/'+str(maxP)),inline=False)
    embed.add_field(name='Players Online',value='\u200b'+pList,inline=False)
    embed.add_field(name='Upcoming event',value='\u200b'+event)
    embed.add_field(name='Next Scheduled Restart',value='Wednesday night at midnight',inline=False)

    if cleared:
        await message.edit(embed=embed)
    else:
        message = await importantChannels['serverstats'].send(embed=embed)
    return message.id

#Once the bot has fully come online run this function before everything else:
@bot.event
async def on_ready():
    global Guild, importantChannels, CITIZENRY,ThroneRoomActive
    Guild = get(bot.guilds, name = GUILD)

    for Role in Guild.roles:
        if Role.name == RoleHeigherarchy[0]:
            CITIZENRY = Role

    jsonData = getJSONFile()
    TH = Guild.get_channel(int(jsonData['channels']['throne-room']))
    AN = Guild.get_channel(int(jsonData['channels']['announcements']))
    AB = Guild.get_channel(int(jsonData['channels']['admin-bots']))
    SS = Guild.get_channel(int(jsonData['channels']['stats']))
    SR = Guild.get_channel(int(jsonData['channels']['rules']))
    importantChannels = dict(throneroom=TH,announcements=AN,adminbots=AB,serverstats=SS,serverrules=SR)

    #Update the loops that run in the background with no user input
    if jsonData['throne-room']['active'] == 'True':
        """ThroneRoomLoop.change_interval(seconds = TimeLeft)"""
        ThroneRoomActive = True
        ThroneRoomLoop.start(True,jsonData['throne-room']['time-left'])
    else:
        ThroneRoomActive = False
    StatusChangeLoop.start()
    await UpdateThroneRoomFile()
    #serverStats.start()

#Change statuses of the bot:
@tasks.loop(hours = 5)
async def StatusChangeLoop():
    Options = ["I spent way too much time on this","I should get a life","Why do I do all the grunt work?","Pedro for president 2024!",\
                "Minecraft","Can I earn money doing this?","Earth is fine, people are dumb",\
                "Everyone should be able to do one card trick, tell two jokes, and recite three poems, in case they are ever trapped in an elevator",\
                "Bruh","When a bird hits your window have you ever wondered if God is playing angry birds with you?",\
                "When I’m on my death bed, I want my final words to be “I left one million dollars in the…",\
                "My study period = 15 minutes. My break time = 3 hours","Never make eye contact while eating a banana",\
                "C.L.A.S.S- come late and start sleeping","My biggest concern in life is actually how my online friends can be informed of my death!",\
                "How do you know what it’s like to be stupid if you’ve never been smart?","I hate fake people. You know what I’m talking about. Mannequins.",\
                "Everything is 10x funnier when you are not supposed to laugh.","It may look like I’m deep in thought, but 99% of the time I’m just thinking about what food to eat later.",\
                "\"Focusing\" on school work","That awkward moment when you realize that dora, who is 5, has more freedom than you.",\
                "That awkward when your eyes assumed “moment” was written after \"awkward\"","Never gonna let you down","Never gonna run around",\
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ","I lost the game","Dont forget to like and subscribe!","Imagine putting in effort",\
                "I put the most effort into these quotes","If you have more status ideas, DM helaugheth#5815","Psst, is anyone watching these?",\
                "There are 10 types of people, those who understand binary and those who dont","I should focus on college homework","There are 13 lines of quotes for me to choose from.",\
                "Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn","#SupportC'thulu","#LearnParsletoung","I'm adding these during class","lol",\
                "XD","Bro this releaves so much boredom","Shoot, I should do homework","College classes are BORING","All around me are familiar faces...",\
                "What is this...\"Fish showcommands\" thing?","Yar dar dar and a hody hody do","https://www.youtube.com/watch?v=Q04Lkw91Gts"]

    Status = random.choice(Options)
    await bot.change_presence(activity = discord.Game(name = Status))

#updates the Throne room file with information about it
@tasks.loop(hours = 1)
async def UpdateThroneRoomFile(new_m_data = None):
    if ThroneRoomActive:
        CurrentTime = int(datetime.now().timestamp())
        if ThroneRoomLoop.next_iteration != None:
            LoopTime = int(ThroneRoomLoop.next_iteration.timestamp())
            TimeLeft = str(LoopTime - CurrentTime)
        else:
            TimeLeft = 'None'
            LoopTime = 'None'
    else:
        TimeLeft = 'None'
        LoopTime = 'None'
    jsonData = getJSONFile()
        
    jsonData['throne-room']['active'] = str(ThroneRoomActive)
    jsonData['throne-room']['time-left'] = str(TimeLeft)
    if new_m_data != None:
        jsonData['throne-room']['messages'].append(new_m_data)
    writeJSONFile(jsonData)

#Main throne room loop:
@tasks.loop(hours = 196)
async def ThroneRoomLoop(RebootedUp,timeLeft=None):
    global ThroneRoomActive
    Active = False

    """
    RebootedUp - Server was rebooted while the throne room was running. Just needs to make sure perms are given and make an anouncement to admins
    """
    if RebootedUp:
        await importantChannels['throneroom'].set_permissions(CITIZENRY, view_channel = True)
        await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Server restarted, resuming the "+importantChannels['throneroom'].mention+" loop. Citizenry has been given access. No announcements made."))
        Active = True
        timeLeft = datetime.fromtimestamp(int(timeLeft))
        t = (datetime.now()-timeLeft).total_seconds()
        ThroneRoomLoop.change_interval(seconds=t)
    else:
        Active = True
        if ThroneRoomLoop.current_loop == 0:
            Active = True
        elif (ThroneRoomLoop.current_loop % 2) == 0:
            Active = True
        else:
            Active = False
                
        if Active:
            await importantChannels['throneroom'].purge()
            await importantChannels['throneroom'].set_permissions(CITIZENRY, view_channel = True)
            temp = ""
            temp2 = ""
            for role in Guild.roles:
                if role.name == RoleHeigherarchy[1]:
                    temp = role.mention
                elif role.name == RoleHeigherarchy2[1]:
                    temp2 == role.mention
                    break
            await importantChannels['throneroom'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("Use the command `Fish title` to automatically request the rank higher than you are currently at. You must have the"+temp+"/"+temp2+"rank to request higher ranks. You can use `Fish Title help` to get more help.")))
            Temp = await importantChannels['announcements'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=(importantChannels['throneroom'].mention + " is now open all yall!")))
            await Temp.delete(delay = 346500)
        else:
            await importantChannels['throneroom'].set_permissions(CITIZENRY, view_channel = False)
            Temp = await importantChannels['announcements'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("I just closed the "+importantChannels['throneroom'].mention+" so voting will be held and results will be announced somewhat soon, depends on how active members are.")))
            Temp.delete(delay=30000)
            for member in  Guild.members:
                Cleared = False #Citizenry check
                Cleared2 = True #Check so that they do NOT have Good Lad/Lady
                for role in member.roles:
                    if role.name == RoleHeigherarchy[0]:
                        Cleared = True
                    if role.name == RoleHeigherarchy[1] or role.name == RoleHeigherarchy2[1]:
                        Cleared2 = False
                                    
                if Cleared and Cleared2:
                    for i in Guild.roles:
                        if i.name == RoleHeigherarchy[0]:
                            lad = i
                        elif i.name == RoleHeigherarchy2[0]:
                            lady = i
                            break
                    Message = await importantChannels['throneroom'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("Grant " + member.mention + " the "+lad.mention+"/"+lady.mention+" role?")))
                    UpdateThroneRoomFile({"messageID":str(Message.id),"role":str(CITIZENRY.id),'discordID':str(Message.author.id)})

            jsonData = getJSONFile()
            for i in jsonData['throne-room']['messages']:
                message = await importantChannels['throneroom'].fetch_message(int(i['messageID']))
                await message.add_reaction("👍")
                await message.add_reaction("👎")

    ThroneRoomActive = Active

#Update server stats for people to be able to see
#@tasks.loop(minutes=5)
async def serverStats():
    jsonData = getJSONFile()
    main_message = None
    secondary_message = None
    if type(jsonData['stats']['main']['messageID']) == type('temp'):
        main_message = await importantChannels['serverstats'].fetch_message(int(jsonData['stats']['main']['messageID']))
    if type(jsonData['stats']['secondary']['messageID']) == type('temp'):
        secondary_message = await importantChannels['serverstats'].fetch_message(int(jsonData['stats']['secondary']['messageID']))

    secondary_event = jsonData['stats']['secondary']['event']
    main_event = jsonData['stats']['main']['event']
    await statUpdate(jsonData['RCON']['main']['mainport'],True,'main',main_event,main_message)
    await statUpdate(jsonData['RCON']['secondary']['mainport'],True,'secondary',secondary_event,secondary_message)

@bot.command(help='Duke level command')
@commands.has_any_role(*DukeCheck)
async def removelink(ctx):
    ToDelete = []
    await ctx.message.delete()
    ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Ping the discord user to force an unlink, *or* you can just slap the minecraft username in")))
    try:
        response = await bot.wait_for("message",check=lambda i: i.author == ctx.message.author,timeout=60)
        ToDelete.append(response)
    except asyncio.TimeoutError:
        ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
    else:
        jsonData = getJSONFile()
        discordUsed = False
        if len(response.raw_mentions) > 0:
            discordUsed = True
        found = False
        for i in jsonData['registry']:
            if discordUsed:
                if response.raw_mentions[0] == int(i['discordID']):
                    soup = bs4(requests.get("https://mcuuid.net/?q="+str(i['uuid'])).text,features="html.parser")
                    username = soup.find("input",attrs={"id":"results_username"})["value"]
                    user=Guild.get_member(response.raw_mentions[0])
                    ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=(user.mention+' is linked to '+username+\
                        '. Please confirm admin unlinkage and that the requestor has correctly inputted their username [yes/no] THIS CANNOT BE UNDONE'))))
                found = True
                break
            else:
                soup = bs4(requests.get("https://mcuuid.net/?q="+str(response.content)).text,features="html.parser")
                username=response.content
                user=Guild.get_member(int(i['discordID']))
                ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=(response.content+' is linked to '+user.mention+\
                        '. Please confirm admin unlinkage and that the requestor has correctly inputted their username [yes/no] THIS CANNOT BE UNDONE'))))
                found = True
                break
        if not found:
            if not discordUsed:
                ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description='I couldn\'t find anyone linked up that Minecraft account, try again using the Discord ping mate')))
            else:
                ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description='I couldn\'t find anyone linked up that Discord account, try again using the Minecraft username mate')))
        else:
            try:
                response2 = await bot.wait_for("message",check=lambda i: i.author == ctx.message.author,timeout=60)
                ToDelete.append(response)
            except asyncio.TimeoutError:
                ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
            else:
                if response2.content.lower() == 'yes' or response2.content.lower() == 'y':
                    jsonData['registry'].remove(i)
                    writeJSONFile(jsonData)
                    await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=(str(ctx.message.author.mention)+' has forcefully removed the link between '+user.mention+' and '+username)))
                    textData = opCommand('whitelist remove '+username, user, 'main')  
                    textData += '    ' + opCommand('whitelist remove '+username, user, 'secondary')
                    jsonData.remove(i)
                    writeJSONFile(jsonData) 
                    await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description='\u200b'+textData))
                
                elif response2.content.lower() == 'no' or response2.content.lower() == 'n':
                    ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description='Right-o then')))
                else:
                    ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=random.choice(BADCOMMANDR))))
    """for i in ToDelete:
        await i.delete(delay = 30)"""

@bot.command(help='Regent level command')
@commands.has_any_role(*RegentCheck)
async def errors(ctx):
    file = discord.File(fp='./ERRORS.log', filename="ERRORS.log")
    await importantChannels['adminbots'].send(file=file)

#help= says it all. They must have the Good Lad role to do this though
@bot.command(help = "Request 1 title higher than you currently have.")
@commands.has_any_role(*GoodLadCheck)
async def title(ctx):
    Message = ctx.message
    await Message.delete()
    ToDelete = []
    jsonData = getJSONFile()
    for i in jsonData['throne-room']['messages']:
        if int(i['discordID']) == Message.author.id:
            m = await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description='Hey now mate...You already requested a title, can\' be requesting two now can you. How would that be fair eh?'))
            await m.delete(delay=30)
            return

    if ctx.channel == importantChannels['throneroom'] and ThroneRoomActive:
        User = Message.author
        RoleChosen = False
        TitleList = Guild.roles
        RequestedTitle = 'TEMP'
        CurrentTitle = 'TEMP'

        for role in User.roles:
            if role.name == RoleHeigherarchy[1]:
                CurrentTitle = {"Role":role,"Rank":1,"H":1}
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
            elif role.name == RoleHeigherarchy[6]:
                CurrentTitle = {"Role":role,"Rank":6,"H":1}
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
                    ToDelete.append(await ctx.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="That title is granted by the King (*cough cough* favoratism *cough cough*")))
                    RoleChosen = False

                elif CurrentTitle["Rank"] == 5:
                    ToDelete.append(await ctx.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="When the King ~~dies~~ leaves you are given his title. So dont get too ambitious or he might take special notice of that...")))
                    RoleChosen = False

                elif CurrentTitle["Rank"] == 6:
                    ToDelete.append(await ctx.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="You're already top of the ship mate. You cant request any higher. I mean you could by adding higher roles but then I'd start calling you an Egyptian or something")))
        
            if RoleChosen:
                if Title.name == RequestedTitle:
                    NewMessage = await ctx.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=User.mention + " Requests the title of: " + str(Title.name)))
                    await UpdateThroneRoomFile({"messageID":str(NewMessage.id),"role":str(Title.id),'discordID':str(Message.author.id)})
    else:
        ToDelete.append(await ctx.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Incorrect channel. Message has been deleted. Please only use this command in the"+importantChannels['throneroom'].mention)))

    for i in ToDelete:
        await i.delete(delay=10)

#Run a minecraft command from discord
@bot.command(help = "Regent level command")
@commands.has_any_role(*RegentCheck)
async def mccommand(ctx):
    await ctx.message.delete()
    ToDelete = []
    ToDelete.append(await ctx.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Enter the command to run on the server").set_footer(text="THIS WILL BE RAN WITH OP PRIVLAGES - DO NOT USE THE `/` I ADD IT")))
    try:
        response = await bot.wait_for("message",check=lambda i: i.author == ctx.message.author,timeout=90)
        ToDelete.append(response)
    except Exception as E:
        await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("ERROR RUNNING A MC-COMMAND. ERROR: "+str(E))))
    else:
        if response.content.startswith('/'):
            ToDelete.append(await ctx.send(embed = discord.Embed(color=discord.Color.dark_gold(),description='HEY! I said no inputting the `/` I will take care of it...I gotchu this time...Try not to in the future, I know it\'s weird though')))
            response.content = response.content[1:]

        server = await serverCheck(ctx)
        if server != 'FAIL':
            
            textData = opCommand(response.content, ctx.message.author, server)
            embed = discord.Embed(color=discord.Color.dark_gold())
            embed.add_field(name='Data returned',value=('\u200b'+textData))
            ToDelete.append(await importantChannels['adminbots'].send(embed=embed))
            await importantChannels['adminbots'].send(embed=discord.Embed(color=discord.Color.dark_gold(),description=(str(ctx.message.author)+' ran the command: '+str(response.content)+' @ '+str(time.asctime()))))

    for i in ToDelete:
        await i.delete(delay=20)    

#The throne room loop
@bot.command(help = "Regent level command")
@commands.has_any_role(*RegentCheck)
async def loop(ctx, arg):
    global ThroneRoomActive
    await ctx.message.delete()
    ToDelete = []
    if arg == "start":
        if ThroneRoomLoop.is_running():
            if  ThroneRoomActive:
                ToDelete.append(await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("The "+importantChannels['throneroom'].mention+" loop is already running. "+importantChannels['throneroom'].mention+" is currently open and will close on: " + str(ThroneRoomLoop.next_iteration)))))
            else:
                ToDelete.append(await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("The "+importantChannels['throneroom'].mention+" loop is already running. "+importantChannels['throneroom'].mention+" is currently closed and will open on: " + str(ThroneRoomLoop.next_iteration)))))
        else:
            ToDelete.append(await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("The "+importantChannels['throneroom'].mention+" loop has been started"))))
            await ThroneRoomLoop.start(False)

    elif arg == "stop":
        if not ThroneRoomLoop.is_running():
            ToDelete.append(await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("The "+importantChannels['throneroom'].mention+" loop is not running."))))
        else:
            ToDelete.append(await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("The "+importantChannels['throneroom'].mention+" loop has been stopped."))))
            ToDelete.append(await importantChannels['announcements'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=(importantChannels['throneroom'].mention + " has closed. Voting will be held and results will be announced soon."))))
            ThroneRoomLoop.cancel()
            await importantChannels['throneroom'].set_permissions(CITIZENRY, view_channel = False)
            for member in  Guild.members:
                Cleared = False #Citizenry check
                Cleared2 = True #Check so that they do NOT have Good Lad/Lady
                for role in member.roles:
                    if role.name == RoleHeigherarchy[0]:
                        Cleared = True
                    if role.name == RoleHeigherarchy[1] or role.name == RoleHeigherarchy2[1]:
                        Cleared2 = False
                                    
                if Cleared and Cleared2:
                    for i in Guild.roles:
                        print(i.name,RoleHeigherarchy[0],RoleHeigherarchy2[0])
                        if i.name == RoleHeigherarchy[0]:
                            lad = i
                        elif i.name == RoleHeigherarchy2[0]:
                            lady = i
                            break
                    Message = await importantChannels['throneroom'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("Grant " + member.mention + " the "+lad.mention+"/"+lady.mention+" role?")))
                    await UpdateThroneRoomFile({"messageID":str(Message.id),"role":str(CITIZENRY.id),'discordID':str(Message.author.id)})

            jsonData = getJSONFile()
            
            for i in jsonData['throne-room']['messages']:
                message = await importantChannels['throneroom'].fetch_message(i['messageID'])
                await message.add_reaction("👍")
                await message.add_reaction("👎")

    elif arg == "status":
        if not ThroneRoomLoop.is_running():
            ToDelete.append(await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=("The "+importantChannels['throneroom'].mention+" loop is not running at the moment"))))
        else:
            ToDelete.append(await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description=(importantChannels['throneroom'].mention+" is currently running status will change in: " + str(ThroneRoomLoop.next_iteration)))))

    elif arg == "help":
        Help = discord.Embed(color=discord.Color.dark_gold())
        Help.add_field(name = "BOT PREFIX", value = "Fish")
        Help.add_field(name = "Loop Commands", value = "`start` | `stop` | `status`")
        Help.add_field(name = "start", value = "Starts the throne room loop EX: `Fish loop start`")
        Help.add_field(name = "stop", value = "Stops the throne room loop EX: `Fish loop stop`")
        Help.add_field(name = "status", value = "Check the status of the Throne Room. EX: `Fish loop status`")
        ToDelete.append(await ctx.send(embed = Help))

    for i in ToDelete:
        await i.delete(delay=20) 

#Display the ServerFile
@bot.command(help = "Regent level command")
@commands.has_any_role(*RegentCheck)
async def serverfile(ctx):
    await ctx.message.delete()

    server = await serverCheck()
    if server == 'FAIL':
        return
    jsonData = getJSONFile()

    with open(jsonData['serverfiles'][server]['properties']) as F:
        ServerFile = F.readlines()
    Book=[]
    Sheet = []
    title=""
    data=""
    await importantChannels['adminbots'].trigger_typing()
    for Place, line in enumerate(ServerFile):
        for i, letter in enumerate(line):
            if letter == "=":
                title = line[:i]
                if line[i+1:] == "\n":
                    data = "NO DATA"
                    break
                else:
                    data = line[i+1:len(line)-1]
                    break

        if Place % 9 == 0 and Place != 0:
            if Place == 9:
                Sheet.pop(0)
                Sheet.pop(0)
            Book.append(Sheet)
            Sheet = []
        else:
            Sheet.append({"title":title,"data":data})
    Page = 0
    Forward = "⏩"
    Back = "⏪"

    EmbedData = discord.Embed(color=discord.Color.dark_gold())
    for i in Book[Page]:
        EmbedData.add_field(name = i["title"],value = '\u200b'+i["data"])

    file = discord.File(fp=jsonData['serverfiles'][server]['properties'], filename="server.propterties")
    await importantChannels['adminbots'].send(file=file)

    Message = await importantChannels['adminbots'].send(embed=EmbedData)

    while True:
        EmbedData = discord.Embed(color=discord.Color.dark_gold())
        for i in Book[Page]:
            EmbedData.add_field(name = i["title"],value = '\u200b'+i["data"])
        EmbedData.set_footer(text = "The whitelist option MUST be done through commands in-game. Spigot has an issue where it will dump the contents of the whitelist file when it's edited manually. No idea why it does so. Further details can be located at: https://minecraft.gamepedia.com/Server.properties")

        await Message.edit(embed=EmbedData)

        left = Page != 0
        right = Page != len(Book) - 1

        if left:
            await Message.add_reaction(Back)
        if right:
            await Message.add_reaction(Forward)
        try:
            Reaction = await bot.wait_for("reaction_add",check = ReactionCheck(Message,left,right),timeout=200)
        except asyncio.TimeoutError:
            await Message.delete()
            return
        else:
            if str(Reaction[0]) == Back:
                Page -= 1
                await Message.remove_reaction(emoji=Back,member=ctx.message.author)
                if Page == 0:
                    await Message.remove_reaction(emoji=Back,member=bot.user)
            elif str(Reaction[0]) == Forward:
                Page += 1
                await Message.remove_reaction(emoji=Forward,member=ctx.message.author)
                if Page == len(Book) - 1:
                    await Message.remove_reaction(emoji=Forward,member=bot.user)

#Show default commands available to everyone below a Count
@bot.command(help = "Shows available commands")
async def showcommands(ctx):
    Help = discord.Embed(color=discord.Color.dark_gold())
    Help.add_field(name = "COMMANDS", value = "`title` | `link` | `userinfo`",inline=False)
    Help.add_field(name = "title", value = "Only available when the Throne Room is available and if you have the Good Lad/Lady Title. EX: `Fish title`",inline=False)
    Help.add_field(name = "link", value = "Link your discord account to your minecraft account. EX: `Fish link` then follow the prompts",inline=False)
    Help.add_field(name = "unlink", value = "UnLink the minecraft account linked to your discord account. EX: `Fish unlink` then follow prompts",inline=False)
    Help.add_field(name = "userinfo", value = "Show skin and name history of a player and what discord account they're linked to. EX: `Fish userinfo` then follow the prompts",inline=False)
    #Help.add_field(name = "prank", value = "Allows those who have linked their discord and minecraft accounts to prank each other. EX: `Fish prank` then follow the prompts",inline=False)
    Help.set_footer(text="BOT PREFIX: `Fish`")
    i = await ctx.send(embed = Help)
    await i.delete(delay=60)

#Clear a bunch of messages from a channel
@bot.command(help = "Count/Countess level command")
@commands.has_any_role(*CountCheck)
async def clear(ctx,arg):
    if arg == "help":
        await ctx.message.delete()
        await ctx.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Clear an amount of messages from a channel. `EX: Fish clear 6`"))
    else:
        await ctx.channel.purge(limit=int(arg) + 1)

#Link minecraft and discord accounts
@bot.command(help="Link discord to minecraft account")
async def link(ctx):
    ToDelete=[]
    await ctx.message.delete()
    jsonData = getJSONFile()
    for i in jsonData['registry']:
        if i['discordID'] == str(ctx.message.author.id):
            soup = bs4(requests.get("https://mcuuid.net/?q="+str(i['uuid'])).text,features="html.parser")
            username = soup.find("input",attrs={"id":"results_username"})["value"]
            temp = await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Mate, you're already linked to a minecraft account... You're linked to an account with the name: "+username+'. You can unlink accounts by running the command `unlink` and following further prompts'))
            await temp.delete(delay=30)
            return

    #ToDelete.append(await ctx.channel.send("You input your minecraft username and then I can link it to your discord account so then it will be updated frequently and other users can check who minecraft users are if they dont know who it is on discord. It also helps with keeping the player registry up to date, this replaces it actually."))
    ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Input your username here and I'll begin the linking process:")))
    try:
        response = await bot.wait_for("message",check=lambda i: i.author == ctx.message.author,timeout=60)
        ToDelete.append(response)
    except asyncio.TimeoutError:
        ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
    else:
        details = discord.Embed(color=discord.Color.dark_gold())
        soup = bs4(requests.get("https://mcuuid.net/?q="+str(response.content)).text,features="html.parser")
        Username = soup.find("input",attrs={"id":"results_username"})["value"]
        uuid = soup.find("input",attrs={"id":"results_id"})["value"]
        Skin = soup.find("img",attrs={"id":"results_avatar_body"})["src"]
        Face = soup.find("img",attrs={"class":"results_avatar mx-auto"})["src"]
        details.set_thumbnail(url=Face)
        details.set_image(url=Skin)
        details.add_field(name="Username",value='\u200b'+Username,inline=False)
        details.set_footer(text="Please confirm if this is you [yes/no]")
        ToDelete.append(await ctx.channel.send(embed = details))
        try:
            response = await bot.wait_for("message", check = lambda i: i.author == ctx.message.author,timeout=60)
            ToDelete.append(response)
        except asyncio.TimeoutError:
            ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
        else:
            found = False
            if response.content.lower() == "no":
                ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Right-o then")))
            elif response.content.lower() == "yes":
                jsonData = getJSONFile()
                for i in jsonData['registry']:
                    if i['uuid'] == uuid:
                        found = True
                        if i['discordID'] != str(ctx.message.author.id):
                            await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Hey now...That minecraft account {Username: "+Username+"} is already linked to someone...You cant be doing that now. It's linked to: "+Guild.get_member(int(i['discordID'])).mention),header=(Guild.get_member(ctx.message.author.id)+" tried to link to a already existing account"))
                            break 
                        else:
                            ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="You must have a bad memory my guy. You're already linked to that account so you already did that...I guess good job?")))
                            break
                    elif i['discordID'] == str(ctx.message.author.id):
                        found = True
                        soup = bs4(requests.get("https://mcuuid.net/?q="+str(i['uuid'])).text,features="html.parser")
                        Username = soup.find("input",attrs={"id":"results_username"})["value"]
                        ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Mate, you're already linked to a minecraft account... You're linked to an account with the name: "+Username)))
                        break
                    if i == jsonData['registry'][-1]:
                        found = True
                        jsonData['registry'].append({'uuid':uuid,'discordID':str(ctx.message.author.id)})
                        writeJSONFile(jsonData)

                        ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Accounts linked. Good job mate. You've earned a donut")))
                        with open('./donut.png', 'rb') as f:
                            donut = discord.File(f,"./donut.png")
                        await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=(str(ctx.message.author.mention)+' has linked his discord to the mincraft account: '+str())))
                        ToDelete.append(await ctx.channel.send(file=donut))

                        textData = opCommand(('whitelist add '+Username),ctx.message.author,'main')
                        temp = opCommand(('whitelist add '+Username),ctx.message.author,'secondary')
                        textData += '   ' +temp
                        await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description='\u200b'+textData))
                        break

                if not found:
                    jsonData['registry'].append({'uuid':uuid,'discordID':str(ctx.message.author.id)})
                    writeJSONFile(jsonData)
                    
                    ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Accounts linked. Good job mate. You've earned a donut")))
                    with open('./donut.png', 'rb') as f:
                        donut = discord.File(f,"donut.png")
                    ToDelete.append(await ctx.channel.send(file=donut))
                    await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=(str(ctx.message.author.mention)+' has linked his discord to the mincraft account: '+str(Username))))

                    textData = opCommand(('whitelist add '+Username),ctx.message.author,'main')
                    temp = opCommand(('whitelist add '+Username),ctx.message.author,'secondary')
                    textData += '   ' +temp
                    await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description='\u200b'+textData))
                
            else:
                ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="My guy, that aint the responce I was looking for...Try again from the beginning. A simple yes/no will do")))
    for i in ToDelete:
        await i.delete(delay=30)

#Unlink minecraft and discord accounts
@bot.command(help="Unlink discord and minecraft account")
async def unlink(ctx):
    ToDelete=[]
    await ctx.message.delete()
    found = False
    jsonData = getJSONFile()
    for i in jsonData['registry']:
        if i['discordID'] == str(ctx.message.author.id):
            found = True
            details = discord.Embed(color=discord.Color.dark_gold())
            soup = bs4(requests.get("https://mcuuid.net/?q="+str(i['uuid'])).text,features="html.parser")
            Username = soup.find("input",attrs={"id":"results_username"})["value"]
            Skin = soup.find("img",attrs={"id":"results_avatar_body"})["src"]
            Face = soup.find("img",attrs={"class":"results_avatar mx-auto"})["src"]
            details.set_thumbnail(url=Face)
            details.set_image(url=Skin)
            details.add_field(name="Username",value='\u200b'+Username,inline=False)
            details.set_footer(text="This is the account you're linked to. Confirm unlinkage? [yes/no]")
            ToDelete.append(await ctx.channel.send(embed = details))
            try:
                response = await bot.wait_for("message",check=lambda i: i.author == ctx.message.author,timeout=60)
                ToDelete.append(response)
            except asyncio.TimeoutError:
                ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
            else:
                if response.content.lower() == "yes":
                    ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description="Deleting account linkage I s'pose")))

                    textData = opCommand(('whitelist remove '+Username),ctx.message.author,'main')
                    temp = opCommand(('whitelist remove '+Username),ctx.message.author,'secondary')
                    textData += '   ' +temp

                    jsonData['registry'].remove(i)
                    writeJSONFile(jsonData)
                    
                    await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description='\u200b'+textData))
                elif response.content.lower() == "no":
                    ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description="Right-o then"))) 
                else:
                    ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="My guy, that aint the responce I was looking for...Try again from the beginning")))
            
    if not found:
        ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description="You aint linked to an account yet mate. You gotta link before you can unlink...No donut for you")))

    for i in ToDelete:
        await i.delete(delay=15)

#Display low level info about a user
@bot.command(help="Queury the registry database for information about a specific player")
async def userinfo(ctx):
    ToDelete = []
    await ctx.message.delete()
    options = discord.Embed(color=discord.Color.dark_gold(),description="Enter a minecraft username to get some information about who that Minecraft account is linked to here on Discord. Just enter the username")
    ToDelete.append(await ctx.channel.send(embed=options))
    try:
        response = await bot.wait_for("message",check = lambda i: i.author == ctx.message.author,timeout=60)
        ToDelete.append(response)
    except asyncio.TimeoutError:
        ToDelete.append(await ctx.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
    else:
        try:
            soup = bs4(requests.get("https://mcuuid.net/?q="+str(response.content)).content,features="html.parser")
            details = discord.Embed(color=discord.Color.dark_gold())
            Username = soup.find("input",attrs={"id":"results_username"})["value"]
            uuid = soup.find("input",attrs={"id":"results_id"})["value"]
            Skin = soup.find("img",attrs={"id":"results_avatar_body"})["src"]
            Face = soup.find("img",attrs={"class":"results_avatar mx-auto"})["src"]
            details.set_thumbnail(url=Face)
            details.set_image(url=Skin)
            details.add_field(name="Minecraft Username",value='\u200b'+Username,inline=False)
            #details.add_field(name="Username",value=Username,inline=False)
            jsonData = getJSONFile()
            for i in jsonData['registry']:
                if i['uuid'] == str(uuid):
                    DiscordUser = Guild.get_member(int(i['discordID']))
                    details.add_field(name="Discord Account:",value='\u200b'+DiscordUser.mention,inline=False)
                    break

            ToDelete.append(await ctx.channel.send(embed = details))
            for i in ToDelete:
                await i.delete(delay=10)

        except Exception as E:
            i = await ctx.channel.send(embed=discord.Embed(colord=discord.Color.dark_gold(),description="There was an error finding that user, they most likely have not linked their accounts yet."))
            await i.delete(delay=10)

#Display the registry of the server       
@bot.command(help="Duke/Duchess level command")
@commands.has_any_role(*DukeCheck)
async def registry(ctx):
    await ctx.message.delete()
    jsonData = getJSONFile()

    details = discord.Embed(color=discord.Color.dark_gold(),title="Registry of the server")
    page = []
    book = []

    for i in jsonData['registry']:
        soup = bs4(requests.get("https://mcuuid.net/?q="+str(i['uuid'])).content,features="html.parser")
        mcName = soup.find("input",attrs={"id":"results_username"})["value"]
        disName = Guild.get_member(int(i['discordID'])).mention
        if len(page) % 9 == 0 and len(page) != 0:
            book.append(page)
            page = []
        else:
            page.append({"header":mcName,"value":disName})

    if len(book) == 0:
        book.append(page)

    Page = 0
    Forward = "⏩"
    Back = "⏪" 

    for i in book[Page]:
        details.add_field(name = i["header"],value = '\u200b'+i["value"])
    details.set_footer(text = "Run `Fish userinfo` to get extended details about a user. A Admin version of that command will be made eventually but I honestly am tired of tweaking this and it not working so who knows anymore")

    Message = await ctx.channel.send(embed=details)
    while True:
        EmbedData = discord.Embed(color=discord.Color.dark_gold())
        for i in book[Page]:
            EmbedData.add_field(name = i["header"],value = '\u200b'+i["value"])
        EmbedData.set_footer(text = "Run `Fish userinfo [username]` to get extended details about a user. A Admin version of that command will be made eventually but I honestly am tired of tweaking this and it not working so who knows anymore")

        await Message.edit(embed=EmbedData)

        left = Page != 0
        right = Page != len(book) - 1

        if left:
            await Message.add_reaction(Back)
        if right:
            await Message.add_reaction(Forward)
        try:
            Reaction = await bot.wait_for("reaction_add",check = ReactionCheck(Message,left,right),timeout=200)
        except asyncio.TimeoutError:
            await Message.delete()
            return
        else:
            if str(Reaction[0]) == Back:
                Page -= 1
                await Message.remove_reaction(emoji=Back,member=ctx.message.author)
                if Page == 0:
                    await Message.remove_reaction(emoji=Back,member=bot.user)
            elif str(Reaction[0]) == Forward:
                Page += 1
                await Message.remove_reaction(emoji=Forward,member=ctx.message.author)
                if Page == len(book) - 1:
                    await Message.remove_reaction(emoji=Forward,member=bot.user)

#Admin help
@bot.command(help = "Duke/Duchess level command")
@commands.has_any_role(*CountCheck)
async def adminhelp(ctx):
    Help = discord.Embed(color=discord.Color.dark_gold())
    Help.add_field(name = "BOT PREFIX", value = "Fish")
    Help.add_field(name = "FURTHER HELP", value = "Run the command with `help` after to get help. EX: `Fish clear help` - NOT FULLY IMPLIMENTED YET")
    Help.add_field(name = "loop", value = "Has 3 sub-commands: Restart, Start and Stop. They will each do that to the Throne Room loop. EX: Fish loop start/stop/restart")
    Help.add_field(name = "clear", value = "Will clear an amount of messages from a given channel if you have the correct rank. EX: `Fish clear 23`")
    Help.add_field(name = "serverfile", value = "List the properties of the *server.properties* file the Minecraft server is using. EX: `Fish serverfile`")
    Help.add_field(name = "mccommand", value = "Run a minecraft command from here in discord. Will be run with OP. EX: `Fish mccommand` then follow the prompts")
    Help.add_field(name = 'prunecheck',value = 'Check what users would have roles revoked if I were to prune them')
    Help.add_field(name = 'errors',value='Posts the Error logs from the bot')
    await ctx.channel.send(embed = Help)

@bot.command(help='Regent level command')
@commands.has_any_role(*RegentCheck)
async def changechannel(ctx):
    global importantChannels
    ToDelete = []
    await ctx.message.delete()
    embed = discord.Embed(color=discord.Color.dark_gold(),title='Which channel function are we working on today eh mate?')
    embed.add_field(name='1',value='Admin bots')
    embed.add_field(name='2',value='Throne room')
    embed.add_field(name='3',value='Announcements')
    embed.add_field(name='4',value='Server stats')
    embed.add_field(name='5',value='Server rules')
    embed.description='Just type out the number. I\'ll getcha more instructions ;)'
    embedMessage = await ctx.channel.send(embed=embed)
    ToDelete.append(embedMessage)
    try:
        update = await bot.wait_for('message',check=lambda i: i.author==ctx.message.author,timeout=60)
    except asyncio.TimeoutError:
        ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
    else:
        await update.delete()
        if int(update.content) == 1:
            embed = discord.Embed(color=discord.Color.dark_gold(),description=('Mention the channel to replace '+importantChannels['adminbots'].mention+' with'))
        elif int(update.content) == 2:
            embed = discord.Embed(color=discord.Color.dark_gold(),description=('Mention the channel to replace '+importantChannels['throneroom'].mention+' with'))
        elif int(update.content) == 3:
            embed = discord.Embed(color=discord.Color.dark_gold(),description=('Mention the channel to replace '+importantChannels['announcements'].mention+' with'))
        elif int(update.content) == 4:
            embed = discord.Embed(color=discord.Color.dark_gold(),description=('Mention the channel to replace '+importantChannels['serverstats'].mention+' with'))
        elif int(update.content) == 5:
            embed = discord.Embed(color=discord.Color.dark_gold(),description=('Mention the channel to replace '+importantChannels['serverrules'].mention+' with'))

        await embedMessage.edit(embed=embed)
        try:
            newChannel = await bot.wait_for('message',check=lambda i: i.author==ctx.message.author,timeout=60)
            ToDelete.append(newChannel)
        except asyncio.TimeoutError:
            ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
            return
        else:
            jsonData = getJSONFile()
            if update.content == '1':
                importantChannels['adminbots'] = Guild.get_channel(newChannel.raw_channel_mentions[0])
                jsonData['channels']['admin-bots'] = importantChannels['adminbots'].id
                ToDelete.append(await importantChannels['adminbots'].send(embed=discord.Embed(color=discord.Color.dark_gold(),description='New channel')))
            elif update.content == '2':
                importantChannels['throneroom'] = Guild.get_channel(newChannel.raw_channel_mentions[0])
                jsonData['channels']['throne-room'] = importantChannels['throneroom'].id
                ToDelete.append(await importantChannels['throneroom'].send(embed=discord.Embed(color=discord.Color.dark_gold(),description='New channel')))
            elif update.content == '3':
                importantChannels['announcements'] = Guild.get_channel(newChannel.raw_channel_mentions[0])
                jsonData['channels']['admin-bots'] = importantChannels['adminbots'].id
                ToDelete.append(await importantChannels['announcements'].send(embed=discord.Embed(color=discord.Color.dark_gold(),description='New channel')))
            elif update.content == '4':
                importantChannels['serverstats'] = Guild.get_channel(newChannel.raw_channel_mentions[0])
                jsonData['channels']['stats'] = importantChannels['stats'].id
                ToDelete.append(await importantChannels['serverstats'].send(embed=discord.Embed(color=discord.Color.dark_gold(),description='New channel')))
            elif update.content == '5':
                importantChannels['serverrules'] = Guild.get_channel(newChannel.raw_channel_mentions[0])
                jsonData['channels']['rules'] = importantChannels['serverrules'].id
                ToDelete.append(await importantChannels['serverrules'].send(embed=discord.Embed(color=discord.Color.dark_gold(),description='New channel')))
            writeJSONFile(jsonData)
            ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description='It has been done. Good job, you got past 3 steps in the process, 2 role checks, and 30 lines of code to get this done')))
    
    for i in ToDelete:
        await i.delete(delay=20)

@bot.command(help='Prank minecraft players')
async def prank(ctx):
    def linkCheck(User):
        jsonData = getJSONFile()
        for i in jsonData['registry']:
            if i['discordID'] == User.id:
                return True
        return False
    
    server = await serverCheck(ctx)
    jsonData = getJSONFile()
    if server == 'main':
        p = jsonData['RCON']['main']['mainport']
    else:
        p = jsonData['RCON']['secondary']['mainport']
    ping = mctools.PINGClient(host=jsonData['RCON']['ip'],port=int(p))
    stats = ping.get_stats()
    pList = ''
    try:
        for index,i in enumerate(stats['players']['sample']):
            if index < len(stats['players']['sample'])-1:
                temp = i[0].replace('\x1b','')
                temp = temp.replace('[0m','')
                
                pList += (temp+', ')
            else:
                temp = i[0].replace('\x1b','')
                temp = temp.replace('[0m','')
                pList += (temp)
    except Exception as E:
        pList='No one online...Sorry'

    ToDelete=[]
    if linkCheck(ctx.message.author):
        await ctx.message.delete()
        commands = ['execute at PLAYER run playsound entity.creeper.primed master PLAYER ~ ~ ~ 1',\
                    'execute at PLAYER run playsound entity.enderman.scream master PLAYER ~ ~ ~ 1',\
                    'execute at PLAYER run particle minecraft:elder_guardian'] 
          
        temp = discord.Embed(color=discord.Color.dark_gold(),description='Give me the minecraft username of who you would like to prank')
        temp.set_footer(text=('Available players: '+pList))
        ToDelete.append(await ctx.channel.send(embed=temp))

        try:
            prankee = await bot.wait_for('message',check = lambda i: i.author == ctx.message.author,timeout=60)
            ToDelete.append(prankee)
        except asyncio.TimeoutError:
            ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
        else:
            options = discord.Embed(color=discord.Color.dark_gold(),title=('Please respond with the according number to what you would like to do to '+prankee.content))
            options.add_field(name='1',value='Create a hissing creeper sound at the player')
            options.add_field(name='2',value='Create a Enderman scream sound at the player')
            options.add_field(name='3',value='Create the visual effect of an Elder Guardian cursing the player')
            options.set_footer(text='[1/2/3] is what you should put in the chat')
            ToDelete.append(await ctx.channel.send(embed = options))
            try:
                toRun = await bot.wait_for('message',check = lambda i: i.author == ctx.message.author,timeout=60)
                ToDelete.append(toRun)
            except asyncio.TimeoutError:
                ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
            else:
                c = commands[int(toRun.content)].replace('PLAYER',str(prankee.content))
                textData = opCommand(c,ctx.message.author,server)

                embed = discord.Embed(color=discord.Color.dark_gold())
                embed.add_field(name='Server response',value=('\u200b'+textData))
                embed.set_footer(text='If no value given, the player was either not online or you misspelled their username')
                ToDelete.append(await ctx.channel.send(embed=embed))
    else:
        ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description='Mate...You gotta link your accounts before you can prank other players...`Fish link` is the command for that')))

    for i in ToDelete:
        await i.delete(delay=15)

@bot.command(help='Duke/Duchess level command')
@commands.has_any_role(*DukeCheck)
async def event(ctx):
    ToDelete=[]
    await ctx.message.delete()
    server = await serverCheck(ctx)
    ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description='Please give me the message to list as the upcoming event for the server')))
    try:
        event = await bot.wait_for("message",check=lambda i: i.author == ctx.message.author,timeout=60)
        ToDelete.append(event)
    except asyncio.TimeoutError:
        ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=random.choice(TIMEOUTR))))
    else:
        jsonData = getJSONFile()
        if server == 'main':
            jsonData['stats']['main']['event'] = event.content
        elif server == 'server':
            jsonData['stats']['secondary']['event'] = event.content
        writeJSONFile(jsonData)
        
        ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description='It is done...Farewhell. The event will show up soonish, the message updates every few minutes')))

    for i in ToDelete:
        await i.delete(delay=15)

@bot.command(help='Regent level command')
@commands.has_any_role(*RegentCheck)
async def prunecheck(ctx):
    await ctx.message.delete()
    ToDelete = []
    temp=discord.Embed(color=discord.Color.dark_gold(),description='How long should I check back in the databases?')
    temp.set_footer(text='You need to put a integer or I\'ll be sad')
    temp=await ctx.channel.send(embed=temp)
    ToDelete.append(temp)
    response = (await bot.wait_for('message',check=lambda i: i.author == ctx.message.author,timeout=60))
    ToDelete.append(response)
    days=int(response.content)
    prunedInt = str(await Guild.estimate_pruned_members(days=30,roles=Guild.roles))
    ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description='Amount of innactive members in the last '+str(days)+' days: '+prunedInt)))
    ToDelete.append(await ctx.channel.send('https://tenor.com/view/hacker-sombra-overwatch-hacking-gif-7952445'))
    memberList = []
    for i in Guild.members:
        ID = i.id
        found = False
        for channel in Guild.text_channels:
            for message in await channel.history().flatten():
                if message.author.id == ID and int(message.created_at.strftime('%s')) > int(time.time() - days*24*60*60):
                    memberList.append(i)
                    found = not found
                    break
            if found:
                break
    
    purgedMembers = ''
    for i in Guild.members:
        if i not in memberList:
            purgedMembers += str(i.mention)+' '

    embed = discord.Embed(color=discord.Color.dark_gold(),title='Users that would be effected by removing all heigherachical roles',description=purgedMembers)
    await ctx.channel.send(embed=embed)

    for i in ToDelete:
        await i.delete(delay = 20)
    
#Just for voting in the throne room
async def on_raw_reaction_add(payload):
    """def RoleGetter(Member,RoleNeeded):
        Cleared = False
        for role in Member.roles:
            if role.name == RoleNeeded:
                Cleared = True
            elif role.name == RoleHeigherarchy[6]:
                Cleared = True
        return Cleared"""

    User = Guild.get_member(payload.member.id)
    if (payload.channel_id == importantChannels['throneroom'].id):
        jsonData = getJSONFile()
        for i in jsonData['throne-room']['messages']:
            message = await importantChannels['throneroom'].fetch_message(i['messageID'])
            requestedMale = message.mentions[0]
            requestedFemale = message.mentions[0]
            if not (requestedMale in User.roles or requestedFemale in User.roles):
                await message.remove_reaction(payload.emoji,payload.member)

#Respond to "E" 
@bot.listen("on_message")
async def Responder(message):
    if message.content == "E":  
        Message2 = await message.channel.send(embed = discord.Embed(color=discord.Color.dark_gold(),description="Oh?"))
        await message.delete(delay = 5)
        await Message2.delete(delay = 5)
    if bot.user.mentioned_in(message):
        await message.channel.send('https://tenor.com/view/summoned-gif-21949657')
    for i in message.author.roles:
        if i.name == RoleHeigherarchy[-1]:
            temp = await message.channel.send('https://tenor.com/view/roger-that-copy-that-yes-sir-yes-maam-ok-gif-18243692')
            await temp.delete(delay=5)
            break

@bot.event
async def on_member_remove(member):
    jsonData = getJSONFile()
    for i in jsonData['registry']:
        if i['discordID'] == member.id:
            soup = bs4(requests.get("https://mcuuid.net/?q="+str(i['uuid'])),features="html.parser")
            Username = soup.find("input",attrs={"id":"results_username"})["value"]
            textData = opCommand('whitelist remove '+Username, member, 'main')  
            textData += '    ' + opCommand('whitelist remove '+Username, member, 'secondary')
            jsonData.remove(i)
            writeJSONFile(jsonData) 
            await importantChannels['adminbots'].send(embed = discord.Embed(color=discord.Color.dark_gold(),description='\u200b'+textData))

@bot.event
async def on_member_join(member):
    sysChannel = Guild.system_channel
    await sysChannel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=(str(member.mention) + ' Please read the ' + importantChannels['serverrules'].mention + ' and a member of the Duchy will be with you soon to get you your roles and verify with you you read the ' + importantChannels['serverrules'].mention)))
    for role in Guild.roles:
        if role.name == RoleHeigherarchy[3]:
            r1 = role
        elif role.name == RoleHeigherarchy2[3]:
            r2 = role
    await importantChannels['adminbots'].send(text=(str(member.mention)+' is in need of roles and whatnot that I have been told I cant do ~~* cough cough * Vasco * cough cough *~~. Please see to it '+str(r1.mention)+'/'+str(r2.mention)))

#Handle errors
"""@bot.event
async def on_command_error(ctx, error):
    ToDelete = [ctx.message]
    if isinstance(error, discord.ext.commands.CommandNotFound):
        ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=random.choice(BADCOMMANDR))))
    elif isinstance(error,discord.ext.commands.errors.CommandOnCooldown):
        choices = ['My guy, try slowing your yee haws down for a minute','Holdup there cowboy, that\'s on a there cooldown','I dont know bout you, but I think you\'re running that command too often',\
            'Just...Just stop that...You\'re too fast there mate']
        ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=random.choice(choices))))
    elif isinstance(error,discord.ext.commands.MissingAnyRole):
        choices=['Hey there cowboy...You dont have access to that command','Dont go tryin that now, you might catch attention of the big bad mods',\
            'I see you dont have your papers...No access for you kiddo','INTRUDER - INTRUDER - INTRUDER - THEY DONT HAVE THE ROLES NEEDED','Come back when you have the correct role for that']
        ToDelete.append(await ctx.channel.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=random.choice(choices))))
    elif isinstance(error,discord.ext.commands.NoPrivateMessage):
        choices = ['I told you to STTTOOOOOPPPPP running commands through DMs!','No you','I lost the game',\
            'I\'m normally never going to let you down, but this time I\'m going to have to give you up','Tryin to bypass the system I see','Go away']
        await ctx.author.send(embed=discord.Embed(color=discord.Color.dark_gold(),description=random.choice(choices)))
        logger.info(str(ctx.author)+' is DMing me this: '+str(ctx.message.content))
    else:
        await importantChannels['adminbots'].send(embed=discord.Embed(color=discord.Color.dark_gold(),description='Error found. Check the ERRORS.log file'))
        logger.error(error)
    for i in ToDelete:
        await i.delete(delay=30)"""

bot.run(TOKEN)
