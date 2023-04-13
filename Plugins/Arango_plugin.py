from dotenv import load_dotenv
import os
import time 
from arango import ArangoClient
from utils.functions_file import make_valid_key,extract_from_sting 


load_dotenv()

'''api_key_id = os.getenv("ARANGO_API_KEY_ID")
secret_key = os.getenv("ARANGO_API_SECRET_KEY")
HOST = "https://e1d9e4e87c7e.arangodb.cloud:8529"'''
password = os.getenv("ARANGO_PASS2")

# Set up the client with your API key

import base64

'''encodedCA = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMrakNDQWVLZ0F3SUJBZ0lSQU5WbkJBNG04MGFac0tXVnhtRVZCZXd3RFFZSktvWklodmNOQVFFTEJRQXcKSmpFUk1BOEdBMVVFQ2hNSVFYSmhibWR2UkVJeEVUQVBCZ05WQkFNVENFRnlZVzVuYjBSQ01CNFhEVEl3TVRFeQpPREUxTURBeU5Wb1hEVEkxTVRFeU56RTFNREF5TlZvd0pqRVJNQThHQTFVRUNoTUlRWEpoYm1kdlJFSXhFVEFQCkJnTlZCQU1UQ0VGeVlXNW5iMFJDTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUEKemFRS2JwWnh5SWFMK0YyV1BzU3ZlWStCMlNDVzlPbXpacFMzUmk5a1N3VTUzeWJYeUd4RHRLcXhWZytzTFZIUwo5MzlXSlpDenRNUkFQeCtWRUN3aEF3VEhLNmsvUlJJOTFzMkFnb2ExYUNDS1dhMm9KKzFVSmYyRzZaL01iVzVhCjBVblRzZ250Ukt2T3k1N1l1dFUrRm51V3FuN3plYklNWXFjWVpWWEppcUtBZkw0emhMSEFnN3FlMFFzalo0eVQKVFZSS1N5a0cvdjdOY2EzVmoxNWpqbXJQYWhybjBSZkVaWnJjN1F0K2JPVDhsM3dpdUk0NFJjQ0RTTnRFSzlweAphTjRSOU1LWW45YnNWSDJsQlFuclVBZTMxeXZOb0xSM3pFcnFMZVE2WXZBcHllblorV09ScFEyZXpveFA5eW84ClVsMm9vWkgwRHRYSmttN0hhV1BaYXdJREFRQUJveU13SVRBT0JnTlZIUThCQWY4RUJBTUNBcVF3RHdZRFZSMFQKQVFIL0JBVXdBd0VCL3pBTkJna3Foa2lHOXcwQkFRc0ZBQU9DQVFFQXhSOWw2NURZemhkeXE2R2NOd094cGR1UwpZRm44clRWeHpPRlRsRHVyNmgyaHR3emVNVG5YYzRqRmptR2ttS1Jha3dqUWVaN0owRDBwbm54WnBHK2VLN1d0ClVvNEdoMXFYVlNDcDlOdzhrWnRNZ0JGbnB1TmFHVGlDZUZraVMzWk14R2trTUpUYUtqbjBtSGgvbDYxUWZZWW4KOEZTMTFMZHQ3SE5DOGlHQXNWTWtDL0JJQk5pQ29XM0E1WUJtcmROVVVyeVBzdGJQdTZnN3dSOEhrM1RCbmlubAptcWJUMHd5bXVJNkx3YjdlbGF4Z2dIWWlPamg3OXpUaWZJUWEvZjBjRTJFSnBFMkROWGRCbHB3c1dXMTdsOUtDCmVTOVVoYUI1MkFSN2VaU25oaXlsVjFLUkxCeTBZa3RJQ1ZvNzZHckJZZE5Ma1ZseEdGZ3ByRVpQQTdVSWt3PT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo="
try:
    file_content = base64.b64decode(encodedCA)
    with open("cert_file.crt", "w+") as f:
        f.write(file_content.decode("utf-8"))
except Exception as e:
    print(str(e))
    exit(1)'''

client = ArangoClient(
    hosts="https://8002ef9dab5a.arangodb.cloud:18529", verify_override="cert_file.crt"
)

db = client.db("stigflow", username="shahar", password=password)

# Note that ArangoGraph Insights Platform runs deployments in a cluster configuration.
# To achieve the best possible availability, your client application has to handle
# connection failures by retrying operations if needed.
print("ArangoDB is on")

#testing permissions
doc = {"identifier":str(time.time())}
db.collection("testing").insert(doc)


