from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
import time
from splinter import Browser

# my dependencies
from .googleMapApi import *


# list to store scraped data
company = []
location = []
job_desc = []
position = []

executable_path = {'executable_path': "chromedriver.exe"}
browser = Browser('chrome', **executable_path, headless=True)
# glassdoor url
url = "https://www.glassdoor.ca/index.htm"
# With initialized browser from global, lets visit glassdoor website
browser.visit(url)

def scrape_current_page():

    # Getting html of first page
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    jobs = soup.find_all("li", class_="jl")

    for job in jobs:
        # Store all info into a list         
#         position.append(job.find("div", class_="jobTitle").a.text)
        
        # Pop up will show up as soon as we start scraping.
        # so wait few seconds
        time.sleep(2)
        
        # print to see if there was a pop-up
        exit_button = soup.find("div", class_="ModalStyle__xBtn___34qya")
        
        # If there was a pop-up click close button.
        if exit_button:
            browser.find_by_css(".ModalStyle__xBtn___34qya").first.click()
        
        # Find company name
        comp = job.find("div", class_="jobHeader").div.text
        # Appending each company name into a list
        company.append(comp)
        
        #same for locations
        loc = job.find('div', class_="empLoc").span.text
        location.append(loc)
                
        # ------------- Scrape Job descriptions within a page -----------
        # job description is in another html, therefore retrieve it once again after
        # clicking.
        browser.click_link_by_href(job.find("a", class_="jobLink")["href"])
        html = browser.html
        soup = BeautifulSoup(html, "html.parser")
        job_desc.append(soup.find("div", class_="desc").text)

        time.sleep(1) # Since splinter scrapes too fast and skips some job description.
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
        

    # Close browser after scraping
    browser.quit()

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


# After scraping has been done, move on to text cleaning step and return top occuring items
# for unigrams and bi-grams
# Make these into [  [{}], [{}]  ]
# first list is top_unigram second is top_bigrams
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

    for item in top_bigram:
        bi_dict = {}
        bi_dict["word"] = item[0] #since json does not recognize numpy data type.
        bi_dict["freq"] = int(item[1]) # since we ran scikit learn it returned numbers as np.int
        bigram_list.append(bi_dict)

    # using company name and location grab [{lat:y, lng:x}, {}, {},...]
    # send list of company and location
    geocodes = googleMapApi.get_geocode(location, company)

    full_list.append(unigram_list)
    full_list.append(bigram_list)
    full_list.append(geocodes)
    full_list.append(company)
    return full_list # in the form [ [{word: freq, word2:freq, ...}], [{bigram: asd, bigram:sdf}] ]

def get_top_100_words(cleaned_corpus, n=50):
    vec = CountVectorizer().fit(cleaned_corpus)
    bag_of_words = vec.transform(cleaned_corpus)
    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in      
                   vec.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], 
                       reverse=True)
    return words_freq[:n]

def get_top_100_words_2chunk(corpus, n=50):
    vec1 = CountVectorizer(ngram_range=(2,2),
            max_features=2000).fit(corpus) 
    bag_of_words = vec1.transform(corpus) 
    sum_words = bag_of_words.sum(axis=0)

    words_freq = [(word, sum_words[0, idx]) for word, idx in # Select 0 because dict_items has all tuples in a first list., ("job", 971) tuple is one item, then as idx increase it select next tuple and so on.
                  vec1.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True) #Sort by number. since ("job", 93). x[1] = 93. In descending order.
    return words_freq[:n]