from shodan import Shodan
import configparser
import requests

try:
    config = configparser.ConfigParser()
    config.read("settings.conf")
    TOKEN = config.get('shodan', 'token')
except configparser.NoSectionError:
    TOKEN = 'cNopDantGXFJq6187snCeEryr4ThAVQK'

api = Shodan(TOKEN)


def shodan_search(word):
    try:
        banner = api.search_cursor('http.title:"{0}"'.format(word))
        title_result = set([host['ip_str'] for host in banner])
        if title_result:
            return title_result
    except:
        return False
