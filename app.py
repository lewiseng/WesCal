from flask import Flask, redirect, url_for, render_template, request, session, flash
from bs4 import BeautifulSoup
from collections import namedtuple
import urllib.request, urllib.error, urllib.parse, ssl, re, unicodedata


def fetchData(url):
    """
    url -> dict {'COURSE': (TIME, 'INSTRUCTOR', 'LOCATION')
    'https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&crse=003331&term=1219'
    -> {'COMP211_01': ('..T.R.. 08:50AM-10:10AM; ...W... 01:20PM-02:40PM;', 'Victoria Ursula Manfredi', 'TBA'), 
    'COMP211_02': ('..T.R.. 08:50AM-10:10AM; ...W... 02:50PM-04:10PM;', 'Victoria Ursula Manfredi', 'TBA')}
    """
    
    fhand = urllib.request.urlopen(url,context=ssl.SSLContext()).read()
    soup = BeautifulSoup(fhand, 'html.parser')
    course_id = "".join(soup.title.string.split()[-2:])
    soup = BeautifulSoup(fhand, 'html.parser')
    fullName = soup.find("span", {"class": "title"}).string
    all_sect = soup.findAll(string = re.compile(r"SECTION (\d*)  "))
    find_time = soup.findAll(string='Times:')
    find_teacher = soup.findAll(string='Instructor(s):') #TWO TEACH?
    find_loc = soup.findAll(string='Location:') #TWO LOC?
    find_end = soup.findAll(string=['In-person only', 'In-person only - 3rd Quarter', 'In-person only - 4th Quarter'])
    temp_dict = {'In-person only': 'a20220504', 'In-person only - 3rd Quarter': 'b20220304', 'In-person only - 4th Quarter': 'c20220504'}
    res_dict = {}
    for i in range(len(all_sect)):
        secName = course_id+'_'+all_sect[i].strip()[-2:]
        secTime = unicodedata.normalize('NFKD',find_time[i].next_element).strip()
        secTeacher = [i.string for i in find_teacher[i].parent.parent.parent.find_all('a')]
        rearragne = list()
        for teacher in secTeacher:
            regex = re.search(r"([a-zA-ZÀ-ú]*),([a-zA-Z .À-ú]*)", teacher)
            rearragne.append(regex.group(2) + ' ' + regex.group(1))  
        secLoc = unicodedata.normalize('NFKD',find_loc[i].next_element).strip()
        res_dict[secName] = [fullName, secTime, ", ".join(rearragne), secLoc, temp_dict[find_end[i]]]


    if res_dict:
        return res_dict
    else:
        return None

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

def processTime(courseDict_original):

    def timeConvert(standard_time):
        import datetime
        military_time = datetime.datetime.strptime(
            standard_time, '%I:%M%p').strftime('%H%M%S')
        return military_time


    def createTime(timeString):
        if timeString == 'TBA':
            return 'TBA'
        else:
            Course = namedtuple('timeObject', ['MO', 'TU', 'WE', 'TH', 'FR'], defaults=[0, 0, 0, 0, 0])
            ins = {'M': (0, 0), 'T': (0, 0), 'W': (0, 0), 'R': (0, 0), 'F': (0, 0)}
            result = re.search(
                r'(^[\.MTWRF]*)\s([\d:(APM)]*)-([\d:(APM)]*)', timeString.strip())
            for day in result.group(1):
                if day == '.':
                    pass
                else:
                    ins[day] = (timeConvert(result.group(2)),
                                timeConvert(result.group(3)))
            # ways to shorten? map&lambda?
                schedule = Course((ins['M'][0], ins['M'][1]), (ins['T'][0], ins['T'][1]), (
                    ins['W'][0], ins['W'][1]), (ins['R'][0], ins['R'][1]), (ins['F'][0], ins['F'][1]))
            return schedule



    def formatTime(inputString, sem):
        if createTime(inputString) != 'TBA':
            temp_dict = {'M':'MO', 'T':'TU', 'W':'WE', 'R':'TH', 'F':'FR'}
            firstDay, firstDate = '', ''
            daylist = list()
            if sem == 'c':
                temp_dict2 = {'MO':'20220321', 'TU':'20220322', 'WE':'20220323', 'TH':'20220324', 'FR':'20220325'} #4th quarter
                for weekday in inputString.strip()[:7]:
                    if weekday in ['M', 'T', 'W', 'R', 'F']:
                        daylist.append(temp_dict[weekday]) 
            else:
                temp_dict2 = {'MO':'20220124', 'TU':'20220125', 'WE':'20220126', 'TH':'20220120', 'FR':'20220121'} #3rd quarter & full sem
                for weekday in inputString.strip()[4:7]+inputString.strip()[:4]:
                    if weekday in ['M', 'T', 'W', 'R', 'F']:
                        daylist.append(temp_dict[weekday]) 

            firstDay = daylist[0]
            firstDate = temp_dict2[firstDay]
            firstDayTime = getattr(createTime(inputString), firstDay)
            result = (",".join(daylist),firstDate+'T'+firstDayTime[0],firstDate+'T'+firstDayTime[1])
            return result
        else:
            return 'TBA'


    def dict_to_link(courseDict_final):
        """
        https://calendar.google.com/calendar/u/0/r/eventedit?dates={FirstClassStart}/{FirstClassEnd}
        &ctz=America/New_York&recur=RRULE:FREQ=WEEKLY;UNTIL=20211210T235900;WKST=SU;BYDAY={DayofClass}&
        location={LOCATION. ‘ ’ if TBD}&text={COURSE ID}&details=Instructor: {INSTRUCTOR} <br/> Classroom: {LOCATION}
        """
        resultList = list()
        for section, val in courseDict_final.items():
            mylist = re.findall(r'(.*?);', courseDict_original[section][1])
            tempList = list()
            for timing in mylist:
                time_final = formatTime(timing, val[4][0])
                if time_final != 'TBA': 
                    link = ("https://calendar.google.com/calendar/u/0/r/eventedit?dates={}/{}"
                    "&ctz=America/New_York&recur=RRULE:FREQ=WEEKLY;UNTIL={}T235900;WKST=SU;BYDAY={}&"
                    "text={}&details=Instructor: {} <br/> Classroom: {}")
                    startTime, endTime, classDay = time_final[1], time_final[2], time_final[0]
                    instructor, location, courseId, sem = val[2], val[3], val[0], val[4][1:]
                    instructor = val[2] if instructor != '' else 'STAFF'
                    # location_inlink = '' if location == 'TBA' else location # UPDATE THIS!
                    result = link.format(startTime, endTime, sem, classDay, courseId, instructor, location)
                    tempList.append(result)
                else:
                    tempList.append(time_final)
            resultList.append(tempList)

        i = 0
        for section in courseDict_final:
            courseDict_final[section][4] = resultList[i]
            i += 1
        return courseDict_final
    
    return dict_to_link(courseDict_original)

app = Flask(__name__)
app.secret_key = "goWes2021"
catalog = get_courses("Catalog - Wesleyan University - 20211126.html")
crossDict = get_crosslisting("Catalog - Wesleyan University - 20211126.html")

@app.route("/", methods=["POST","GET"])
def newSearch():
    
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
    
    # return render_template('errorPage.html') 

@app.route('/result', methods=["GET"])
def result():

    if "courseName" in session:
        courseName = session["courseName"]
        return render_template('results.html', catalog = catalog, data=processTime(fetchData(catalog[courseName])))
    else:
        return redirect(url_for("newSearch"))

        # return render_template('errorPage.html') 


if __name__ == "__main__":
    app.run(debug=True)