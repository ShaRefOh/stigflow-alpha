import requests
from bs4 import BeautifulSoup







def scrape(url:str):
    # Send a request to the given url and get its content
    response = requests.get(url)

    # Parse the response html into soup format to extract data
    soup = BeautifulSoup(response.content, "html.parser")
    # Extract the H1 tag which contains the title
    title = soup.find("h1").get_text()

    # Extract the author name
    try:
        author = soup.find("span", class_="fe bm").find("a").get_text()
    except:
        author = ''

    # Extract the post date
    try:
        post_date = str(soup.find("time")['datetime'])
    except:
        post_date = ''

    # Extract the article content
    article_body = soup.find_all('p')

    # Print the results
    print(f"Title: {title}")
    print(f"Author: {author}")
    #print(f"Publish Date: {post_date}")
    body = ''
    for paragraph in article_body:
        body = body + paragraph.get_text()
    return {"title":title,"author":author,"date":post_date,"body":body}


