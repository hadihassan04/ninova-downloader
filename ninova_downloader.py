import requests
import bs4
import getpass
import os
import re


def login(s):

    '''Get username'''
    username = input("username: ")
    '''Get password with getpass module, cuz muh privacy'''
    password = getpass.getpass("pass: ")

    '''Try to get main page of ninova'''
    r = s.get('http://ninova.itu.edu.tr/kampus')

    '''Parse the returned page with bs4'''
    forms = bs4.BeautifulSoup(r.text, 'html.parser').find_all('input')

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


def sanitize_filename(name):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip(' .')


def mkdir(classTag):

    '''Get cwd'''
    root = os.getcwd()

    name = sanitize_filename(classTag.find_previous('span').text)

    '''Try creating a new folder'''
    if not os.path.exists(name):
        os.mkdir(name)

    os.chdir(name)

    '''Create the necessary subfolders'''
    if not os.path.exists('dersDosyalari'):
        os.mkdir('dersDosyalari')
    if not os.path.exists('sinifDosyalari'):
        os.mkdir('sinifDosyalari')

    '''Go back'''
    os.chdir(root)

    return name


def capturePage(session, resourceTagList):

    '''Iterate through tags'''
    for tag in resourceTagList:

        '''Check for the icon, if it is a folder, create the subfolder,
            and enter, then call capturePage for the subfolder page'''
        if tag.find_previous('img')['src'] == '/images/ds/folder.png':

            '''Get root directory'''
            root = os.getcwd()

            folder_name = sanitize_filename(tag.text)
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)
            os.chdir(folder_name)

            soup = getPage(session, url+tag['href'])
            links = getLinks(soup, 'Dosyalari?g')

            capturePage(session, links)

            '''Go back when done'''
            os.chdir(root)

        elif tag.find_previous('img')['src'] == '/images/ds/link.png':
            '''If the icon is a link, dont touch it'''
            continue

        else:
            '''Download the rest'''
            filename = sanitize_filename(tag.text)
            if os.path.exists(filename):
                print(f"[SKIP] {filename} already exists.")
                continue
            r = session.get(url+tag['href'])
            saveFile(r, filename)


def captureClass(session, classTag):

    '''Get root directory'''
    root = os.getcwd()

    '''Create class folder'''
    name = mkdir(link)
    os.chdir(name)

    '''GET and capture lecture files'''
    pageSoup = getPage(s, url+link['href']+'/DersDosyalari')
    links = getLinks(pageSoup, 'DersDosyalari?')
    os.chdir('dersDosyalari')
    capturePage(session, links)
    os.chdir('..')

    '''GET and capture class files'''
    pageSoup = getPage(s, url+link['href']+'/SinifDosyalari')
    links = getLinks(pageSoup, 'SinifDosyalari?')
    os.chdir('sinifDosyalari')
    capturePage(session, links)
    os.chdir('..')

    # --- Homework (Ödevler) support ---
    hw_url = url + link['href'] + '/Odevler'
    hwSoup = getPage(s, hw_url)
    # Only include assignment detail links, never /OdevGonder
    hwLinks = []
    for a in hwSoup.find_all('a', href=True):
        href = a['href']
        if re.match(r'^/Sinif/\d+\.\d+/Odev/\d+($|\?)', href):
            hwLinks.append(a)
    if hwLinks:
        # Create a folder for homeworks if not exists
        hw_folder = 'odevler'
        if not os.path.exists(hw_folder):
            os.mkdir(hw_folder)
        os.chdir(hw_folder)
        for hw in hwLinks:
            # Go to assignment detail page
            detail_url = url + hw['href']
            detailSoup = getPage(s, detail_url)
            # Extract assignment title (e.g., from <h1>)
            title_tag = detailSoup.find('h1')
            hw_title = sanitize_filename(title_tag.text.strip()) if title_tag else sanitize_filename(hw.text.strip())
            if not os.path.exists(hw_title):
                os.mkdir(hw_title)
            os.chdir(hw_title)
            # Download all files in 'Kaynak Dosyalar' table
            table = detailSoup.find('table', id='ctl00_ContentPlaceHolder1_gvDosyalar')
            if table:
                for a in table.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('javascript:'):
                        continue  # skip JavaScript links
                    file_url = url + href if href.startswith('/') else href
                    fname = sanitize_filename(a.text)
                    if os.path.exists(fname):
                        print(f"[SKIP] {fname} already exists.")
                        continue
                    r = s.get(file_url)
                    saveFile(r, fname)
            os.chdir('..')
        os.chdir('..')

    '''Go back to root when done'''
    os.chdir(root)


'''Base URL'''
url = 'http://ninova.itu.edu.tr'

'''Create a session for cookie management'''
s = requests.Session()

'''Login to ITU account'''
login(s)

'''Get the main page and class links from ninova'''
kampusSoup = getPage(s, url+'/Kampus1')
classLinks = getLinks(kampusSoup, 'ErisimAgaci')

# Course selection step

course_infos = []
for link in classLinks:
    # Try to get the course code from previous <span>
    code = None
    span = link.find_previous('span')
    if span:
        code = span.text.strip()
    # Try to get CRN from link text or nearby text
    crn = None
    # Look for CRN in link text (e.g., 'CRN: 30328')
    crn_match = re.search(r'CRN[:\s]*([0-9]+)', link.text)
    if crn_match:
        crn = crn_match.group(1)
    # If not found, look in previous span
    if not crn and span:
        crn_match = re.search(r'CRN[:\s]*([0-9]+)', span.text)
        if crn_match:
            crn = crn_match.group(1)
    # Fallbacks
    code = code or link.text.strip() or 'Unknown Code'
    crn = crn or 'Unknown CRN'
    course_infos.append((code, crn))

print("\nAvailable courses:")
for idx, (code, crn) in enumerate(course_infos):
    print(f"{idx+1}. {code} (CRN: {crn})")

selected = input("Enter course numbers to download (comma-separated, e.g. 1,3,5): ")
selected_indices = set()
for part in selected.split(','):
    try:
        i = int(part.strip()) - 1
        if 0 <= i < len(classLinks):
            selected_indices.add(i)
    except ValueError:
        continue

selected_links = [classLinks[i] for i in sorted(selected_indices)]

'''Capture parsed classes'''
for link in selected_links:
    captureClass(s, link)
