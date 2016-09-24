import staygold
from itertools import chain
from goldship import parser
from goldship import storer
from logging import getLogger

logger = getLogger(__name__)


def race_result(year, month, day):
    logger.info('year={}, month={}, day={}'.format(year, month, day))
    BASE_URL = 'http://keiba.yahoo.co.jp'
    race_list_paths = list()

    logger.info('Scraping race list urls from schedule list...')
    staygold.run(
        urls=['{}/schedule/list/{}/?month={}'.format(BASE_URL, year, month)],
        parse=parser.schedule_list.build(day=day),
        store=lambda x: race_list_paths.append(x)
    )
    logger.info('race list paths: {}'.format(race_list_paths))

    race_list_urls = ["{}/{}".format(BASE_URL, path)
                      for path in chain.from_iterable(race_list_paths)]

    race_result_paths = list()

    logger.info('Scraping race result urls from race list...')
    staygold.run(
        urls=race_list_urls,
        parse=parser.race_list.parse,
        store=lambda x: race_result_paths.append(x)
    )
    logger.info('race result paths: {}'.format(race_result_paths))

    race_result_urls = ["{}/{}".format(BASE_URL, path)
                        for path in chain.from_iterable(race_result_paths)]

    logger.info('Scraping race result, payoff, meta from race result...')
    staygold.run(
        urls=race_result_urls,
        parse=parser.race_result.parse,
        store=storer.race_result.store
    )
    logger.info('Done')
