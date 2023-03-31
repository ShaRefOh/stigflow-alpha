#Test, listen to Discord and stuff
import os
import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv
from Plugins.Arango_plugin import upsert_reaction, upsert_message, key_in_collection, fetch_message_arango, remove_reaction, get_active_flows, calculate_message_emoji_role_score, fetch_Q_and_A
import re
from utils.functions_file import isoformat, make_valid_key
from Plugins.Airtable_plugin import airtable_stig_delete_record,airtable_stig_upsert
from Plugins.Notion_plugin import NotionIntegration
#import subprocess

"""# SSH command to create a background SSH connection
ssh_command = 'ssh -L 8529:localhost:8529 -p 2223 brad@95.175.123.125 -i ~/etc/secrets/id_ed15519_meta'


# Run the SSH command in the background
ssh_process = subprocess.Popen(ssh_command, shell=True)    """

# Load environment variables
load_dotenv()

# Set up Discord bot
intents = discord.Intents.all()
client = commands.Bot(command_prefix='./', intents=intents)


#Prepere Notion
try:
    Notion_plugin = NotionIntegration()
except:
    Exception("Notion API request timed out")

print("here")


#indicates the bot is ready
@client.event
async def on_ready():
    print(f'Bot named {client.user} is listening for discord messages...')

#listen to messages
@client.event
async def on_message(payload):

    print("on_message detected a new message: ")
    print(payload.id)

    #building a message dict that will be maped into the database
    message = await build_message_object(payload)
   
    #Upsert to arango
    upsert_message(message)
    print("on_message upserted the message: ")
    print(message["Message_ID"])

    #check if the message satisfies a flow's logic
    await StigLogic(message,"on_message")


#listen to new assigned reactions
@ client.event
async def on_raw_reaction_add(payload):
    
    #get maker prophile
    guild = await client.fetch_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)
    
    role_names = []
    for role in payload.member.roles:
        role_names.append(role.name)

    maker = {
    "Discord_roles" : {make_valid_key(guild.name):role_names},
    "Discord_handle" : str(member),
    "_key" : make_valid_key(str(member)),
    "discord_user_id": payload.user_id
    }
    
    reaction={

    "Maker_doc" : maker,

    "Message_ID" : payload.message_id,
    }

    if payload.emoji.is_custom_emoji():
        reaction["Emoji"] =  payload.emoji
    else:
        reaction["Emoji"] =  payload.emoji.name
        
    #reaction["maker"] = payload.member.name + "#" + payload.member.discriminator

    reaction["Guild"] = payload.member.guild.name
    #print(reaction)
    
    #here I need to add the function key_in_collection to check if if we need to add it to arango in an if statment
    if key_in_collection(str(reaction["Message_ID"]),"messages"):
        print("Message assosiated with the reaction exist")
    else:
        channel = await client.fetch_channel(payload.channel_id)
        raw_message = await channel.fetch_message(payload.message_id)
        message = await build_message_object(raw_message)
        upsert_message(message)

        
    #Also need to change the format of the message and get the old reactions and users
    #Seems to work, need to test
    upsert_reaction(reaction)
    print(reaction)
    await StigLogic(payload,'on_reaction')


@client.event
async def on_raw_reaction_remove(payload):
   
   guild = await client.fetch_guild(payload.guild_id)
   member = await guild.fetch_member(payload.user_id)
   role_names = []
   for role in member.roles:
        role_names.append(role.name)

   maker = {
    "Discord_roles" : {make_valid_key(guild.name):role_names},
    "Discord_handle" : str(member),
    "_key" : make_valid_key(str(member)),
    "discord_user_id": payload.user_id
    }
    
   reaction={

    "Maker_doc" : maker,

    "Message_ID" : payload.message_id,
    }

   

   if payload.emoji.is_custom_emoji():
        reaction["Emoji"] =  payload.emoji
   else:
        reaction["Emoji"] =  payload.emoji.name
        
   reaction["maker"] = str(member)

   reaction["Guild"] = guild.name
   print("we are on reaction remove")
   print(reaction)

   remove_reaction(reaction)
   await StigLogic(payload,'on_reaction')


@client.event
async def on_raw_message_edit(payload):
    channel = await client.fetch_channel(payload.channel_id)
    raw_message = await channel.fetch_message(payload.message_id)
    message = await build_message_object(raw_message)
    message_id = message["Message_ID"]
    if key_in_collection(str(message_id),"messages"):
        print("Message assosiated with the edit exist")
        old_message = await fetch_message_arango(message_id)
        message["Original_saved_on " + str(old_message["saved_at"])] = old_message["Message_content"]

    else:
        print("Not in arango")
        channel = await client.fetch_channel(payload.channel_id)
        raw_message = await channel.fetch_message(payload.message_id)
        message = await build_message_object(raw_message)
        
    #an improvment here will be to add new attribute for each edite, we can use date or somthing.
    print(message)
    upsert_message(message)