#Calculate message score by all or single emoji, and single role. message_id = int/str, role = str, guild = valid str, eomoji ="emoji"
def intersect_logic(lists):
    inter = set(lists[0])
    for l in lists[1:]:
        inter = inter & set(l)
    return list(inter)

async def calculate_message_emoji_role_score(message_key,role,emoji,guild):
    by_role = count_makers_by_roles(message_key=message_key,role=role,guild=guild)
    by_emoji = count_makers_by_emoji(message_key=message_key,emoji=emoji)
    print(f"{'intersection is '}{intersect_logic([by_emoji,by_role])}")
    return intersect_logic([by_emoji,by_role])




    
        
def count_makers_by_roles(message_key,role,guild):
    print(f"{'argumets, message_key='}{message_key},{'role='}{role},{'guild='}{guild}")
    aql = "WITH messages, makers FOR v,e,p IN 1..1 INBOUND @message_id reactionEdges FILTER INTERSECTION(@role,v.Discord_roles."+make_valid_key(guild)+") RETURN DISTINCT v._key"
    bind_vars={
            
            "message_id":"messages/"+str(message_key),
            #"guild":make_valid_key(guild),
            "role":role
            }
    print(bind_vars)
    print(aql)
    #try:
    id_list_roles = list(db.aql.execute(aql,bind_vars=bind_vars))
    print(f"{'got  the list '}{id_list_roles}")
    return id_list_roles
    #except:
        #print("bad input")
        #return "bad input"
    
        
def count_makers_by_emoji(message_key,emoji):
    if emoji == 'all':
        print(f"{'emoji == '}{'all'}")
        aql = "WITH makers,messages FOR v,e,p IN 1..1 INBOUND @message_id reactionEdges RETURN DISTINCT v._key"
        bind_vars={
            "message_id":'messages/'+str(message_key),
            }
        print(bind_vars)
        print(aql)
        try:
       
            results = list(db.aql.execute(aql,bind_vars=bind_vars))
            print(results)

            print(f"{'id list is '}{results}")
            return results
        except:
            return "bad input"
        
    else: 
        print(f"{'emoji == '}{emoji}")
        aql = "WITH makers,messages FOR v,e,p IN 1..1 INBOUND @message_id reactionEdges FILTER e.Emoji == @emoji RETURN v._key"
        bind_vars={
                "emoji":emoji,
                "message_id":'messages/'+str(message_key),
                #guild":make_valid_key(guild),
                #"role":role
                }
        print(bind_vars)
        print(aql)
        try:
        
            results = list(db.aql.execute(aql,bind_vars=bind_vars))
            print(results)

            print(f"{'id list is '}{results}")
            return results
        except:
            return "bad input"
        




"""#Calculate message score by all or single emoji, and single role. message_id = int/str, role = str, guild = valid str, eomoji ="emoji"
async def claculate_message_score_by_role(message_id,role,guild,emoji):
    print(f"{'caculating role score of message '}{message_id}")
    if emoji == "all":
        print("emoji == all")
        aql = "WITH makers FOR v,e,p IN 1..1 INBOUND @message_id reactionEdges FILTER INTERSECTION(@role,v.Discord_roles."+make_valid_key(guild)+") RETURN DISTINCT v"
        bind_vars={
                   
                   "message_id":"messages/"+str(message_id),
                   #"guild":make_valid_key(guild),
                   "role":role
                   }
        print(bind_vars)
        print(aql)
        try:
            score = len(list(db.aql.execute(aql,bind_vars=bind_vars)))
            print(f"{'score is '}{score}")
        except:
            print("bad input")
            return "bad input"
        else:
            return score
    else:
        print(f"{'emoji == '}{emoji}")
        aql = "WITH makers,messages FOR v,e,p IN 1..1 INBOUND @message_id reactionEdges FILTER e.Emoji == @emoji RETURN v"
        bind_vars={
                   "emoji":emoji,
                   "message_id":'messages/'+str(message_id),
                   #guild":make_valid_key(guild),
                   #"role":role
                   }
        print(bind_vars)
        print(aql)
        try:
            #score = len(list(db.aql.execute(aql,bind_vars=bind_vars)))
            #tests
            results = list(db.aql.execute(aql,bind_vars=bind_vars))
            print(results)

            print(f"{'score is '}{score}")
        except:
            return "bad input"
        else:
            return score
"""
#a function that calculates the score of a message based on a defined group of makers _id's, a defiened array of emojies.
def calculate_message_emoji_group_score(emojis,group,message_id:str):
    if emojis == "all":
        aql = "FOR v,e,p IN 1..1 INBOUND @message_id reactionEdges FILTER v._id IN @group RETURN DISTINCT v"
        try:
            score = len(list(db.aql.execute(aql,bind_vars={"group":group,"message_id":message_id})))
        except:
            return "bad input"
        else:
            return score
    else:
        aql = "FOR v,e,p IN 1..1 INBOUND @message_id reactionEdges FILTER e.emoji IN @emojis AND v._id IN @group RETURN DISTINCT v"
        try:
            score = len(list(db.aql.execute(aql,bind_vars={"group":group,"emojis":emojis,"message_id":message_id})))
        except:
            return "bad input"
        else:
            return score
        
