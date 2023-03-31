#Notion plugin
import os
from dotenv import load_dotenv
from utils.Scraper import scrape
from notion_client import Client
import requests

print("I am here 1")

# Load environment variables
load_dotenv()

# Get Notion credentials
notion_token = os.getenv('NOTION_TOKEN')
notion_db_id = os.getenv('NOTION_TEST_DB_ID')
notion_db_qa_id = os.getenv('NOTION_QA_DB_ID')
# Connect to Notion and retrieve database
print("I am here 2")

notion = Client(auth=notion_token)
print("I am here 3")


notion_db = notion.databases.retrieve(database_id=notion_db_id)

notion_db_qa = notion.databases.retrieve(database_id=notion_db_qa_id)
print("I am here 4")

class NotionIntegration:
    """Initialize Notion client with provided token and database ID,
    or use environment variables as defaults
    """

    def __init__(self):
        self.notion_token = notion_token or os.getenv('NOTION_KEY')
        self.notion_db_id = notion_db_id or os.getenv('NOTION_DATABASE_ID')
        self.notion_db_qa_id = notion_db_qa_id or os.getenv('NOTION_QA_DB_ID')
        self.notion = Client(auth=notion_token)
        self.notion_db = notion.databases.retrieve(database_id=notion_db_id)
        self.notion_db_qa = notion.databases.retrieve(database_id=notion_db_qa_id)

    def upsert_notion_page(self, message,flow_name,score):
        print(f"{'In upsert_notion_page '}")

        # Searches for an existing page with the matching message ID in the Notion database
        results = self.notion.databases.query(
            database_id=self.notion_db_id,
            filter={
                "property": "Message ID",
                "rich_text": {
                    "equals": str(message['Message_ID'])
                }
            }
        ).get("results")
        """print(f"{'the results are '}{results}")
        print("END results")
        print("")"""

        try:
            message['Extracted_URL']
        except:
            message['Extracted_URL'] = [None]

        if message['Extracted_URL'][0]:
            url = message['Extracted_URL'][0]
            # Check if URL has a valid scheme
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            scraped_results = scrape(url)
            scraped_content = scraped_results["body"]
            scraped_title = scraped_results['title']
        else:
            scraped_content = ''
            scraped_title = ''

        if   scraped_title:
            title = scraped_title
        else: 
            title =  message['Message_type']+" by "+message['Author']+'on'+message['Channel']+', '+message['Thread_Title']
            
                   
        print(f"{'scraped title is '}{scraped_title}")
        page = {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": "From Discord: "+title
                            }
                        }
                    ]
                },
                "Message ID": {
                    "rich_text": [
                        {
                            "text": {
                                "content": str(message['Message_ID'])
                            }
                        }
                    ]
                },
                "Flow name": {
                    "rich_text": [
                        {
                            "text": {
                                "content": flow_name
                            }
                        }
                    ]
                },
                "Score": {
                    "type": "number",
                    "number": score
                },
                "Message author": {
                    "rich_text": [
                        {
                            "text": {
                                "content": message['Author']
                            }
                        }
                    ]
                },
                "Jump URL": {
                    "url": message['Jump_URL']
                },
                 "First URL": {
                    "url": message['Extracted_URL'][0]
                },
               
                 
                "Message content": {
                    "rich_text": [
                        {
                            "text": {
                                "content": message['Message_content']
                            }
                        }
                    ]
                }
                
            
        } 

        chilndren = [
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                        {
                            "type": "text",
                            "text": {
                            "content": "Scraped URL"
                            }
                        }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": scraped_content[:2000]
                                    
                                }
                            }
                        ]
                    }
                }
            ] 

        #print(page)
       
            
            
        if len(results) == 0:
            print("creating new page ")
            self.notion.pages.create(parent={"database_id": self.notion_db_id}, properties=page,children = chilndren)
            print(f"{'page has been created'}")
            
        else:
            page_id = results[0]['id']
            self.notion.pages.update(page_id=page_id, properties=page)
            print(f"{'page has been updated'}")



    def remove_notion_page(self, message_id):
        """Removes the Notion page associated with the incoming message"""

        # Searches for the page with the matching message ID in the Notion database and deletes it
        results = self.notion.databases.query(
            database_id=self.notion_db_id,
            filter={
                "property": "Message ID",
                "rich_text": {
                    "equals": message_id
                }
            }
        ).get("results")

        if len(results) > 0:
            # If a page is found, update its message_score property
            page = results[0]
            self.notion.pages.update(page_id=page['id'], archived=True)

    def upsert_notion_QandA(self, question:dict,answer:dict,flow_name:str,score):
            
            #print(f"{'in upsert_notion_QandA with Q&A'}{question}{  'and'  }{answer}")
            #print(f"{'Score is '}{score}{', flow name is '}{flow_name}")
            # Searches for an existing page with the matching message ID in the Notion database

            results = self.notion.databases.query(
                database_id=self.notion_db_qa_id,
                filter={
                    "property": "Answer ID",
                    "rich_text": {
                        "equals": str(answer['Message_ID'])
                    }
                }
            ).get("results")
            """print(f"{'the results are '}{results}")
            print("END results")
            print("")"""

            try:
                answer['Extracted_URL']
            except:
                answer['Extracted_URL'] = [None]

            try:
                question['Extracted_URL']
            except:
                question['Extracted_URL'] = [None]

        
                
            
            page = {
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": "Question answered by "+answer['Author']+'on'+question['Channel']+', '+question['Thread_Title']
                                }
                            }
                        ]
                    },
                    "Answer ID": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": str(answer['Message_ID'])
                                }
                            }
                        ]
                    },
                    "Flow name": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": flow_name
                                }
                            }
                        ]
                    },
                    "Score": {
                        "type": "number",
                        "number": score
                    },
                    "Answer author": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": answer['Author']
                                }
                            }
                        ]
                    },
                    "Question author": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": question['Author']
                                }
                            }
                        ]
                    },
                    "Jump to Question": {
                        "url": question['Jump_URL']
                    },
                    "Jump to Answer": {
                        "url": answer['Jump_URL']
                    },
                    "First URL in Question": {
                        "url": question['Extracted_URL'][0]
                    },
                    "First URL in Answer": {
                        "url": answer['Extracted_URL'][0]
                    },
                
                    
                    "Answer content": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": answer['Message_content']
                                }
                            }
                        ]
                    },
                    "Question content": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": question['Message_content']
                                }
                            }
                        ]
                    },
                    "Channel": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": question['Channel']
                                }
                            }
                        ]
                    }
                    
                
                }
           

        

            #print(f"{'We have a page: '}{page}")
            
            if len(results) == 0:
                print("creating new page ")
                self.notion.pages.create(parent={"database_id": self.notion_db_qa_id}, properties=page)
            
            else:
                print("Updating page")
                page_id = results[0]['id']
                self.notion.pages.update(page_id=page_id, properties=page)
    
    def remove_notion_QA(self, message_id):
        """Removes the Notion page associated with the incoming message"""

        # Searches for the page with the matching message ID in the Notion database and deletes it
        print(f"{'In reomve_notion_QA with '}{message_id}")
        results = self.notion.databases.query(
            database_id=self.notion_db_qa_id,
            filter={
                "property": "Answer ID",
                "rich_text": {
                    "equals": str(message_id)
                }
            }
        ).get("results")
        print(f"{'Results are'}{results}")

        if len(results) > 0:
            # If a page is found, update its message_score property
            page = results[0]
            print(f"{'page id is '}{page['id']}")
            self.notion.pages.update(page_id=page['id'], archived=True)

