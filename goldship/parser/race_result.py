import datetime
import re
import bs4
from collections import defaultdict
from logging import getLogger

logger = getLogger(__name__)

regex = dict()
regex['raceTitDay'] = re.compile(
            r"(\d*)年(\d*)月(\d*)日.*?(\d*)回"
            "(.*?)(\d*)日.*?(\d*:\d*)発走")
regex['raceTitMeta'] = re.compile(
                    r"(.+?) (\d+?)m \[コースガイド\]"
                    " \| 天気： \| 馬場： \| (.+?) \| (.+?)"
                    " \| 本賞金：(.+?)万円 \|")
regex['raceNo'] = re.compile(r"(\d*?)R")
regex['number'] = re.compile(r"\d+")
regex['grade'] = re.compile(r"\d+?万下|オープン|新馬|未勝利")
regex['horse_weight'] = re.compile("(\d*)\((.*?)\)")


def __parse_time(raw):
    if raw.count('.') == 1:
        t = datetime.datetime.strptime(raw, '%S.%f').time()
    elif raw.count('.') == 2:
        t = datetime.datetime.strptime(raw, '%M.%S.%f').time()
    else:
        t = None

    return t


def __parse_result(soup, race_id):
    res = []
    records = [line.find_all('td')
               for line in soup.find(id='resultLs').find_all('tr')
               if line.find_all('td')]
    for idx, record in enumerate(records):
        r = {}
        r['race_id'] = race_id
        r['row'] = idx
        r['fp'] = record[0].text.strip()
        r['bk'] = record[1].text.strip()
        r['pp'] = record[2].text.strip()
        r['horse_id'] = regex['number'].findall(record[3].a['href'])[0]
        r['horse_sex'] = record[4].text.strip('0123456789')
        r['horse_age'] = regex['number'].findall(record[4].text)[0]
        r['jockey_id'] = regex['number'].findall(record[5].a['href'])[0]
        r['time'] = __parse_time(record[6].text)
        r['margin'] = record[7].text.strip()

        try:
            r['positions'] = [int(x) for x in
                              record[8].text.strip().split('-')]
        except:
            r['positions'] = None

        r['l3f'] = __parse_time(record[9].text)
        r['jockey_weight'] = float('.'.join(
            regex['number'].findall(record[10].text)))

        try:
            r['horse_weight'], _ = regex['horse_weight'].findall(
                    record[11].text)[0]
        except:
            r['horse_weight'] = None

        try:
            r['fav'] = float(record[12].text)
        except:
            r['fav'] = None

        try:
            r['odds'] = float(record[13].text)
        except:
            r['odds'] = None

        r['blinker'] = record[14].text
        r['trainer_id'] = regex['number'].findall(record[15].a['href'])[0]
        res.append(r)

    return res


def extract_regex(soup, name, arg):
    if arg == "class":
        ret = regex[name].findall(soup.find(class_=name).text)[0]
    elif arg == "id":
        ret = regex[name].findall(soup.find(id=name).text)[0]
    return ret


def __get_grade(name, race_type):
    for grade in ['GIII', 'GII', 'GI']:
        if grade in name:
            return grade
        return regex['grade'].findall(race_type)[0]


def __get_track_info(track_types):
    track = defaultdict(lambda: None)
    if '障害' in track_types:
        track['type'] = '障害'
    else:
        track['type'] = '平地'

    for track_type in track_types:
        if track_type in ['芝', 'ダート', '芝→ダート']:
            track['surface'] = track_type
        elif track_type in ['右', '左', '直線']:
            track['rotation'] = track_type
        elif track_type in ['内', '外', '内->外', '外->内', '外→内', '内2周', '外2周']:
            track['side'] = track_type
    return track


def __check_condition(race_conditions):
    condition = defaultdict(lambda: False)

    condition['local'] = list(filter(
        lambda x: x in race_conditions, ['特指', '（指定）', '[指定]']))
    condition['international'] = list(filter(
        lambda x: x in race_conditions, ['国際', '混合', '父', '九州']))
    condition['weight'] = list(filter(
        lambda x: x in race_conditions, ['定量', '別定', 'ハンデ', '馬齢']))
    condition['jockey'] = list(filter(
        lambda x: x in race_conditions, ['']))

    for k, v in condition.items():
        if not v:
            condition[k] = None
        else:
            condition[k] = v[0].strip('（）')

    return condition


def __parse_race(soup, race_id):
    name = soup.find(class_="fntB").text.strip()
    race_no = extract_regex(soup, "raceNo", "id")
    metas = extract_regex(soup, "raceTitDay", "id")
    year, month, day, place_weeks, place, place_days, time = metas
    metas = extract_regex(soup, "raceTitMeta", "id")
    track_types, meter, race_required, race_condition, prize = metas
    grade = __get_grade(name, race_condition)
    track = __get_track_info(track_types.split('・'))
    condition = __check_condition(race_condition)

    prize = prize.split('、')
    time = time.split(':')

    weather, track_condition = [x['alt'] for x in soup.find_all(class_='spBg')]

    race = {
        "race_id": race_id, "race_no": race_no, "race_name": name,
        "race_weeks": place_weeks, "race_days": place_days,
        "race_grade": grade,
        "race_datetime": datetime.datetime(int(year), int(month), int(day),
                                           int(time[0]), int(time[1])),
        "cond_jockey": condition['jockey'],
        "cond_intl": condition['international'],
        "cond_local": condition['local'], "cond_weight": condition['weight'],
        "cond_age": race_required,
        "track_type": track['type'], "track_surface": track['surface'],
        "track_side": track['side'], "track_rotation": track['rotation'],
        "track_meter": meter,  "track_place": place,
        "track_weather": weather,
        "track_condition": track_condition,
        "prize1": prize[0],
        "prize2": prize[1],
        "prize3": prize[2],
        "prize4": prize[3],
        "prize5": prize[4],
        }
    return race


def __parse_payoff(soup, race_id):
    payoff = soup.find(class_="layoutCol2M")

    keys = [x.text for x in payoff.find_all("th")
            for i in range(int(x.attrs["rowspan"]))]
    v_keys = ['comb', 'yen', 'popularity']
    values = [{v_keys[i]: x.text.strip() for i, x in enumerate(line.find_all("td"))}
              for line in payoff.find_all("tr")]

    for k, v in zip(keys, values):
        if not v['comb']:
            continue
        v['race_id'] = race_id
        v['odds_id'] = v['comb']
        v['kind'] = k
        try:
            v['popularity'] = regex['number'].findall(v['popularity'])[0]
        except:
            logger.warn('popularity is invalid data.')
            v['popularity'] = None
        v['yen'] = ''.join(regex['number'].findall(v['yen']))
        v['comb'] = [int(x) for x in v['comb'].split('－')]

    return [x for x in values if x['comb']]


def parse(page):
    soup = bs4.BeautifulSoup(page, "lxml")
    race_id = regex['number'].findall(
            soup.find(id='raceNaviC').a.attrs['href'])[0]
    logger.info(race_id)
    result = __parse_result(soup, race_id)
    payoff = __parse_payoff(soup, race_id)
    race = __parse_race(soup, race_id)
    return {"race": race, "result": result, "payoff": payoff}
