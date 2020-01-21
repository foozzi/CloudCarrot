import requests
from bs4 import BeautifulSoup
import sys
import re
import base64

_URL = "https://dnsdumpster.com/"
_API_KEY_IMAGE_HOSTING = 'cc88f7f179186ec599daf4227123e522'


class Error(Exception):
    pass


class IncorrectHostError(Error):
    """Error in host name or domain"""
    pass


class ApiLimitError(Error):
    """Rate limit dnsdumpster"""
    pass


class DNSDumpsterAPI:

    def __init__(self, host=''):
        self.session = requests.Session()
        self.token = None
        self.host = host

        self.data = {}

        if not self._receive_middleware():
            return None

    def _receive_middleware(self):
        r = self.session.get(_URL)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            csrf_middleware = soup.findAll(
                'input', attrs={'name': 'csrfmiddlewaretoken'})[0]['value']
        except IndexError:
            return False

        self.token = csrf_middleware.strip()

    def _receive_data_from_table(self, table):
        res = []
        trs = table.findAll('tr')
        self.headers = ["Domain", "IP", "Reverse dns",
                        "AS", "Provider", "Country"]
        self.table_cli = []
        for tr in trs:
            tds = tr.findAll('td')
            pattern_ip = r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'
            try:
                ip = re.findall(pattern_ip, tds[1].text)[0]
                domain = str(tds[0]).split('<br/>')[0].split('>')[1]
                header = ' '.join(tds[0].text.replace('\n', '').split(' ')[1:])
                reverse_dns = tds[1].find('span', attrs={}).text

                additional_info = tds[2].text
                country = tds[2].find('span', attrs={}).text
                autonomous_system = additional_info.split(' ')[0]
                provider = ' '.join(additional_info.split(' ')[1:])
                provider = provider.replace(country, '')

                data = {'domain': domain,
                        'ip': ip,
                        'reverse_dns': reverse_dns,
                        'as': autonomous_system,
                        'provider': provider,
                        'country': country,
                        'header': header}

                """Generate pretty table"""
                self.table_cli.append(
                    [domain, ip, reverse_dns, autonomous_system, provider, country])

                res.append(data)
            except Exception:
                """pass if we don't have some table with info about host"""
                pass
        return res

    def start(self):
        cookies = {'csrftoken': self.token}
        data = {'targetip': self.host, 'csrfmiddlewaretoken': self.token}
        headers = {'Referer': _URL}
        r = self.session.post(_URL, cookies=cookies,
                              data=data, headers=headers)
        if r.status_code != 200:
            r.raise_for_status()

        if 'There was an error getting results' in r.text:
            return False
        if 'Too many requests from your IP address' in r.text:
            return False

        soup = BeautifulSoup(r.text, 'html.parser')
        main_tables = soup.findAll('table')

        self.data['records'] = {}
        self.data['records']['dns'] = self._receive_data_from_table(
            main_tables[0])
        self.data['records']['mx'] = self._receive_data_from_table(
            main_tables[1])
        self.data['records']['txt'] = self._receive_data_from_table(
            main_tables[2])
        self.data['records']['hosts'] = self._receive_data_from_table(
            main_tables[3])

        try:
            tmp_url = 'https://dnsdumpster.com/static/map/{}.png'.format(
                self.host)
            image_data = self.session.get(tmp_url)
            if image_data.status_code == 200:
                r = requests.post(
                    'https://api.imgbb.com/1/upload?key={}'.format(
                        _API_KEY_IMAGE_HOSTING),
                    data={'image': tmp_url})
                if r.status_code == 200:
                    self.data['image_data'] = r.json()['data']['url']
        finally:
            if 'image_data' not in self.data:
                self.data['image_data'] = None

        return self.data
