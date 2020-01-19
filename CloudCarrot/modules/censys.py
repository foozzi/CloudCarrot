import censys.certificates
import censys.ipv4
import configparser

config = configparser.ConfigParser()
try:
    config.read("settings.conf")
    TOKEN = config.get('censys', 'token')
    UID = config.get('censys', 'uid')
except configparser.NoSectionError:
    UID = '0b327c2b-d37c-4006-85af-ff736a6ca3fb'
    TOKEN = 'VocEkMyECnZ2idvZao0YKcMv2lXV7mxm'

def censys_search_certs(host):
    try:
        certificates = censys.certificates.CensysCertificates(api_id=UID, api_secret=TOKEN)

        cert_query = certificates.search("parsed.names: {0} AND tags.raw: trusted AND NOT parsed.names: cloudflaressl.com".format(host))        
        result = set([cert['parsed.fingerprint_sha256'] for cert in cert_query])        
        hosts_query = censys.ipv4.CensysIPv4(api_id=UID, api_secret=TOKEN)
        hosts = ' OR '.join(result)
        if hosts:
            searching = hosts_query.search(hosts)
            host_result = set([ search_result['ip'] for search_result in searching ])
            return host_result
    except:
        return False
