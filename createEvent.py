# %%
from collections import namedtuple, Counter; from datetime import time; from itertools import product
import re, math, time, csv, copy
import urllib.request, urllib.error, urllib.parse, ssl, re, unicodedata, time
from bs4 import BeautifulSoup, SoupStrainer
from fetch_data import fetchData


def processTime(courseDict_original):
#region
    '''
    {'COMP211_01': ['Computer Science I',[COMP211_01(MO=(0, 0), TU=('085000', '101000'), 
    WE=(0, 0), TH=('085000', '101000'), FR=(0, 0)),COMP211_01(MO=(0, 0), TU=(0, 0), 
    WE=('132000', '144000'), TH=(0, 0), FR=(0, 0))], 'Victoria Ursula Manfredi','TBA',[]],
    'COMP211_02': ['Computer Science I',[COMP211_02(MO=(0, 0), TU=('085000', '101000'), WE=(0, 0), 
    TH=('085000', '101000'), FR=(0, 0)), COMP211_02(MO=(0, 0), TU=(0, 0), WE=('145000', '161000'), 
    TH=(0, 0), FR=(0, 0))], 'Victoria Ursula Manfredi','TBA',[]]}
    -->>
    NEWDICT {'COMP211_01': ['Computer Science I', [('TU,TH', '20210907085000', '20210907101000'), 
    ('WE', '20210908132000', '20210908144000')], 'Victoria Ursula Manfredi', 'TBA', []], 
    'COMP211_02': ['Computer Science I', [('TU,TH', '20210907085000', '20210907101000'), ('WE', '20210908145000', 
    '20210908161000')], 'Victoria Ursula Manfredi', 'TBA', []]}
    '''
#endregion
    def timeConvert(standard_time):
        import datetime
        military_time = datetime.datetime.strptime(
            standard_time, '%I:%M%p').strftime('%H%M%S')
        return military_time


    def createTime(timeString):
        end_list = list()
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


    def formatTime(inputString):
    
        end_list = list()
        temp_dict = {'M':'MO', 'T':'TU', 'W':'WE', 'R':'TH', 'F':'FR'}
        temp_dict2 = {'MO':'20210906', 'TU':'20210907', 'WE':'20210908', 'TH':'20210909', 'FR':'20210910'}
        firstDay, firstDate = '', ''
        daylist = list()
        for weekday in inputString.strip()[:8]:
            if weekday in ['M', 'T', 'W', 'R', 'F']:
                daylist.append(temp_dict[weekday]) 
        firstDay = daylist[0]
        firstDate = temp_dict2[firstDay]
        firstDayTime = getattr(createTime(inputString), firstDay)
        result = (",".join(daylist),firstDate+'T'+firstDayTime[0],firstDate+'T'+firstDayTime[1])
        return result

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
                time_final = formatTime(timing)
                link = ("https://calendar.google.com/calendar/u/0/r/eventedit?dates={}/{}"
                "&ctz=America/New_York&recur=RRULE:FREQ=WEEKLY;UNTIL=20211210T235900;WKST=SU;BYDAY={}&"
                "location={}&text={}&details=Instructor: {} <br/> Classroom: {}")
                startTime, endTime, classDay = time_final[1], time_final[2], time_final[0]
                instructor, location, courseId = val[2], val[3], val[0]
                location_inlink = '' if location == 'TBA' else location # UPDATE THIS!
                result = link.format(startTime, endTime, classDay, location_inlink, courseId, instructor, location)
                tempList.append(result)
            resultList.append(tempList)

        i = 0
        for section in courseDict_final:
            courseDict_final[section][4] = resultList[i]
            i += 1
        return courseDict_final
    
    return dict_to_link(courseDict_original)


if __name__ == "__main__":
    print(fetchData('https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&crse=003331&term=1219'))
    testObj = processTime(fetchData('https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&crse=003331&term=1219'))
    print(testObj)




# %%