#fech convo thread
async def fetch_convo(message_key):
    aql = "FOR v,e,p IN 1..100 ANY @message refEdges FILTER e.Type == 'Reply' RETURN DISTINCT v"
    query = db.aql.execute(aql,bind_vars={"message":'messages/'+str(message_key)})
    result = [ doc for doc in query]
    for doc in result:
        print(doc)
        print("")
    print("still here")

#fetch amswer and qeuistion, the answer id is the input and the question is the reference.
async def fetch_Q_and_A(message_key):
    print("in fetch_Q_and_A")
    try:
        print(f"feaching answer")
        answer = await fetch_message_arango(str(message_key))
        print(answer)
    except:
        print(f"{'could not find message '}{message_key}{' in arango'}")
        return {}
    else: 
        print(f"feaching qustion")
        question = await fetch_message_arango(answer["Reference"])
        print(question)
        return {"Q":question,"A":answer}
    


#Return the number of reactions per message in aragno
async def get_arango_reaction_count(message_id):
    aql = "FOR v,e,p IN 1..1 INBOUND @message_id reactionEdges RETURN e"
    count = len(list(db.aql.execute(aql,bind_vars={"message_id",message_id})))
    return count

    
        
#Functions to handle discord events
#Define upsert function, must specify a non empty update
def upsert(col:str,search:dict,doc:dict,update:dict):
    aql = "UPSERT @search INSERT @doc UPDATE @update IN "+col+" RETURN {new: NEW, old: OLD}"
    query = db.aql.execute(aql,bind_vars={"search":search,"doc":doc,"update":update})
    result = query.next()
    return result

#Upsert Author
def upsert_maker(maker):
    upsert("makers",{"_key":make_valid_key(maker["Discord_handle"])},maker,maker)
"""maker needs to have the discord handle key"""
#Upsert reaction
def upsert_reaction(reaction):
    upsert_maker(reaction["Maker_doc"])
    reactionEdges = db.collection("reactionEdges")
    reactionEdges.insert({"_from":"makers/"+make_valid_key(reaction["Maker_doc"]["Discord_handle"]),"_to":"messages/"+str(reaction["Message_ID"]),"Emoji":reaction["Emoji"]})
    if "Guild" in reaction.keys():
        edge = {"_key":make_valid_key(reaction["Guild"])+"_"+make_valid_key(reaction["Maker_doc"]["Discord_handle"]),"_from":"servers/"+make_valid_key(reaction["Guild"]),"_to":"makers/"+make_valid_key(reaction["Maker_doc"]["Discord_handle"])}
        upsert("membership",{"_key":make_valid_key(reaction["Guild"])+"_"+make_valid_key(reaction["Maker_doc"]["Discord_handle"])},edge,edge)
    #test
    #print(result)
    #m = reactionEdges.get(myedge["_id"])
    #print(m)
"""for now reaction event needs to have the keys: maker, Message ID,maker doc, Emoji, can have Guild"""

#delete reaction where the attributes shoud be (_from,_to,_Emoji) raction is a dictionary of an a reaction event
def remove_reaction(reaction):
    col = db.collection("reactionEdges")
    aql = '''
    FOR edge in reactionEdges
    FILTER edge._from == @from
        AND edge._to == @to
        AND edge.Emoji == @emoji
    RETURN edge._id
    '''
    #creating the right parameters for the aql querry from a reaction event object
    search = {"from":"makers/"+make_valid_key(reaction["Maker_doc"]["Discord_handle"]),"to":"messages/"+str(reaction["Message_ID"]),"emoji":reaction["Emoji"]}
    result = db.aql.execute(aql,bind_vars=search)
    try:
        edge_id = result.next()
        col.delete(edge_id)
        print(edge_id)
        print("has been deleted")
    except:
        print(" No reaction to delete - query result is empty ")



    
#Check if a message is in a collection by discord message id
def id_in_collection(id,collection):
    try:
        col = db.collection(collection)
    except:
        print("bad input")
    else:
        return collection+"/"+str(id) in col   
    

