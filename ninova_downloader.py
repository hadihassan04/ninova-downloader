import requests
import bs4

credFile = open('cred')
loginKey = credFile.readline()
cookies = dict(ITUGirisV3=loginKey)

kampusPage = requests.get('http://ninova.itu.edu.tr/Kampus1',
                          cookies=cookies)

kampusSoup = bs4.BeautifulSoup(kampusPage.text, 'html.parser')

for line in kampusSoup.find_all('a'):
    if 'ErisimAgaci' in str(line):
        print(line)
