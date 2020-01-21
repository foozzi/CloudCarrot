import argparse
import sys
from .cloudcarrot import CloudCarrot, bcolors
from .settings import __version__


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', required=False, action='store_true')
    parser.add_argument(
        '-u', '--host', help='Domain or host for detecting', default='')

    return parser


def main():
    parser = create_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    if parser.parse_args().version is True:
        parser.exit(0, bcolors.OKBLUE +
                    'CloudCarrot {}\n'.format(__version__) + bcolors.ENDC)

    CloudCarrot(parser.parse_args().host).search()


if __name__ == '__main__':
    main()
