from shodan import Shodan
from pathlib import Path
import configparser
import requests

try:
    config = configparser.ConfigParser()
    config.read(Path("settings.conf").absolute())
    TOKEN = config.get('shodan', 'API_KEY')
except configparser.NoSectionError:
    TOKEN = False

api = Shodan(TOKEN)


def shodan_search(word):
    if not TOKEN:
        return False
    try:
        banner = api.search_cursor('http.title:"{0}"'.format(word))
        title_result = set([host['ip_str'] for host in banner])
        if title_result:
            return title_result
        else:
            return set()
    except:
        return False
