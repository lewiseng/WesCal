import urllib.request, urllib.error, urllib.parse, ssl, re, unicodedata, time
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
    only_tags = SoupStrainer(id='print_sect_info')
    soup = BeautifulSoup(fhand, 'html.parser',parse_only=only_tags)
    all_sect = soup.findAll(string = re.compile(r"SECTION (\d*)  "))
    find_time = soup.findAll(string='Times:')
    find_teacher = soup.findAll(string='Instructor(s):')
    find_loc = soup.findAll(string='Location:')
    

    res_dict = {}
    for i in range(len(all_sect)):
        secName = course_id+'_'+all_sect[i].strip()[-2:]
        secTime = unicodedata.normalize('NFKD',find_time[i].next_element).strip()
        secTeacher = find_teacher[i].parent.parent.a.get_text()
        rearragne = re.search(r"([a-zA-Z]*),([a-zA-Z ]*)", secTeacher)
        secTeacher = rearragne.group(2) + ' ' + rearragne.group(1)
        secLoc = unicodedata.normalize('NFKD',find_loc[i].next_element).strip()
        res_dict[secName] = (secTime, secTeacher, secLoc)


    if res_dict:
        return res_dict
    else:
        return None

    
print(fetchData('https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&crse=003331&term=1219'))
