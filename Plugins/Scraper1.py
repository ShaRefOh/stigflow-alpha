import requests
from bs4 import BeautifulSoup
def scrape(url):
    # Send a GET request to the URL and retrieve the HTML content
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract the description and name fields based on their HTML tags or attributes
    description = soup.find("meta", attrs={"name": "description"})["content"]
    name = soup.find("meta", attrs={"property": "og:title"})["content"]
    return {"name":name,"description":description}