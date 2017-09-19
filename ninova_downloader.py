import requests
import bs4


def loadCreds():
    credFile = open('cred')
    loginKey = credFile.readline()
    credFile.close()
    return loginKey


def getPage(url):
    cookies = dict(ITUGirisV3=loadCreds())
    kampusPage = requests.get(url, cookies=cookies)
    return bs4.BeautifulSoup(kampusPage.text, 'html.parser')


def getLinks(soup, filter):
    classes = []
    for line in soup.find_all('a'):
        if filter in str(line):
            classes.append(line['href'])
    return classes


url = 'http://ninova.itu.edu.tr/Kampus1'
kampusSoup = getPage('http://ninova.itu.edu.tr/Kampus1')
classLinks = getLinks(kampusSoup, 'ErisimAgaci')

for link in classLinks:
    page = getPage(url+link+'/DersDosyalari', cookies=loadCreds())
    links = getLinks(page, 'DersDosyalari?')
    for i in links:
        print(link['href'])
