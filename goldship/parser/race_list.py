import bs4


def parse(page):
    soup = bs4.BeautifulSoup(page, 'lxml')
    res = list()

    for line in soup.find(class_='scheLs').find_all('tr'):
        tds = line.find_all('td')
        if not tds:
            continue
        if not tds[0].p:
            continue
        res.append(tds[1].a.get('href'))

    return res
