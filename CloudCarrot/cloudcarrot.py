import re
import sys
import requests
import socket
from bs4 import BeautifulSoup
from termcolor import cprint
from tabulate import tabulate
from pathlib import Path
import emoji
from .modules.dnsdumpster_module import DNSDumpsterAPI
from .modules.censys_module import censys_search_certs
from .modules.shodan_module import shodan_search

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
    def __init__(self, domain, check_open_ports=False):
        self.domain = domain
        self.found_host = set()
        self.found_domain = set()
        self.dnsdumpster_graph = None
        self.open_port_hosts = {}
        self.check_open_ports = check_open_ports

        m = re.match(
            r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$", self.domain)

        if m is None:
            cprint('Enter a valid domain or host. ex. - "site.com"',
                   'red', 'on_grey', attrs=['bold'])
            sys.exit(0)

    def search(self):
        cprint('Trying get data from DNSDumpster.',
               'green', 'on_grey', attrs=['bold'])
        """Search with DNSDumpster"""
        dnsdumpster_data = DNSDumpsterAPI(self.domain).start()
        if not dnsdumpster_data:
            cprint(
                'DNSDumpster return error,'
                'maybe you exceeded api limit.'
                'We skip dnsdumpster search',
                'red', 'on_grey')
        """set dnsdumpster graph image"""
        self.dnsdumpster_graph = dnsdumpster_data['image_data']

        """Search with Censys"""
        cprint('Trying get data from Censys.',
               'green', 'on_grey', attrs=['bold'])
        censys_data = censys_search_certs(self.domain)
        if censys_data is False:
            cprint(
                'Censys return error, maybe you'
                'exceeded api limit or another error.\n'
                'Check your `settings.conf`\n'
                'We skip censys search.',
                'red', 'on_grey')

        """Search with Shodan"""
        cprint('Trying get data from Shodan.',
               'green', 'on_grey', attrs=['bold'])
        shodan_data = shodan_search(self.domain)
        if shodan_data is False:
            cprint(
                'Shodan return error, maybe you'
                'exceeded api limit or another error.\n'
                'Check your `settings.conf`\n'
                'We skip censys search.',
                'red', 'on_grey')

        if censys_data is not None and censys_data is not False:
            self.found_host.update(
                host for host in censys_data if self._check_cloudflare(host))
        if shodan_data is not None and shodan_data is not False:
            self.found_host.update(
                host for host in shodan_data if self._check_cloudflare(host))

        if 'hosts' in dnsdumpster_data['records']:
            self.found_host.update(data_host['ip'] for data_host in dnsdumpster_data['records']
                                   ['hosts'] if self._check_cloudflare(data_host['ip']))
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
            if self.check_open_ports:
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
            else:
                table_headers = ['{} Hosts{} '.format(
                    bcolors.OKBLUE, bcolors.ENDC)]
                table_data = [[host] for host in self.found_host]

        """print table with hosts and port info"""
        print(tabulate(table_data, table_headers, tablefmt="github") + '\n')

        if self.found_domain:
            """print find domains and graph image link"""
            print(tabulate([[domain] for domain in self.found_domain], [
                  '{} Domains {}'.format(bcolors.OKBLUE, bcolors.ENDC)], tablefmt="github") + '\n')
            if not self.dnsdumpster_graph is None:
                cprint('Mapping the domain from dnsdumpster: {}'.format(
                    self.dnsdumpster_graph), 'green', 'on_grey', attrs=['bold'])

    def _check_cloudflare(self, ip):
        http = True
        https = True
        try:
            r = requests.get('http://{}'.format(ip),
                             verify=False, headers=_headers, timeout=10)
        except requests.exceptions.ConnectionError:
            http = False
            pass
        except requests.exceptions.Timeout:
            http = False
            pass

        if not http:
            try:
                r = requests.get('https://{}'.format(ip),
                                 verify=False, headers=_headers, timeout=10)
            except requests.exceptions.ConnectionError:
                https = False
                pass
            except requests.exceptions.Timeout:
                https = False
                pass

        if http or https:
            soup = BeautifulSoup(r.text, 'html.parser')
            if soup.title:
                for title in soup.title:
                    m = re.findall('Cloudflare', title)
                    if len(m):
                        return False
                    if 'Server' in r.headers:
                        if r.headers['Server'] == 'cloudflare':
                            return False
                    return True
            """if we could not get headers"""
            return True
        """if the host is not responding"""
        return True

    def _check_ports(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((host, int(port)))
            s.shutdown(2)
            return True
        except KeyboardInterrupt:
            """ctrl+c - exit app and close sockets"""
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            sys.exit()
        except:
            return False

    def _check_hosts(self):
        cprint('Check main open ports', 'green', 'on_grey', attrs=['bold'])
        self.open_port_hosts = {}
        for host in self.found_host:
            self.open_port_hosts[host] = {}
            for port in _ports:
                self.open_port_hosts[host][port] = {}
                if self._check_ports(host, port):
                    self.open_port_hosts[host][port]['is_open'] = True
                else:
                    self.open_port_hosts[host][port]['is_open'] = False