#if __name__ == '__main__':

#Functions:

async def get_message_type_channel_and_ref(message):
    """ Evaluates the message.channel to see whether a message is a Message, Reply, or Forum and sets the appropriate channel information

    Input: Discord Message object
    Output:
    - message_type: Message, Forum, or Reply
    - message_channel: The channel the message or thread is in
    - message_thread_title: If the message is in a thread (Forum or Reply), the title is the first message's text (Message) or title (Forum)
    """
    message_type = ''
    if str(message.channel.type) == "text":
        print(f"{'message'},{message.id},{' is in text channel'}")
        
        if message.reference:
            message_type = "Reply"
            reference = message.reference.message_id
            print("The message is a reply to")
            print(reference)
            if not key_in_collection(str(reference),"messages"):
                print("refered message was not found in arango")
                channel = message.channel
                raw_ref = await channel.fetch_message(reference)
                parent_message = await build_message_object(raw_ref)
                upsert_message(parent_message)
                print("refered message inserted to arango")
                print(parent_message)
            else:
                print("refered message was found in arrango")
        else: 
            message_type = "Message"
            reference = ""
            print("No ref")
        message_channel = message.channel.name
        message_thread_title = ''

    elif str(message.channel.type) == "public_thread":


        print(f"{'message in '}{message.channel.type}")

        """ Forum post is starting message of the thread.

        Reply is in response to TextChannel, which starts the Thread
        """

        if message.reference:
                message_type = "Reply"
                reference = message.reference.message_id
                print("The message is a reply to")
                print(reference)
                if not key_in_collection(str(reference),"messages"):
                    print("refered message was not found in arango")
                    channel = message.channel
                    raw_ref = await channel.fetch_message(reference)
                    parent_message = await build_message_object(raw_ref)
                    upsert_message(parent_message)
                    print("refered message inserted to arango")
                    print(parent_message)
                else:
                    print("refered message was found in arrango")
        
        
        elif message.channel.id == message.id:
            message_type = "Post"
            print("message is a post")
            reference = ""

        elif str(message.channel.parent.type) == "forum":
            channel_id = message.channel.id
            message_type = "In thread"
            reference = ""
            print("No ref found")
            print("message is in a forum post thread")
            reference = channel_id 

            
        else:
            channel_id = message.channel.id
            print("message is in a thread")
            message_type = "In thread"
            reference = channel_id
            print(reference)
            
            if not key_in_collection(str(reference),"messages"):
                    
                    print(f"{'refered message ' }{channel_id}{' is not in arango'}")

                    channel = message.channel.parent
                    m = await channel.fetch_message(channel_id)
                    parent_message = await build_message_object(m)
                    print(f"{'refered message have been built-'}{parent_message['Message_ID']}")

                    upsert_message(parent_message)
                    print("refered message was upserted")
                    
                    print(parent_message)
            else:
                print("refered message found in arango")   
            
            
        message_channel = message.channel.parent.name
        message_thread_title =message.channel.name
    else:
        message_channel = message.channel.name
        message_thread_title = ''
        try:
            reference = message.reference.message_id
        except:
            reference = ''

    return message_type, message_channel, message_thread_title, reference


