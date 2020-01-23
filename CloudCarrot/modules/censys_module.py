import censys.certificates
import sys
import censys.ipv4
from pathlib import Path
import configparser

config = configparser.ConfigParser()
try:
    config.read(Path("settings.conf").absolute())
    SECRET = config.get('censys', 'SECRET')
    API_ID = config.get('censys', 'API_ID')
except configparser.NoSectionError:
    API_ID = False
    SECRET = False


def censys_search_certs(host):
    if not API_ID or not SECRET:
        return False
    try:
        certificates = censys.certificates.CensysCertificates(
            api_id=API_ID, api_secret=SECRET)

        cert_query = certificates.search(
            "parsed.names: {0} AND tags.raw: trusted AND NOT parsed.names: cloudflaressl.com".format(host))
        result = set([cert['parsed.fingerprint_sha256']
                      for cert in cert_query])
        hosts_query = censys.ipv4.CensysIPv4(api_id=API_ID, api_secret=SECRET)
        hosts = ' OR '.join(result)
        if hosts:
            searching = hosts_query.search(hosts)
            host_result = set([search_result['ip']
                               for search_result in searching])
            return host_result
        else:
            return []
    except:
        return False
