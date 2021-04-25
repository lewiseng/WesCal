from flask import Flask, redirect, url_for, render_template, request, session
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
from createCatalog import get_courses, get_crosslisting
from createEvent import processTime
from fetch_data import fetchData

app = Flask(__name__)
app.secret_key = "WesHack2021"
catalog = get_courses("Catalog - Wesleyan University - 20210424.html")
crossDict = get_crosslisting("Catalog - Wesleyan University - 20210424.html")

# @app.context_processor
# def inject_catalog():
#     return dict(log=fetchData(catalog[request.form["course"].upper()]))

@app.route("/", methods=["POST","GET"])
def newSearch():
    try:
        session.clear()
        if request.method == "POST":
            courseName = request.form["course"].upper()
            if courseName in crossDict:
                courseName = crossDict[courseName]
            if courseName in catalog:
                session["courseName"] = courseName
                return redirect(url_for("result"))
            else:
                return redirect(url_for("newSearch"))
        else:
            return render_template('index.html')
    except:
        return "SOMETHINGS WRONG"

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
    app.run(debug=True)