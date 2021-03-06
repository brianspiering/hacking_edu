#!/usr/bin/env python

""" Call wolframalpha API

docs (pdf): http://products.wolframalpha.com/docs/WolframAlpha-API-Reference.pdf?_ga=1.107330246.599422832.1445658318

Doesn't work for:
- one: returns itself

"""

from collections import defaultdict
import csv
import json
import requests
import shutil
import sys

from bs4 import BeautifulSoup

# Open config file to get key
with open('wolframalpha_api.config', 'r') as f:
    wolfram_key = f.readline().rstrip()
 
# Get phrase translation dictionary
with open("title_translation.json", "r") as f:
    title_translation = json.load(f)

def clean_wolfram_data(raw_data):
    try:
        clean_data = round(float(raw_data[:10]), 4)

        return clean_data
    except ValueError:
        print('\n\n{} is not handled by the code'.format(raw_data))

def make_card_front(title, hyponym):
    "Reformat a title string into front of a flashcard."
    
    title = title.lower().strip() # Munge data

    # Take wolfram api 'title' tag and make into human readable title
    card_front = title_translation[title]['subject']+' '+hyponym+title_translation[title]['punctation']
    return card_front

def save_image(url, filename):
    "Save image to disk"
    r = requests.get(url, stream=True)

    if r.status_code == 200:
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    else:
        print('Non-valid url')    
  
def call_wolfram_api(topic):
    
    # Get category
    # category = raw_input('Enter a topic to query on Wolfram Alpha: ') # Ask for topic to query

    # Look for hyponyms
    try:
        file_endpoint = "data/"+topic+"_hyponyms.csv"
         # Load file
        with open(file_endpoint, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for hyponyms in spamreader:
                pass
    except:
        hyponyms = [topic]

    # Hack for empty hyponyms file
    if not hyponyms:
        hyponyms = [topic] # Make them the topic

    # Call api for each topic
    for hyponym in hyponyms:

        hyponym = hyponym.replace('_', ' ').lower().strip()

        # Build URL using hyponym
        url = 'http://api.wolframalpha.com/v2/query?input=' + hyponym + "&format=image" +'&appid=' + wolfram_key 

        # Scrape URL
        r  = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data)

        # Make an image flashcard
        for i, pod in enumerate(soup.findAll('pod')):
            # print('Processing data from wolfram API: ', hyponym) # Number of data sets from api: '|',i
            if i == 1:
                print('Processing data from wolfram API: ', hyponym) # Number of data sets from api: '|',i
                try:
                    title = pod.attrs['title']
                    card_front = make_card_front(title, hyponym)

                    # raw_data = pod.findAll("img")[0].get("alt") # Sometimes 
                    # card_back = clean_wolfram_data(raw_data) # The text is not good nor consistent
                    image_url = pod.findAll("img")[0].get("src")
                    image_filename = 'data/images/'+hyponym+'.jpg'
                    save_image(image_url, image_filename)
                    flashcard = {"fcid": 1,
                            "order": 0,
                            "term": card_front,
                            "definition": None,
                            "hint": "",
                            "example": "",
                            "term_image": image_filename,
                            "hint_image": None}

                    # Save the data
                    flashcard_endpoint = "data/"+topic+"_"+hyponym+".json"

                    with open(flashcard_endpoint, "w") as data_out:
                        json.dump(flashcard, data_out)

                    print('Wolfram Alpha data stored for: '+hyponym+'\n\n')

                    break
                except KeyError:
                    print("New title. Please process: '"+title+"'")
                except NameError:
                    print("Couldn't find your term. Please try another one.")

if __name__ == "__main__":
    call_wolfram_api(sys.argv[1]) # The command line argument is the name of the hyponyms file
