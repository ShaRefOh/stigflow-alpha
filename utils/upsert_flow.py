from dotenv import load_dotenv
import os
import time 
from arango import ArangoClient
from functions_file import make_valid_key,extract_from_sting 
from Plugins.Arango_plugin import upsert
#from test_ArangoClient import upsert


load_dotenv()

'''api_key_id = os.getenv("ARANGO_API_KEY_ID")
secret_key = os.getenv("ARANGO_API_SECRET_KEY")
HOST = "https://e1d9e4e87c7e.arangodb.cloud:8529"'''
password = os.getenv("ARANGO_PASS2")

# Set up the client with your API key

import base64

encodedCA = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMrakNDQWVLZ0F3SUJBZ0lSQU5WbkJBNG04MGFac0tXVnhtRVZCZXd3RFFZSktvWklodmNOQVFFTEJRQXcKSmpFUk1BOEdBMVVFQ2hNSVFYSmhibWR2UkVJeEVUQVBCZ05WQkFNVENFRnlZVzVuYjBSQ01CNFhEVEl3TVRFeQpPREUxTURBeU5Wb1hEVEkxTVRFeU56RTFNREF5TlZvd0pqRVJNQThHQTFVRUNoTUlRWEpoYm1kdlJFSXhFVEFQCkJnTlZCQU1UQ0VGeVlXNW5iMFJDTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUEKemFRS2JwWnh5SWFMK0YyV1BzU3ZlWStCMlNDVzlPbXpacFMzUmk5a1N3VTUzeWJYeUd4RHRLcXhWZytzTFZIUwo5MzlXSlpDenRNUkFQeCtWRUN3aEF3VEhLNmsvUlJJOTFzMkFnb2ExYUNDS1dhMm9KKzFVSmYyRzZaL01iVzVhCjBVblRzZ250Ukt2T3k1N1l1dFUrRm51V3FuN3plYklNWXFjWVpWWEppcUtBZkw0emhMSEFnN3FlMFFzalo0eVQKVFZSS1N5a0cvdjdOY2EzVmoxNWpqbXJQYWhybjBSZkVaWnJjN1F0K2JPVDhsM3dpdUk0NFJjQ0RTTnRFSzlweAphTjRSOU1LWW45YnNWSDJsQlFuclVBZTMxeXZOb0xSM3pFcnFMZVE2WXZBcHllblorV09ScFEyZXpveFA5eW84ClVsMm9vWkgwRHRYSmttN0hhV1BaYXdJREFRQUJveU13SVRBT0JnTlZIUThCQWY4RUJBTUNBcVF3RHdZRFZSMFQKQVFIL0JBVXdBd0VCL3pBTkJna3Foa2lHOXcwQkFRc0ZBQU9DQVFFQXhSOWw2NURZemhkeXE2R2NOd094cGR1UwpZRm44clRWeHpPRlRsRHVyNmgyaHR3emVNVG5YYzRqRmptR2ttS1Jha3dqUWVaN0owRDBwbm54WnBHK2VLN1d0ClVvNEdoMXFYVlNDcDlOdzhrWnRNZ0JGbnB1TmFHVGlDZUZraVMzWk14R2trTUpUYUtqbjBtSGgvbDYxUWZZWW4KOEZTMTFMZHQ3SE5DOGlHQXNWTWtDL0JJQk5pQ29XM0E1WUJtcmROVVVyeVBzdGJQdTZnN3dSOEhrM1RCbmlubAptcWJUMHd5bXVJNkx3YjdlbGF4Z2dIWWlPamg3OXpUaWZJUWEvZjBjRTJFSnBFMkROWGRCbHB3c1dXMTdsOUtDCmVTOVVoYUI1MkFSN2VaU25oaXlsVjFLUkxCeTBZa3RJQ1ZvNzZHckJZZE5Ma1ZseEdGZ3ByRVpQQTdVSWt3PT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo="
try:
    file_content = base64.b64decode(encodedCA)
    with open("cert_file.crt", "w+") as f:
        f.write(file_content.decode("utf-8"))
except Exception as e:
    print(str(e))
    exit(1)

client = ArangoClient(
    hosts="https://8002ef9dab5a.arangodb.cloud:18529", verify_override="cert_file.crt"
)

db = client.db("stigflow", username="shahar", password=password)

# Note that ArangoGraph Insights Platform runs deployments in a cluster configuration.
# To achieve the best possible availability, your client application has to handle
# connection failures by retrying operations if needed.
#print("ArangoDB:")


def upsert_flow(key:str,reactions:list,threshold:int,guild:str,roles:list,channel:str,action:str,status:int):
    flow = {
        "_key":make_valid_key(str(key)),
        "reactions":reactions,
        "threshold":threshold,
        "channel":channel,
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

upsert_flow(
    key="TestChannle",channel="bot-testing",reactions=['🔁'],threshold=2,guild="Common Sense [makers]",roles=['Maker'],status=1,action="R_T"
)
#A function that goes over all of the documents in the specified collection 'col'
# and renames a chossen field/attribute 'old_field' as 'new_field'.
"""def rename_field(old_field:str,new_field,col:str):
    c = db.collection(col)
    for doc in c:
        if old_field in doc.keys():
            """
#fix the value of an attrebute for all docs, given an attribute 'att', in a certain collection 'collection_name' 
# we check if it is 'bad_val' if so, we replace it if 'fixed_val'
def fix_attribute_to_all(collection_name:str,att:str,bad_val,fixed_val):
    print('here')
    col = db.collection(collection_name)
    for doc in col:
        
        if att in doc.keys():
            
            if doc[att]==bad_val:
                
                doc[att]=fixed_val
                col.update(doc)
                print(f'{"doc "}{doc["_id"]}{" was fixed"}')
                

#fix_attribute_to_all('refEdges','edgeType','Authership','Authorship')
