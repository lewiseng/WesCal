#%%
import urllib.request, urllib.error, urllib.parse, ssl, re, unicodedata, time
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime

#CROSSLISTING

def get_courses(src):
    fhand= open(src, encoding = "ISO-8859-1").read()
    soup = BeautifulSoup(fhand, 'html.parser')
    a_list = soup.findAll('a')
    courseDict = dict()
    '''
    list of bs4.element.ResultSet  ->  dict
    [<a href="https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&crse=007162&amp;term=1219">SPAN254</a>]
    ->
    {'SPAN254':"https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&crse=007162&amp;term=1219"}
    ''' 
    for course in a_list:
        if course.get('href') != 'mailto:wesmaps@wesleyan.edu' and 'class' not in course.attrs:
            temp = course.get('href')
            if temp:
                courseDict[course.string] = temp
    return courseDict

def get_crosslisting(src):
    fhand= open(src, encoding = "ISO-8859-1").read()
    soup = BeautifulSoup(fhand, 'html.parser')
    crossDict = {}
    crosslisting = soup.findAll(string='Crosslistings:')
    for i in crosslisting:
        course = unicodedata.normalize('NFKD',i.next_element.next_element.string).strip()
        listing = i.parent.parent.parent.previous_sibling.previous_sibling.a.string
        for coursename in course.split(","):
            crossDict[coursename] = listing
    return crossDict

if __name__ == "__main__":
    get_courses('Catalog - Wesleyan University - 20210424.html')
    get_crosslisting('Catalog - Wesleyan University - 20210424.html')

# %%
