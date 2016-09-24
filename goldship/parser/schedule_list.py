import re
import bs4


def build(day):
    def parse(page):
        soup = bs4.BeautifulSoup(page, 'lxml')
        res = list()

        for line in soup.find(class_='scheLs').find_all('tr'):
            tds = line.find_all('td')
            if not tds:
                continue
            if re.match("\d*", tds[0].text).group() == str(day):
                res.append(tds[1].a.get('href'))

        return res

    return parse
