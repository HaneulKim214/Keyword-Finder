from splinter import Browser
from bs4 import BeautifulSoup
import os
import pymongo

# use pymongo to store all info from LinkedIN
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.linkedin_db


chrome_driver_path = os.path.abspath(r"C:\Users\haneu\Desktop\Data Analytics\6_mongo_webScrape\chromedriver.exe")
executable_path = {'executable_path': chrome_driver_path}
browser = Browser('chrome', **executable_path, headless=False)
url = "https://www.glassdoor.ca/index.htm"
browser.visit(url)


def search_location():
    print("Where do you want to find your job?")
    job_location = input()
    location = browser.find_by_id("LocationSearch")
    location.fill(job_location)
    # Clicking button
    browser.find_by_id("HeroSearchButton").click()


search_location()
def scrape_data():
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    # loop through pages
    pages = soup.find("div", class_="pagingControls").ul
    print(pages)
    
scrape_data()