import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from arango.http import HTTPClient
from arango.response import Response
from arango import ArangoClient
import time

class FixieHTTPClient(HTTPClient):
    def __init__(self):
        # Set up Fixie proxy credentials
        
        self.proxy = os.getenv('FIXIE_URL')

        
    def create_session(self, host):
        # Create a new requests session
        session = requests.Session()

        # Set up Fixie proxy
        session.proxies = {
            "http": self.proxy,
            "https": self.proxy
        }

        # Add retry logic
        retries = Retry(total=5,
                        backoff_factor=1,
                        status_forcelist=[ 500, 502, 503, 504 ])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # Return the session object
        return session

    def send_request(self, session, method, url, params=None, data=None, headers=None, auth=None):
        # Send the HTTP request using the session object
        response = session.request(method, url, params=params, data=data, headers=headers, auth=auth)

        # Return an instance of arango.response.Response
        return Response(
            method=response.request.method,
            url=response.url,
            headers=response.headers,
            status_code=response.status_code,
            status_text=response.reason,
            raw_body=response.text,
        )



# Get the Fixie URL from the Heroku config vars
FIXIE_URL = os.getenv('FIXIE_URL')
password = os.getenv("ARANGO_PASS2")
# Define a custom HTTP client class that uses Fixie IPs



client = ArangoClient(
    hosts="https://8002ef9dab5a.arangodb.cloud:18529", 
    http_client=FixieHTTPClient(),
    verify_override="cert_file.crt"
    
)

db = client.db("stigflow", username="shahar", password=password)




    
