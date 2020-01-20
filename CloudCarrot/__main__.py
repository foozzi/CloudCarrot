import re
import sys
import cfscrape
import requests
import socket
from bs4 import BeautifulSoup
from termcolor import colored, cprint
from tabulate import tabulate
import emoji
from modules.dnsdumpster import DNSDumpsterAPI
from modules.censys import censys_search_certs
from modules.shodan import shodan_search

_ports = ['443', '80', '21', '22']
_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CloudCarrot:
    def __init__(self, domain):
        self.domain = domain
        self.scrap_title = None
        self.found_host = set()
        self.found_domain = set()
        self.dnsdumpster_graph = None
        self.open_port_hosts = {}

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
            cprint('We have problem with url or connection,'
                   'check your proxy or VPN connection for blocking.',
                   'red', 'on_grey', attrs=['bold'])
            sys.exit(0)

    def search(self):
        """Search with dnsdumpster.com"""
        dnsdumpster_data = DNSDumpsterAPI(self.domain).start()
        if not dnsdumpster_data:
            cprint(
                'DNSDumpster return error,'
                'maybe you exceeded api limit.'
                'We skip dnsdumpster search',
                'red', 'on_grey')
        """set dnsdumpster graph image"""
        self.dnsdumpster_graph = dnsdumpster_data['image_data']

        censys_data = censys_search_certs(self.domain)
        if censys_data is False:
            cprint(
                'Censys return error, maybe you'
                'exceeded api limit or another error.\n'
                'Check your `settings.conf`\n'
                'We skip censys search.',
                'red', 'on_grey')

        shodan_data = shodan_search(self.scrap_title)
        if shodan_data is False:
            cprint(
                'Shodan return error, maybe you'
                'exceeded api limit or another error.\n'
                'Check your `settings.conf`\n'
                'We skip censys search.',
                'red', 'on_grey')

        if not censys_data is None and not censys_data:
            self.found_host.update(censys_data)
        if not shodan_data is None and not shodan_data:
            self.found_host.update(shodan_data)

        if 'hosts' in dnsdumpster_data['records']:
            self.found_host.update(data_host['ip'] for data_host in dnsdumpster_data['records']
                                   ['hosts'] if data_host['ip'] not in self.found_host)
            """subdomains from dnsdumpster"""
            self.found_domain.update(
                data_host['domain'] for data_host in dnsdumpster_data['records']['hosts'])

        self.found_host = list(set(self.found_host))
        if len(self.found_host) < 1:
            self.found_host = False
            cprint('We tried but didn’t find any hosts...')
        if len(self.found_domain) < 1:
            self.found_domain = False
            cprint('We tried but didn’t find any domains...')

        if self.found_host:
            self._check_hosts()

            table_headers = ['{} Hosts {}'.format(
                bcolors.OKBLUE, bcolors.ENDC)] + [bcolors.OKBLUE + port + bcolors.ENDC for port in _ports]
            table_data = []
            for h in self.open_port_hosts:
                table_data.append([
                    h,
                    emoji.emojize(':carrot:') if self.open_port_hosts[h]['443']['is_open'] is True else emoji.emojize(
                        ':no_entry:'),
                    emoji.emojize(':carrot:') if self.open_port_hosts[h]['80']['is_open'] is True else emoji.emojize(
                        ':no_entry:'),
                    emoji.emojize(':carrot:') if self.open_port_hosts[h]['21']['is_open'] is True else emoji.emojize(
                        ':no_entry:'),
                    emoji.emojize(':carrot:') if self.open_port_hosts[h]['22']['is_open'] is True else emoji.emojize(':no_entry:')])

            """print table with hosts and port info"""
            print(tabulate(table_data, table_headers) + '\n')

        if self.found_domain:
            """print find domains and graph image link"""
            print(tabulate([[domain] for domain in self.found_domain], [
                  '{} Domains {}'.format(bcolors.OKBLUE, bcolors.ENDC)]) + '\n')
            # if not self.dnsdumpster_graph is None:
            #    cprint('Mapping the domain from dnsdumpster: {}'.format(
            #        self.dnsdumpster_graph), 'green', 'on_grey', attrs=['bold'])

    def _check_ports(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((host, int(port)))
            s.shutdown(2)
            return True
        except:
            return False

    def _check_hosts(self):
        self.open_port_hosts = {}
        for host in self.found_host:
            self.open_port_hosts[host] = {}
            """simple check open ports"""
            for port in _ports:
                self.open_port_hosts[host][port] = {}
                if self._check_ports(host, port):
                    self.open_port_hosts[host][port]['is_open'] = True
                else:
                    self.open_port_hosts[host][port]['is_open'] = False


CloudCarrot('alphapay24.com').search()
