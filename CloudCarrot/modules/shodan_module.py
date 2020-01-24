from shodan import Shodan
from pathlib import Path
import configparser
import requests
from CloudCarrot.settings import __config_file__
import os

config = configparser.ConfigParser()
try:
    config.read(os.path.join(str(Path.home()),
                             '.config/{}'.format(__config_file__)))
    TOKEN = config.get('shodan', 'API_KEY')
except configparser.NoSectionError:
    TOKEN = False

api = Shodan(TOKEN)


def shodan_search(host):
    if not TOKEN:
        return False
    try:
        banner = api.search_cursor('"{0}"'.format(host))
        title_result = set([host['ip_str'] for host in banner])
        if title_result:
            return title_result
        else:
            return set()
    except:
        return False
