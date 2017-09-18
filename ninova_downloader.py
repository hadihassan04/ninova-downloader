import requests
import bs4

credFile = open('cred')
loginKey = credFile.readline()
credFile.close()
cookies = dict(ITUGirisV3=loginKey)

kampusPage = requests.get('http://ninova.itu.edu.tr/Kampus1',
                          cookies=cookies)

kampusSoup = bs4.BeautifulSoup(kampusPage.text, 'html.parser')

classes = []
for line in kampusSoup.find_all('a'):
    if 'ErisimAgaci' in str(line):
        classes.append(line['href'])

for classLink in classes:
    classPage = requests.get('http://ninova.itu.edu.tr' + classLink +
                             '/DersDosyalari', cookies=cookies)
    classPageSoup = bs4.BeautifulSoup(classPage.text, 'html.parser')
    for link in classPageSoup.find_all('a'):
        if 'DersDosyalari?' in str(link):
            print(link['href'])
