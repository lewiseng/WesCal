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

def extract_info(link):
    pass