#add new message
def upsert_message(message):
    message["arango_time"]=time.time()
    message["_key"]=str(message["Message_ID"])
    result = upsert("messages",{"_key":str(message["Message_ID"])},message,message)
    Author={"_key":make_valid_key(message["Author"]),"Discord_handle":message["Author"],"Discord_roles":message["Discord_roles"]}
    upsert_maker(Author)
    if not result["old"]: 
        #Between author and message
        refEdges = db.collection("refEdges")
        refEdges.insert({"_from":"makers/"+make_valid_key(message["Author"]),"_to":"messages/"+str(message["Message_ID"]),"creation_time":message["Authorship"],"edgeType":"Authership"})
       
        #Between Guild and Author
        if "Guild" in message.keys():
            edge = {"_key":make_valid_key(message["Guild"])+"_"+make_valid_key(message["Author"]),"_from":"servers/"+make_valid_key(message["Guild"]),"_to":"makers/"+make_valid_key(message["Author"])}
            upsert("membership",{"_key":make_valid_key(message["Guild"])+"_"+make_valid_key(message["Author"])},edge,edge)
    if "Extracted_URL" in message.keys():
        for u in message["Extracted_URL"]:
            result2 = upsert("urls",{"URL":u},{"URL":u,"creation_time":message["Authorship"]},{"URL":u})
            # if result[old] is empty then the url is new and we need to add the edge
            if not result2["old"]: 
                refEdges = db.collection("refEdges")
                refEdges.insert({"_from":"messages/"+str(message["Message_ID"]),"_to":"urls/"+result2["new"]["_key"],"creation_time":message["Authorship"],"Type":"Reference"})
        
    
    #If the message is a reply to another message then we add a refEdge outbound from the reply
    if message["Reference"]:
        ref_key = str(message["Reference"])
        
        upsert("refEdges",{"_key":str(message["Message_ID"])+"_to_"+ref_key},{"_key":str(message["Message_ID"])+"_to_"+ref_key,"_from":"messages/"+str(message["Message_ID"]),"_to":"messages/"+ref_key,"Type":"Reply"},{"up":"date"})
        print("arango incerted reference")
    print(f"{'arango_plugin upserted message '}{message['Message_ID']}")  

    #upsert mentions (If ment)
    try: 
        message["mentions"]
        mentions = message["mentions"]
        for maker in mentions:
            edge = {
                "_key":str(message["Message_ID"])+"to"+make_valid_key(maker),
                "_from":"messages/"+str(message["Message_ID"]),
                "_to":"makers/"+make_valid_key(maker),
                "type":"mention"
            }  
            upsert("refEdges",{"_key":edge["_key"]},edge,{"type":"mentions"})
    except: 
        print("no mentions")
    #testing to see message build in action
    """try: 
        result2
    except:
        print("No URL")
    else:
        aql = "FOR v,e,p IN 3..3 INBOUND @url refEdges,membership RETURN p"
        r = db.aql.execute(aql,bind_vars={"url":result2["new"]["_id"]})
        print(list(r))"""

#checks if a doc/edge with a certain key is in a collection. make sure you feed it with strings
def key_in_collection(key,collection):
    col = db.collection(collection)
    return col.get(key) 

#fetches a message doc from messages collection by message_id which it's str is the key in the collection           
async def fetch_message_arango(key):
    print(" In fetch_message_arango")
    messages = db.collection("messages")
    message = messages.get("messages/"+str(key))
    return message

#retrive all active flows (thouse with "status" = 1) from the StigFlows collection
async def get_active_flows():
    col = db.collection("StigFlows")
    flows = []
    for doc in col:
        if doc["Status"] == 1:
            flows.append(doc)
    return flows
"""emoji = '📘'
aql = "FOR e IN reactionEdges FILTER e.Emoji == @emoji RETURN e"
results = db.aql.execute(aql,bind_vars={"emoji":emoji})

for doc in results:
    print(doc)"""
def upsert_flow(key:str,reactions:list,threshold:int,guild:str,roles:list,action:str,status:int):
    flow = {
        "_key":make_valid_key(str(key)),
        "reactions":reactions,
        "threshold":threshold,
        "group":{
        "Guild":make_valid_key(guild),
        "roles":roles
        },
        "action":action,
        "Status":status

    }
    
    upsert(
        col = "StigFlows", search = {"_key":flow["_key"]}, doc = flow, update = flow 
    )

"""upsert_flow(
    key="notion_tweets",reactions=['🐦'],threshold=2,guild="Common Sense [makers]",roles=["Maker"],status=0,action='N_T'
)"""


