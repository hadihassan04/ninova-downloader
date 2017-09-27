import requests
import bs4
import getpass
import os


def login(s):

    '''Get username'''
    username = input("username: ")
    '''Get password with getpass module'''
    password = getpass.getpass("pass: ")

    '''Try to get main page of ninova'''
    r = s.get('http://ninova.itu.edu.tr/kampus')

    '''Parse the returned page with bs4'''
    forms = bs4.BeautifulSoup(r.text, 'html.parser').findAll('input')

    '''Fill POST data'''
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

    '''Login and return'''
    return s.post(r.url, data=data)


def getPage(session, url):

    '''GET the url'''
    kampusPage = session.get(url)
    print(kampusPage.url)

    '''Return parsed data'''
    return bs4.BeautifulSoup(kampusPage.text, 'html.parser')


def getLinks(soup, filterString):

    '''Fill the list with relevant links'''
    tags = []
    for line in soup.find_all('a'):
        '''Only links with filterString in them'''
        if filterString in str(line):
            tags.append(line)

    '''Return the list of tags'''
    return tags


def saveFile(r, name):

    '''Save the content of response to file "name"'''
    f = open(name, 'wb')
    f.write(r.content)
    f.close()


def mkdir(classTag):

    '''Try creating a new folder'''
    try:
        name = classTag.findPrevious('span').text
        os.mkdir(name)

    '''If folder exists, create a new folder'''
    except FileExistsError:
        print('Folder already exists "'+name+'"')
        name = name+' (2)'
        os.mkdir(name)

    '''Create the necessary subfolders'''
    os.mkdir(name+os.sep+'dersDosyalari')
    os.mkdir(name+os.sep+'sinifDosyalari')

    '''Go up'''
    os.chdir(name)


def capturePage(session, resourceTagList):

    '''Iterate through tags'''
    for tag in resourceTagList:

        '''Check for the icon, if its a folder, create the subfolder,
            and enter, then call capturePage for the subfolder page'''
        if tag.findPrevious('img')['src'] == '/images/ds/folder.png':

            os.mkdir(tag.text)
            os.chdir(tag.text)

            soup = getPage(session, url+tag['href'])
            links = getLinks(soup, 'Dosyalari?g')

            capturePage(session, links)

            '''Go up when done'''
            os.chdir('..')

        '''If the icon is a link, dont touch it'''
        elif tag.findPrevious('img')['src'] == '/images/ds/link.png':
            continue

        '''Download the rest'''
        else:
            r = session.get(url+tag['href'])
            f = open(tag.text, 'wb')
            f.write(r.content)
            f.close()


def captureClass(session, classTag):

    '''Create class folder'''
    mkdir(link)

    '''GET and capture lecture files'''
    pageSoup = getPage(s, url+link['href']+'/DersDosyalari')
    links = getLinks(pageSoup, 'DersDosyalari?')
    os.chdir('dersDosyalari')
    capturePage(session, links)

    '''GET and capture class files'''
    pageSoup = getPage(s, url+link['href']+'/SinifDosyalari')
    links = getLinks(pageSoup, 'SinifDosyalari?')
    os.chdir('../sinifDosyalari')
    capturePage(session, links)

    '''Go up when done'''
    os.chdir('../../')


'''Base URL'''
url = 'http://ninova.itu.edu.tr'

'''Create a session for cookie management'''
s = requests.Session()

'''Login to ITU account'''
login(s)

'''Get the main page and class links of ninova'''
kampusSoup = getPage(s, url+'/Kampus1')
classLinks = getLinks(kampusSoup, 'ErisimAgaci')

'''Capture every class'''
for link in classLinks:
    captureClass(s, link)
