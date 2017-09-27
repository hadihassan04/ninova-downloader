import requests
import bs4
import pickle
import getpass


def login(s):
    username = "erfur"
    password = getpass.getpass("pass: ")
    r = s.get('http://ninova.itu.edu.tr/kampus')
    data = {'__EVENTTARGET':'',
            '__EVENTARGUMENT':'',
            '__VIEWSTATE':'iaP9ZZL72CjcyuH4ZblQI0AVwAvFcGZStqyeZZJ8VRcate4vsBOcISQG2hMVcnVb4fh141wJC8Ct3bMcsKlHwpnRtCCOZWNqowEhv5tHtiRTImjQ1Eysr2ttRHuBE/VuRgX6zoUYNZUBVpjBSgZq+iPsAuKPzmG/ZKx4IWmNfGtgxEUl2QP69IBK+PtlpDmsh0RJdI4uqM6wLo/3G63x8uYNSeHTG7qexhEbgyHhml3vvHkHMDZWNpEiKMmYdnQu',
            '__VIEWSTATEGENERATOR':'C2EE9ABB',
            '__EVENTVALIDATION':'MENDCN4R2D6sr9PCfpWCv0zgtgcxDb3RFgaiUbHVDKmC2sSSaSfQB/nZJW1JhsGbkjAdBSAbIXV+CqYW3HxzwcKd1FHcAtjZkB5tm5uFQG3xx8FE7VmqqJk+67Tcu9c0vIwgzqmraAPLrHAjGujLvqTtoSsbtnIgAN6/Nlv5H4/4OWRLfoOSdV79bTCZ5tQ5T9Qo1EHW8xw9GZ9asJ9GIFeJW4FyisvWGyEqTTj3H9l/JaMG9LqPpI+6B3PUz4kM3seg8mpACDUbuHMiA6+uEi+UeP8gvB5PIro5fnhhv1UDarXkVLFRV8KVCxjVF0YgivMwmu1A9uqEEjvrcJ8b+E6jpGbif6nPMnEXpxVAznXhFg5VwpeS0zkliO5VeZIbLwZVn1MekPzXkahwBPf0YGHYSPldR4bX2+7rPc+1LXg=',
            'ctl00$ContentPlaceHolder1$hfAppName':'Ninova',
            'ctl00$ContentPlaceHolder1$hfToken':'',
            'ctl00$ContentPlaceHolder1$hfVerifier':'',
            'ctl00$ContentPlaceHolder1$hfCode':'',
            'ctl00$ContentPlaceHolder1$hfState':'',
            'ctl00$ContentPlaceHolder1$tbUserName':username,
            'ctl00$ContentPlaceHolder1$tbPassword':password,
            'ctl00$ContentPlaceHolder1$btnLogin':'Giriş'
            }
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
        print(entry)
       # r = s.get(url+entry)
       # f = open(entry.split('/')[-1], 'wb')
       # f.write(r.content)
       # f.close()
