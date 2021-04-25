import urllib.request, urllib.error, urllib.parse, ssl, re, unicodedata, time, copy
from bs4 import BeautifulSoup, SoupStrainer

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
    res_dict = {}
    for i in range(len(all_sect)):
        secName = course_id+'_'+all_sect[i].strip()[-2:]
        secTime = unicodedata.normalize('NFKD',find_time[i].next_element).strip()
        secTeacher = [i.string for i in find_teacher[i].parent.parent.parent.find_all('a')]
        rearragne = list()
        for teacher in secTeacher:
            regex = re.search(r"([a-zA-Z]*),([a-zA-Z ]*)", teacher)
            rearragne.append(regex.group(2) + ' ' + regex.group(1))  
        secLoc = unicodedata.normalize('NFKD',find_loc[i].next_element).strip()
        res_dict[secName] = [fullName, secTime, ", ".join(rearragne), secLoc,[]]
    


    if res_dict:
        return res_dict
    else:
        return None

# print(processTime(fetchData('https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&crse=003331&term=1219')))