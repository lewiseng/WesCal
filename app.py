from flask import Flask, redirect, url_for, render_template, request, session, flash
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
from createCatalog import get_courses, get_crosslisting
from createEvent import processTime
from fetch_data import fetchData

app = Flask(__name__)
app.secret_key = "goWes2021"
catalog = get_courses("Catalog - Wesleyan University - 20210424.html")
crossDict = get_crosslisting("Catalog - Wesleyan University - 20210424.html")

@app.route("/", methods=["POST","GET"])
def newSearch():
    try:
        if request.method == "POST":
            courseName = request.form["course"].upper()
            if courseName in crossDict:
                courseName = crossDict[courseName]
            if courseName in catalog:
                session["courseName"] = courseName
                return redirect(url_for("result"))
            else:
                flash('Looks like you entered a wrong class number!', 'info')
                return redirect(url_for("newSearch"))
        else:
            return render_template('index.html')
    except:
        return render_template('errorPage.html') 

@app.route('/result', methods=["GET"])
def result():
    try:
        if "courseName" in session:
            courseName = session["courseName"]
            return render_template('results.html', catalog = catalog, data=processTime(fetchData(catalog[courseName])))
        else:
            return redirect(url_for("newSearch"))
    except:
        return render_template('errorPage.html') 


if __name__ == "__main__":
    app.run()