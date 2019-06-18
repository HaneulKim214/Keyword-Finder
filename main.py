from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request, redirect, url_for
import matplotlib.pyplot as plt
import os
import pymongo
from splinter import Browser


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scrape/<input>")
def test(input):
    # grabbing variable from nlp file
    from nlp import browser
    # import nlp to use its methods
    import nlp

    title, loc = input.split("!")
    print(title, f'location = {loc}')

    # Find where we should fill using splinter then fill it up
    job_type = browser.find_by_id("KeywordSearch")
    job_type.fill(title)

    location = browser.find_by_id("LocationSearch")
    location.fill(loc)

    # Clicking button
    browser.find_by_id("HeroSearchButton").click()

    nlp.scrape_all()
    full_list = nlp.text_classification()

    print(full_list)
    return jsonify(full_list)


if __name__ == "__main__":
    app.run()