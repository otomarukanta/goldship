from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
import json
import os
from kurofune import RaceMeta, RaceResult, RacePayoff

with open('{}/goldship/conf/engine.json'.format(
          os.getenv('XDG_CONFIG_HOME'))) as f:
    ENGINE = create_engine(URL(**json.load(f)))


def store(data):
    session = sessionmaker(bind=ENGINE)()
    session.merge(RaceMeta(**data['race']))
    [session.merge(RaceResult(**x)) for x in data['result']]
    [session.merge(RacePayoff(**x)) for x in data['payoff']]
    session.commit()
