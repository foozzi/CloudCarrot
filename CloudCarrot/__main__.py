import re
import sys
import cfscrape
import requests
from bs4 import BeautifulSoup
from termcolor import colored, cprint
from modules.dnsdumpster import DNSDumpsterAPI
from modules.censys import censys_search_certs
from modules.shodan import shodan_search

_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}


class CloudCarrot:
    def __init__(self, domain):
        self.domain = domain
        self.scrap_title = None

        m = re.match(
            r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$", self.domain)

        if m is None:
            cprint('Enter a valid domain or host. ex. - "site.com"',
                   'red', 'on_grey', attrs=['bold'])
            sys.exit(0)

        try:
            scraper = cfscrape.create_scraper()
            cf_scap_data = scraper.get(
                'http://{}'.format(self.domain), headers=_headers)
        except requests.exceptions.MissingSchema:
            cprint('Enter a valid domain or host. ex. - "site.com"',
                   'red', 'on_grey', attrs=['bold'])
            sys.exit(0)

        if cf_scap_data.status_code == 200:
            soup = BeautifulSoup(cf_scap_data.text, 'html.parser')
            for title in soup.title:
                self.scrap_title = title
                break
        else:
            cprint('We have problem with url or connection',
                   'red', 'on_grey', attrs=['bold'])
            sys.exit(0)

    def search(self):
        """Search with dnsdumpster.com"""
        #dnsdumpster_data = DNSDumpsterAPI(self.domain).start()
        # if not dnsdumpster_data:
        #    cprint(
        #        'DNSDumpster return error,'
        #        'maybe you exceeded api limit.'
        #        'we skip dnsdumpster search',
        #        'red', 'on_grey')

        #censys_data = censys_search_certs(self.domain)
        # if not censys_data:
        #    cprint(
        #            'Censys return error, maybe you'
        #            'exceeded api limit or another error'
        #            'we skip censys search.',
        #            'red', 'on_grey')

        #shodan_data = shodan_search(self.scrap_title)
        # if not shodan_data:
        #    cprint(
        #            'Shodan return error, maybe you'
        #            'exceeded api limit or another error'
        #            'we skip censys search.',
        #            'red', 'on_grey')

        sys.exit(0)


CloudCarrot('7money.co').search()
