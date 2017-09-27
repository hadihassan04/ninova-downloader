import requests
import bs4
import getpass


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
    classes = []
    for line in soup.find_all('a'):
        if filterString in str(line):
            classes.append(line['href'])
    return classes


def saveFile(r, name):
    f = open(name, 'wb')
    f.write(r.content)
    f.close()


url = 'http://ninova.itu.edu.tr'
s = requests.Session()
login(s)

kampusSoup = getPage(s, url+'/Kampus1')
classLinks = getLinks(kampusSoup, 'ErisimAgaci')

for link in classLinks:
    pageSoup = getPage(s, url+link+'/DersDosyalari')
    links = getLinks(pageSoup, 'DersDosyalari?')
    for entry in links:
        try:
            r = s.get(url+entry)
        except:
            continue
        print(r.is_redirect)
        print(r.encoding)
        if not r.encoding:
            f = open(entry.split('/')[-1], 'wb')
            f.write(r.content)
            f.close()