async def build_message_object(payload):
    """  Uses a payload to build all the message fields used throughout the DiscordMessage, TopMessage, and GardenMessage tables

    Inputs
    - payload: The Discord payload object from on_raw_reaction_add/remove
    - trigger_event: 'add' of 'remove'
    """
  
   
  
    extracted_urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+[^. ]', payload.content)
    #Can add to the next the forum tags
    message_type, message_channel, message_thread_title, reference = await get_message_type_channel_and_ref(payload)

    #return authors roles
    role_names = []
    for role in payload.author.roles:
        role_names.append(role.name)
        
    guild = payload.guild.name 
        

    message = {
        "Message_ID": payload.id,
        "Author": f"{payload.author.name}#{payload.author.discriminator}",
        "Authorship": isoformat(payload.created_at),
        "Channel" : message_channel,
        "Thread_Title":message_thread_title,
        "Message_content" : str(payload.content),
        #forum_tags=forum_tags,
        "Guild" : guild,
        #"Edited at" : payload.edited_at, 
        "Jump_URL":payload.jump_url,
        "Message_type":message_type,
        "saved_at":isoformat(datetime.datetime.now()),
        "Discord_roles": {make_valid_key(guild):role_names},
        "Reference" : reference,
        "discord_user_id" : payload.author.id     
    }
    #pulling user mentions (not role mentions yet)
    mentions = payload.mentions 
    # If there are, then we replace the string in the content of the message
    #which appear in the form of <@uesr.id> with name#discrominator
    if mentions:
        content = message["Message_content"]  
        ids = []    
        for member in mentions:
            m_id = member.id  
            content = content.replace(f"<@{m_id}>",str(member))
            #print(str(member))
            ids.append(str(member))
        message["Message_content"] = content
        message["mentions"] = ids
        print(f"{'mentions in message: '}{ids}")
    
    # and then it will be better to do it in get_message_type_and_channel function
    if message["Message_type"] == "Post":
        thread = await client.fetch_channel(payload.channel.id)
        message["Forum_tags"] =[]
        for tag in thread.applied_tags:
            message["Forum_tags"].append(tag.name)
        print(" a post! with tags ")
        print(message["Forum_tags"])
    


    
    #add urls only if there some, other wise we get empty url documents
    if extracted_urls:
        message["Extracted_URL"] = extracted_urls
    
    
    print(message)
    return message
#need to add credentials somewhere
#also while using out, I should only provide the id, out should fetch the message if needed
async def StigLogic(payload,event_type):
    flows = await get_active_flows()
    print(f"{'Checking Logic for '}")
    if event_type == "on_message":
        print(f"{'message event '}{payload['Message_ID']}")
        for flow in flows:
            if flow["threshold"] == 0:
                payload["StigFlow"] = flow["_key"]
                payload["Score"] = 0
                await out(flow["action"],payload,1)
            
    elif event_type == "on_reaction":
        print(f"{'reaction event with message '}{payload.message_id}")
        for flow in flows:
            #preper parameters for fo score calculation
            #group = await get_group_ids(flow)
            print(f"{'cheking logic for flow - '}{flow}")
            #calculate score
            try:
                print("trying to calculate score")
                result = await calculate_message_emoji_role_score(message_key=payload.message_id,role= flow["group"]["roles"],guild= flow["group"]["Guild"],emoji= str(flow['reactions'][0]))
                score = len(result)
                print(f"{'Score '}{score}{' was calculated'}")
                #check threashold
                if score>=flow['threshold']:
                    print("Threshold reached")
                    message = await fetch_message_arango(str(payload.message_id))
                    message["Score"] = score
                    message["StigFlow"] = flow["_key"]
                    print(f"{'message hase been fetched'}{message['Message_ID']}")

                    await out(flow["action"],message,1)
                else:
                    print("Threshold was not reached")
                    print(payload.message_id)
                    await out(flow["action"],payload.message_id,0)
            except:
                print('')



   
    
        
#need to add credentials somewhere            
async def out(action,payload,val):
    print('in out')
    if action == "N_K":
        if val:

            print(f"{'Upserting payload '}{payload['Message_ID']}{' to Notion!'}")
            Notion_plugin.upsert_notion_page(message=payload,flow_name=action,score=payload['Score'])
        else:
            print(f"{'Removing payload '}{payload}{' to Notion!'}")
            Notion_plugin.remove_notion_page(payload["Message_ID"])

            print("Removed entry from Notion")
    elif action == "A_K":
        if val:
            print(f"{'Upserting payload '}{payload['Message_ID']}{' to Airtable!'}")
            airtable_stig_upsert(payload)
        else:
            print(f"{'Removing payload '}{payload}{' From Airtable!'}")
            airtable_stig_delete_record(payload)

            print("Removed entry from Notion")
    elif action == "Q&A":
        if val:
            print(f"{'Fertching Q&A from arango '}")
            convo = await fetch_Q_and_A(payload['Message_ID'])
            if convo:
                print(f"{'Upserting Q&A '}{payload['Message_ID']}{' to Notion!'}")
                try:
                    Notion_plugin.upsert_notion_QandA(question = convo["Q"],answer=convo["A"],score=payload['Score'],flow_name=action)
                except:
                    Exception("Notion API request timed out")
            else:
                print(f"{'could not find the question '}")   


            
        else:
            print(f"{'Removing Q&A '}{payload}{' from Notion!'}")
            try:
                Notion_plugin.remove_notion_QA(payload)
            except:
                Exception("Notion API request timed out")
            print("Removed entry from Notion")
    else:
        print("action is not defined..")
    return payload

#fetch message by message id and channel id


client.run(os.getenv('DISCORD_BOT_TOKEN'))

