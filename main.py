from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request, redirect, url_for
import matplotlib.pyplot as plt
import nltk
import os
import pymongo
import pandas as pd
import re
from splinter import Browser
import time

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/scrape/<input>")
def test(input):
    title, loc = input.split("!")
    print(title, f'location = {loc}')
    # Call init function to open browser

    # Initialize browser to use chrome and show its process.
    executable_path = {'executable_path': "chromedriver.exe"}
    browser = Browser('chrome', **executable_path, headless=False)
    url = "https://www.glassdoor.ca/index.htm"
    browser.visit(url)

    # Find where we should fill job-title then fill it up
    job_type = browser.find_by_id("KeywordSearch")
    job_type.fill(title)

    location = browser.find_by_id("LocationSearch")
    location.fill(loc)

    # Clicking button
    browser.find_by_id("HeroSearchButton").click()

    # list to store scraped data
    company = []
    location = []
    job_desc = []
    position = []
    
    # scrape first page and append data into initial lists 
    scrape_current_page(company, location, job_desc, position)


    # grab new html, grab page control elements
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    result = soup.find("div", class_="pagingControls").ul
    pages = result.find_all("li")

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


def scrape_current_page(company, location, job_desc, position):
    
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
        location.append(loc.strip())
        
        browser.click_link_by_href(job.find("a", class_="jobLink")["href"])
        
        # ------------- Scrape Job descriptions within a page -----------
        # job description is in another html, therefore retrieve it once again after
        # clicking.
        html = browser.html
        soup = BeautifulSoup(html, "html.parser")
        job_desc.append(soup.find("div", class_="desc").text)



if __name__ == "__main__":
    app.run(debug=True)