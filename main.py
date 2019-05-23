from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request, redirect, url_for
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os
import pymongo
import pandas as pd
import re
from splinter import Browser
from sklearn.feature_extraction.text import CountVectorizer
import time

app = Flask(__name__)

# list to store scraped data
company = []
all_location = []
job_desc = []
position = []

# Initialize browser to use chrome and show its process.
executable_path = {'executable_path': "chromedriver.exe"}
browser = Browser('chrome', **executable_path, headless=False)
# glassdoor url
url = "https://www.glassdoor.ca/index.htm"

def scrape_current_page():
    # Getting html of first page
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    jobs = soup.find_all("li", class_="jl")

    for job in jobs:
        # Store all info into a list         
        position.append(job.find("div", class_="jobTitle").a.text)
        # ex: Tommy - Singapore
        comp_loc = job.find("div", class_="empLoc").div.text
        comp, loc = comp_loc.split("–")
        # print(comp)
        company.append(comp.strip())
        all_location.append(loc.strip())
                
        # ------------- Scrape Job descriptions within a page -----------
        # job description is in another html, therefore retrieve it once again after
        # clicking.
        browser.click_link_by_href(job.find("a", class_="jobLink")["href"])
        html = browser.html
        soup = BeautifulSoup(html, "html.parser")
        job_desc.append(soup.find("div", class_="desc").text)

        time.sleep(1)
    return None

def scrape_all():
    # grab new html, grab page control elements
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # Will throw an error if there is no pagining control => one page => goto except statement
    try:
        result = soup.find("div", class_="pagingControls").ul
        pages = result.find_all("li")

        for page in pages:
            # scrape each page
            scrape_current_page()
            # run if <a> exists since un-clickable do not have <a> skipping < and pg1
            if page.a:
                # within <a> tag click except next button         
                if not page.find("li", class_="Next"):
                    try:
                        # Click to goto next page.
                        browser.click_link_by_href(page.a['href'])
                    except:
                        print("This is the last page")
                        break
    # only one page
    except:
        scrape_current_page()

    # No need to return since we appened all data into list
    return None

def stopword_deleter(tokenized_job_desc):
    """ ignore stop words, bullets, etc. And put it into one list """
    stop = stopwords.words('english')
    final_word_list = []
    for lists in tokenized_job_desc:
        for item in lists:
            if len(item)>2 and (item not in stop) and not(re.search(r"^[0-9]", item)):
                # Some words have \\ at the end, remove them.           
                final_word_list.append(item.replace("\\",""))
    return final_word_list

def lemmatize(cleaned_list_to_be_lemmatized):
    lemmatizer = WordNetLemmatizer()
    lemmatized_list = [lemmatizer.lemmatize(word,pos="v") for word in cleaned_list_to_be_lemmatized]
    return lemmatized_list

def text_classification():
    global job_desc # this allows you to modify global variable locally.

    # Befroe cleaning remove duplicated scrapes so we do not have same job desctions
    job_desc = set(job_desc)
    job_desc = list(job_desc)    

    for job in job_desc:
        ", ".join(job.split('/'))
    job_desc = [", ".join(job.split('/')) for job in job_desc]
    tok = [nltk.word_tokenize(job.lower()) for job in job_desc]
    # call function and store it into variable.
    cleaned_list = stopword_deleter(tok)
    lemmatized_list = lemmatize(cleaned_list)
    # Call get_top_100_words function to grab most occuring words in tuple format (word, freq)
    top_unigram = get_top_100_words(lemmatized_list)
    top_bigram = get_top_100_words_2chunk(lemmatized_list)

    # change it to [{word:freq}] format.
    full_list = []
    unigram_list = []
    bigram_list = []

    for item in top_unigram:
        uni_dict = {}
        uni_dict["word"] = item[0]
        uni_dict["freq"] = int(item[1])
        unigram_list.append(uni_dict)
    for item in top_unigram:
        bi_dict = {}
        bi_dict["word"] = item[0] #since json does not recognize numpy data type.
        bi_dict["freq"] = int(item[1]) # since we ran scikit learn it returned numbers as np.int
        bigram_list.append(uni_dict)

    full_list.append(unigram_list)
    full_list.append(bigram_list)

    return full_list # in the form [{word: freq, word2:freq, ...}]

def get_top_100_words(cleaned_corpus, n=100):
    vec = CountVectorizer().fit(cleaned_corpus)
    bag_of_words = vec.transform(cleaned_corpus)
    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in      
                   vec.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], 
                       reverse=True)
    return words_freq[:n]

def get_top_100_words_2chunk(corpus, n=100):
    vec1 = CountVectorizer(ngram_range=(2,2),
            max_features=2000).fit(corpus) 
    bag_of_words = vec1.transform(corpus) 
    sum_words = bag_of_words.sum(axis=0)

    words_freq = [(word, sum_words[0, idx]) for word, idx in #Select 0 because dict_items has all tuples in a first list., ("job", 971) tuple is one item, then as idx increase it select next tuple and so on.
                  vec1.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True) #Sort by number. since ("job", 93). x[1] = 93. In descending order.
    return words_freq[:n]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scrape/<input>")
def test(input):
    # With initialized browser from global, lets visit glassdoor website
    browser.visit(url)

    title, loc = input.split("!")
    print(title, f'location = {loc}')

    # Find where we should fill using splinter then fill it up
    job_type = browser.find_by_id("KeywordSearch")
    job_type.fill(title)

    location = browser.find_by_id("LocationSearch")
    location.fill(loc)

    # Clicking button
    browser.find_by_id("HeroSearchButton").click()

    scrape_all()
    # After scraping has been done, move on to text cleaning step and return top occuring items
    # for unigrams and bi-grams
    # Make these into [  [{}], [{}]  ]
    # first list is top_unigram second is top_bigrams
    full_list = text_classification()

    print(full_list)
    # Returning to scrape function in js
    return jsonify(full_list)


if __name__ == "__main__":
    app.run(debug=True)