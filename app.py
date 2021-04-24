from flask import Flask, redirect, url_for, render_template, request, session
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
from createCatalog import get_courses


app = Flask(__name__)
app.secret_key = "WesHack2021"
catalog = get_courses("Catalog - Wesleyan University - 20210424.html")

@app.context_processor
def inject_catalog():
    return dict(log=catalog)

@app.route("/", methods=["POST","GET"])
def newSearch():
    session.clear()
    if request.method == "POST":
        courseName = request.form["course"].upper()
        if courseName in catalog:
            session["courseName"] = courseName
            return redirect(url_for("result"))
        else:
            return 'humm'
    else:
        return render_template('index.html')

@app.route('/result', methods=["GET"])
def result():
    if "courseName" in session:
        courseName = session["courseName"]
        return render_template('results.html',course=courseName)
    else:
        return redirect(url_for("newSearch"))

if __name__ == "__main__":
    app.run(debug=True)