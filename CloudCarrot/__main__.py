import argparse
import sys
import os
from pathlib import Path
from .cloudcarrot import CloudCarrot, bcolors
from .settings import __version__, __config_file__


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', required=False, action='store_true')
    parser.add_argument(
        '-u', '--host', help='Domain or host for detecting', default='')
    parser.add_argument('--check_open_ports', help='Check for standard open host ports',
                        required=False, action='store_true')

    return parser


def main():
    parser = create_parser()
    if os.name == 'posix':
        _config_path = os.path.join(str(Path.home()), '.config')
        if os.path.exists(_config_path):
            if not os.path.exists(os.path.join(_config_path, __config_file__)):
                with open(os.path.join(_config_path, __config_file__), 'w') as f:
                    f.write(open(Path('settings.conf').absolute(), 'r').read())
        else:
            parser.exit(
                0, '{}{} directory not found, please create it for '
                'cloudcarrot to work properly{}\n'
                .format(bcolors.WARNING, _config_path, bcolors.ENDC))

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    if parser.parse_args().version is True:
        parser.exit(0, bcolors.OKBLUE +
                    'CloudCarrot {}\n'.format(__version__) + bcolors.ENDC)

    CloudCarrot(parser.parse_args().host,
                parser.parse_args().check_open_ports).search()


if __name__ == '__main__':
    main()
