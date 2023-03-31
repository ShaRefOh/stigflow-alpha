#airtable plugin
from airtable import Airtable
from dotenv import load_dotenv
import os
import time 

load_dotenv() 

# Retrieve the Airtable API key and base key from the environment variables
AIRTABLE_API_KEY = os.environ.get('SHA_AT_API_KEY')
TARGET_AIRTABLE_BASE_KEY = "appoQC04ImNE1w0nO"
#TARGET_AIRTABLE_BASE_KEY = os.environ.get('CSM_AT_BASE_ID')

# Initialize the Airtable objects for the source table and view
target_table = Airtable(base_id = TARGET_AIRTABLE_BASE_KEY,table_name= "Test", api_key=AIRTABLE_API_KEY)

#Define upsert function
def upsert(table, fields, message_id):
    record_id = None
    # Search for a record with the given message ID in the target table
    search_results = table.search('Message ID', message_id)
    if search_results:
        print('record found')
        # Update the existing record with the new data
        record_id = search_results[0]['id']
        table.update(record_id, fields)
    else:
        # Create a new record with the given data
        fields['Message ID'] = message_id
        table.insert(fields)
    return record_id

def airtable_stig_upsert(message):
    print("Airtable upsert is called")
    # Get the current time in UTC timezone
    current_time = time.gmtime()

    # Format the time as a string 
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", current_time)


    fields = {"Message ID" : str(message["Message_ID"]),
              "Message content" : message["Message_content"],
              "StigFlow Name" : message["StigFlow"],
              "Score" : message["Score"],
              "Authorship" : message["Authorship"],
              "Author" : message["Author"],
              "Channel" : message["Channel"],
              "Guild" : message["Guild"],
              "Thread Title" : message["Thread_Title"],
              "Jump URL" : message["Jump_URL"],
              "Upserted to Airtable" : timestamp,
              "Message Type" : message["Message_type"]
              }
    try:
        message["Extracted_URL"]
    except:
        print("No URLs found")
    else:
        string = message["Extracted_URL"][0]
        for url in message["Extracted_URL"][1:]:
            string = string + ',' + url
        fields['Extracted URLs']=string
    #Message ID might be an int in airtable
    upsert(target_table,fields,str(message["Message_ID"]))
    print("Airtable upsert is done")
#Need to change so we can handle multiple airtables 
def airtable_stig_delete_record(message_id):
    search_results = target_table.search('Message ID', message_id)
    if search_results:
        print('record found')
        # Update the existing record with the new data
        record_id = search_results[0]['id']
        target_table.delete(record_id)


"""message = {'_key': '1084420373757562961', 
           '_id': 'messages/1084420373757562961', 
           '_rev': '_frTT_xC---', 
           'Message_ID': 1084420373757562961, 
           'Author': 'Sha#6179', 
           'Authorship': '2023-03-12T10:19:24.660000+00:00', 
           'Channel': 'bot-test', 
           'Thread_Title': '', 
           'Message_content': 'Hi', 
           'Guild': 'StigFlow Beta', 
           'Jump_URL': 'https://discord.com/channels/1067891474873716796/1069248528766992516/1084420373757562961', 
           'Message_type': 'Message', 
           'saved_at': '2023-03-12T12:19:24.645588', 
           'Discord_roles': {'StigFlow_Beta': ['@everyone', 'Curator', 'Administrator']}, 
           'Reference': '', 
           'arango_time': 1678616364.645673,
           'StigFlow' : "Airtable_K", 
           'Score': 3,
           "Extracted_URL":'ww.shalom.peace'
           }

airtable_stig_upsert(message)"""

#remove_record('1084420373757562961',target_table)