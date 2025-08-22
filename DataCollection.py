import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random


#headers for request agent
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
  'Accept-Language': 'en-US,en;q=0.9',
  'Accept-Encoding': 'gzip, deflate, br',
  'Connection': 'keep-alive'
}

link = 'https://www.rappler.com/newsbreak/fact-check/sara-duterte-face-book-isang-kaibigan/'

# Request using `request` library
r = requests.get(link, headers=headers)
r
r.content

# Use BeautifulSoup to parse the HTML page
soup = BeautifulSoup(r.content, 'html.parser')
soup

soup.title  # with HTML tags
soup.title.text  # text within the HTML tags
title = soup.title.text.strip()  # whitespaces are removed
title

# Date published
date_published = soup.find(
  'time',  # HTML element tag
  {
      'class': 'published',
      'datetime': True
  }  # HTML attribute
)
# Actual text within the HTML element
date_published.text.strip()

# If you're after the HTML attribute, use the attribute name for the key
date_published = date_published['datetime']
date_published

# Extract article text
# element: div
# class: post-single__content entry-content
article_text = soup.find(
  'div',  # HTML element tag
  {
      'class': 'post-single__content entry-content'
  }  # HTML attribute
)
# Returns the HTML code for the article
article_text

# Get all paragraph (<p>) from the article_text
tagged_lines = article_text.find_all('p')  # Return list of paragraph elements

# Removes the HTML tags
text = ''
for line in tagged_lines:
  untagged_line = line.get_text()
  text += untagged_line + '\n'

# Returns the article text as 1 big string
print(text)

# Link
# Title
# Date Published
# Article's Text
rappler = pd.DataFrame(
    columns=['title', 'link', 'date_published', 'text']
)
doc_details = [title, link, date_published, text]
rappler.loc[len(rappler)] = doc_details
rappler

# Extract data from article based on link
def extract_article_data(link):
  """
  Extracts data from an article based on the provided link.

  Parameters:
    link (str): The URL of the article.

  Returns:
    list: A list containing the extracted article details in the following order:
      - title (str): The title of the article.
      - date (str): The date the article was published.
      - link (str): The URL of the article.
      - text (str): The content of the article.
  """
  # Make a GET request for the article URL
  r = requests.get(link, headers=headers)

  # Parse the HTML
  soup = BeautifulSoup(r.content, 'html.parser')

  # Retrieve doc title
  title = soup.title.text.strip()

  # IF NOT WITH RAPPLER ARTICLE, CHANGE THIS XOXO
  # Retrieve doc date
  date = soup.find("time", {"datetime": True})['datetime']

  # IF NOT WITH RAPPLER ARTICLE, CHANGE THIS XOXO
  # Retrieve article content
  text = ''
  tagged_lines = soup.find("div", {"class": "post-single__content entry-content"}).find_all('p')
  for line in tagged_lines:
    untagged_line = line.get_text()
    text += untagged_line + '\n'

  # Create list containing doc details
  # Append to dataset
  doc_details = [title, date, link, text]
  return doc_details

# Test the `extract_article_data` function
rappler.loc[len(rappler)] = extract_article_data(
  'https://www.rappler.com/philippines/hontiveros-seek-realignment-sara-duterte-book-fund-request-2025-budget/'
)
rappler

# Extracting Multiple Rappler Articles
mother_url = 'https://www.rappler.com/philippines/n13706946-ateneo-de-manila-university/'
page = 1
page_limit = 5
corpus = pd.DataFrame(columns=['title', 'link', 'date_published', 'text'])


while True:
  if page == 1:
    # Remove 'page/' at the end of mother_url
    page_url = mother_url[:-1]
  else:
    # Convert page number as a string
    page_str = str(page)
    # Form the article page
    page_url = mother_url + page_str
  print('Working on ' + page_url)

  # Add random time between 1 to 5 seconds before requesting
  time.sleep(random.randint(1, 5))

  # Get the list of articles within the page
  page_r = requests.get(page_url, headers=headers)
  page_soup = BeautifulSoup(page_r.content, 'html.parser')

  # Get the container of the articles
  article_container = page_soup.find('div', {'id': 'primary'})
  if article_container is None:
    print(f"No articles found on {page_url}")
    continue

  article_previews = article_container.find_all('article', {'class': 'post'})
  number_of_articles = len(article_previews)

  # If no article/s found, end
  if number_of_articles < 1:
    print('Extraction Finished!')
    break

  # Go through each article to extract and save to the dataframe
  for article_id in range(number_of_articles):
    # Focus on the article preview
    article = article_previews[article_id]
    # Get the clickable article title
    article_title = article.find("h2")

    # If no title, skip
    if article_title is None:
      continue

    # For each articles, invoke `extract_article_data`
    try:
      # Append to a dataframe
      corpus.loc[len(corpus)] = extract_article_data(article_title.find("a")['href'])
    except:
      # if there's an extraction error, skip
      continue

  # Check whether you have reached the page limit
  if page >= page_limit:
    break

  # Go to the next page
  page += 1

  
  file_name = 'rappler_corpus.xlsx'
  corpus.to_excel(file_name)
  print(f'File saved to {file_name}')

  corpus

# Extracting YouTube Comments