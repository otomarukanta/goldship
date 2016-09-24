import os
import yaml
from logging.config import dictConfig


with open('{}/goldship/conf/logger.yml'.format(
            os.getenv('XDG_CONFIG_HOME'))) as f:
    dictConfig(yaml.load(f))