Notion_int = NotionIntegration()
question = {'_key': '1012318905389057', '_id': 'messages/1077617878905389057', '_rev': '_fsEoraq---','Extracted_URL':['https://medium.com/bettersharing/steward-ownership-is-capitalism-2-0-76a1c50a6d88'], 'Message_ID': 1231233333333, 'Author': 'ronent#2267', 'Authorship': '2023-02-21T15:48:43.503000+00:00', 'Channel': '🌐general', 'Thread_Title': '', 'Message_content': 'Sure, you can open one on <#1037262609793155112>  🙂', 'Guild': 'Common Sense [makers]', 'Jump_URL': 'https://discord.com/channels/1001036228294094909/1001036228294094914/1077617878905389057', 'Message_type': 'Reply', 'saved_at': '2023-03-14T21:48:26.595435', 'Discord_roles': {'Common_Sense_makers_': ['@everyone', 'StigFlow dev', 'StigSurfer', 'StigPerson', 'Veeoist', 'CS protocolist', 'StigFlow-gardener', 'Maker', 'Contributor', 'Discord-gardener', 'Steward']}, 'Reference': 1077440467060404224, 'arango_time': 1678823306.595531}
answer = {'_key': '1012318905389057', '_id': 'messages/1077617878905389057', '_rev': '_fsEoraq---','Extracted_URL':['www.wow.com'], 'Message_ID': 3333, 'Author': 'ronent#2267', 'Authorship': '2023-02-21T15:48:43.503000+00:00', 'Channel': '🌐general', 'Thread_Title': '', 'Message_content': 'Sure, you can open one on <#1037262609793155112>  🙂', 'Guild': 'Common Sense [makers]', 'Jump_URL': 'https://discord.com/channels/1001036228294094909/1001036228294094914/1077617878905389057', 'Message_type': 'Reply', 'saved_at': '2023-03-14T21:48:26.595435', 'Discord_roles': {'Common_Sense_makers_': ['@everyone', 'StigFlow dev', 'StigSurfer', 'StigPerson', 'Veeoist', 'CS protocolist', 'StigFlow-gardener', 'Maker', 'Contributor', 'Discord-gardener', 'Steward']}, 'Reference': 1077440467060404224, 'arango_time': 1678823306.595531}
flow = {'_key': '72892347', '_id': 'StigFlows/72892347', '_rev': '_fsDLUEa---', 'reactions': ['✅'], 'threshold': 1, 'group': {'Guild': 'Common_Sense_makers_', 'roles': ['Maker']}, 'action': 'Q&A', 'Status': 1}
Notion_int.upsert_notion_QandA(question=question,answer=answer,flow_name="Q&A",score=3)
#Notion_int.upsert_notion_page(message=question,flow_name=flow['action'],score=5)

print("Notion on line")


""""Scraped URL": {
                    "rich_text": [
                        {
                            "text": {
                                "content": scraped_content[:2000]
                            }
                        }
                    ]
                }"""
