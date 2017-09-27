import requests
import bs4
import getpass
import os


def login(s):
    username = "erfur"
    password = getpass.getpass("pass: ")
    r = s.get('http://ninova.itu.edu.tr/kampus')
    forms = bs4.BeautifulSoup(r.text, 'html.parser').findAll('input')
    data = {}
    for form in forms:
        if 'value' in form.attrs:
            data[form['name']] = form['value']
        else:
            data[form['name']] = ""
    data['__EVENTTARGET'] = ''
    data['__EVENTARGUMENT'] = ''
    data['ctl00$ContentPlaceHolder1$tbUserName'] = username,
    data['ctl00$ContentPlaceHolder1$tbPassword'] = password,
    return s.post(r.url, data=data)


def getPage(session, url):
    kampusPage = session.get(url)
    print(kampusPage.url)
    return bs4.BeautifulSoup(kampusPage.text, 'html.parser')


def getLinks(soup, filterString):
    tags = []
    for line in soup.find_all('a'):
        if filterString in str(line):
            tags.append(line)
    return tags


def saveFile(r, name):
    f = open(name, 'wb')
    f.write(r.content)
    f.close()


def mkdir(classTag):
    try:
        name = classTag.findPrevious('span').text
        os.mkdir(name)
        os.mkdir(name+os.sep+'dersDosyalari')
        os.mkdir(name+os.sep+'sinifDosyalari')
        os.chdir(name)
    except:
        print('Could not create folder')


def capturePage(session, resourceTagList):
    for tag in resourceTagList:
        if tag.findPrevious('img')['src'] == '/images/ds/folder.png':
            os.mkdir(tag.text)
            os.chdir(tag.text)
            soup = getPage(session, url+tag['href'])
            links = getLinks(soup, 'Dosyalari?g')
            capturePage(session, links)
            os.chdir('..')
        elif tag.findPrevious('img')['src'] == '/images/ds/link.png':
            continue
        else:
            r = session.get(url+tag['href'])
            f = open(tag.text, 'wb')
            f.write(r.raw)
            f.close()


def captureClass(session, classTag):
    mkdir(link)

    pageSoup = getPage(s, url+link['href']+'/DersDosyalari')
    links = getLinks(pageSoup, 'DersDosyalari?')
    os.chdir('dersDosyalari')
    capturePage(session, links)

    pageSoup = getPage(s, url+link['href']+'/SinifDosyalari')
    links = getLinks(pageSoup, 'SinifDosyalari?')
    os.chdir('../sinifDosyalari')
    capturePage(session, links)

    os.chdir('../../')


url = 'http://ninova.itu.edu.tr'
s = requests.Session()
login(s)

kampusSoup = getPage(s, url+'/Kampus1')
classLinks = getLinks(kampusSoup, 'ErisimAgaci')

for link in classLinks:
    captureClass(s, link)
