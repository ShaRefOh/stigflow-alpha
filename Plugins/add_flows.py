from Arango_plugin import upsert_flow

#Change the paramenters to create the flow you want
# Key should be a valid arangoDB key - uses only letters and '_', no spaces. 
# Add reactions to the list.
# Threshold is an integer
#add discord roles names to the list, 
# A flow with status 0 will be ignored, A flow with status 1 is active
# Choose action from: A_K - airtable, N_K - notion liberary, Q&A - Notion questions and answers
upsert_flow(
    key="key",
    reactions=['🐦'],
    threshold=1,
    guild="Common Sense [makers]",
    channel=["all"],
    roles=["Maker"],
    status=0,
    action='N_T'
)