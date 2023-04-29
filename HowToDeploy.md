Corrected instructions:

# How to deploy your own instance of the app to Heroku

You will need the following:
1. A Discord account and a server where you have bot-inviting permissions
2. An ArangoDB cloud service account
3. Airtable or Notion with admin permissions
4. A Heroku account
5. Git installed on your local machine and some basic knoledge on how to use it
6. Python 3.9 installed in your local machine

## Discord bot settings

### Setting up your Discord app:
* Firstly, you will need to have a Discord account. 
* Then, go to the [Discord Developer Portal](https://discord.com/developers/applications). Make sure you are on the "Applications" tab, and add a new app by pressing the "New Application" button. 
* Enter your application details, and add any additional information you would like in the "General Information" tab.
* Go to the "Bot" tab on the left-hand menu and create a bot.
* Save your bot token; later, we will add it to the environment variables of the app.
* Turn on the following options: "REQUIRES OAUTH2 CODE GRANT", "PRESENCE INTENT", "SERVER MEMBERS INTENT", and "MESSAGE CONTENT INTENT".

### Creating a bot invite link and adding your bot to a Discord server
* Now, go to "OAuth2" -> "URL generator" in the side menu.
* For "SCOPES", check the "bot" and "messages.read" boxes.
* For "BOT PERMISSIONS", check "Read Messages/View Channels".
* For "TEXT PERMISSIONS", check "Read Message History".
* Copy the link, go to that address, and choose the server you wish to use.

## ArangoDB settings
### Creating a deployment
* Go to https://cloud.arangodb.com and create an account, and then create a new deployment.
* Choose the Google Cloud deployment.

### Collections settings 
* Go to your endpoint and create a new database named "stigflow". 
* Create the following document collections:
  * StigFlows
  * Makers
  * Messages
  * URLs
  * Servers
* Create the following edge collections:
  * RefEdges
  * Membership
  * ReactionEdges

## Airtable settings
* Create an Airtable account or have admin permissions on an existing one.
* Create a new table in a base (either a new or existing one).
* The table must include the following fields: 
  * Author
  * Message ID (single line text)
  * Message content (long text)
  * Channel (single line text)
  * StigFlow Name (single line text)
  * Score (number)
  * Authorship (date - ISO - 12 hour)
  * Guild (single line text)
  * Thread Title (single line text)
  * Jump URL (URL)
  * Upserted to Airtable (date - iso - 12 hours)
  * Extracted URLs (URL)
  * Message Type (single line text)

## Notion settings
* You will need admin permissions on a Notion workspace.
* Create two databases using the following templates: [Liberary](https://www.notion.so/m4co/984c7369f720453fb2f4d87a833d8586?v=62efddf722e94da184bf56a317479faf&pvs=4) and [Q&A](https://www.notion.so/m4co/841e7a36683546cfbdc2d970d83ff7bc?v=632a2dde80e3447f8f0fd1ecef7bdbd8&pvs=4)
* Go to Notion developer portal
* Create an app and save the secret key
* Go to the Notion databases, press the three doted manue and add in connections the app you just created - that will enable access to the databases through the secret key

## Heroku instructions
### Heroku settings
* You will need to create a Heroku account and install the Heroku CLI.
* Create a new app in Heroku and get a dyno plan.
* Clone this repo to your local machin using git.
* Generate an arangoDB cert_file
 * Go to your arango cloud dashboard and press the view button on your deployment
 * Press the 'Connect drivers' button
 * Go to the Python tab and copy the code anb save it with .py
 * Replace "_system" with "stigflow" and use your password obtained in the deployment screan.
 * Run the python script and check that a new cert_file has been created. 
 * Now you can follow Heroku's instruction and git push your local repo into Heroku Git
 * In the settings tab of your app, press reveal cofig variables
 * You need to retrive and add the following keys:
  * ARANGO_PASS2 = your arangoDB passward
  * DISCORD_BOT_TOKEN = your bot token retrived from Discord developer portal
  * NOTION_QA_DB_ID = your notion Q&A database id, wich is the first serial in the database address before the question mark
  * NOTION_TEST_DB_ID = the Liberary Notion database ID
  * NOTION_TOKEN = the token retrived from Notion's developer portal
  * SHA_AT_API_KEY = the personal secret key retrived form Airtable
 * Now you go to the add-ons tab in your Heroku dashboard and add Fixie to your app
 * You can do it using CLI in your terminal - see [instructions](https://devcenter.heroku.com/articles/fixie) 
 * During this process you will be exposed to fixie's IP list that they provide
 * Copy these IPs
 * Go to your arango cloud deployment and peast the IPs to the allowlist.
 
 ## Setting up basic flows
 Flows make up rules on discord messages, the app will aggregate reactions assigned to messages, check if the dicord roles of the issuers should be counted and calculate a score, if the score passes a predefiend threshod it will triger an action. Thses are the possible actions
 1. N_K - posting into a the Notion Liberary database, note that the entries are being updated if changes have being made in discord.
 2. A_K - similar to N_K only on airtable
 3. Q&A - workes when the chosen reactions (assinged by the chosen discord roles) are being issued on a discord reply or a message in a thread. The app will fetch the message which was replied on and store bith message and reply as a question and answer in the notion Q&A database. This is meant to prompt a chatbot so it is able to answer common Q&A for a community. This flow is meant to be used together with [Algoveras AI workflows](https://app.algovera.ai/workflows/run?id=question-answering). 
 The parameters for setting up a new flow are
 1. key - a string of a arangoDB documment key
 2. reactions - a list with strings of reactions, "all" is also an option which will make the flow calculate all reactions
 3. treashold
 ### Currently avialble flows
 * Notion Liberary - Set a threa
 * Open add_flows.py locally
 * Edit the script ass instructed
 * Run the script to add the new flow
 
 # TO-DO
 * Set the keys with normal names
 * Change arango username to be a key
 