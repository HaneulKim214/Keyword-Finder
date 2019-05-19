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
    return None
def scrape_all():
    # grab new html, grab page control elements
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    result = soup.find("div", class_="pagingControls").ul
    pages = result.find_all("li")

    # Scrape first page before going to next
    scrape_current_page()
    for page in pages:
        # run if <a> exists since un-clickable do not have <a> skipping < and pg1
        if page.a:
            # within <a> tag click except next button         
            if not page.find("li", class_="Next"):
                try:
                    # Click to goto next page, then scrape it.
                    browser.click_link_by_href(page.a['href'])
                    # --------- call scrape data function here ---------
                    scrape_current_page()
                except:
                    print("This is the last page")
    # No need to return since we appened all data into list
    return None

def stopword_deleter(tokenized_job_desc):
    """ ignore stop words, bullets, etc. And put it into one list """
    stop = stopwords.words('english')
    final_word_list = []
    for lists in tokenized_job_desc:
        for item in lists:
            if len(item)>2 and (item not in stop):
                # Some words have \\ at the end, remove them.           
                final_word_list.append(item.replace("\\",""))
    return final_word_list

def lemmatize(cleaned_list_to_be_lemmatized):
    lemmatizer = WordNetLemmatizer()
    lemmatized_list = [lemmatizer.lemmatize(word,pos="v") for word in cleaned_list_to_be_lemmatized]
    return lemmatized_list

def text_classification():
    global job_desc
    for job in job_desc:
        ", ".join(job.split('/'))
    job_desc = [", ".join(job.split('/')) for job in job_desc]
    tok = [nltk.word_tokenize(job.lower()) for job in job_desc]
    # call function and store it into variable.
    cleaned_list = stopword_deleter(tok)
    lemmatized_list = lemmatize(cleaned_list)

    # Find out 100 most frequent words
    freq = nltk.FreqDist(lemmatized_list)
    most_freq_words = freq.most_common(100)
    print(most_freq_words)  # ================================================================ Left off here----> Works fine!

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scrape/<input>")
def test(input):
    # With initialized browser, lets visit glassdoor website
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
    # After scraping has been done, move on to text cleaning step
    text_classification()

    # Returning to scrape function in js
    return "All done"


if __name__ == "__main__":
    app.run(debug=True)