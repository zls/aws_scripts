from __future__ import print_function

import argparse

import zones
import rrsets


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    sp_list = subparsers.add_parser('list')
    sp_list.set_defaults(func=_parse_list)

    args, remain = parser.parse_known_args()
    args.func(remain)


def _parse_list(args):
    '''Pasrse further list arguments.'''
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    sp_zone = subparsers.add_parser('zones')
    sp_zone.set_defaults(func=zones.pprint)

    sp_rrset = subparsers.add_parser('rrset')
    sp_rrset.add_argument('zone')
    sp_rrset.set_defaults(func=rrsets.pprint)

    _args = parser.parse_args(args)
    _args.func(_args)

