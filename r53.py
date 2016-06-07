#!/usr/bin/python

from __future__ import print_function

import boto3
import argparse

def ap_parse_list(args):
    '''Pasrse further list arguments.'''
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    sp_zone = subparsers.add_parser('zones')
    sp_zone.set_defaults(func=print_zones)

    sp_rrset = subparsers.add_parser('rrset')
    sp_rrset.add_argument('zone')
    sp_rrset.set_defaults(func=print_rrset)

    _args = parser.parse_args(args)
    _args.func(_args)


def _get_zones():
    '''Return a list of AWS R53 Hosted Zones.'''
    client = boto3.client('route53')
    ret = client.list_hosted_zones()
    return ret['HostedZones']


def print_zones(args):
    '''Print all zones to console.'''
    for zone in _get_zones():
        print(zone['Name'], zone['Id'])


def _has_root_label(dn):
    '''Check domain name has trailing '.' root label.'''
    if dn.endswith('.'):
        return True
    return False


def _add_root_label(name):
    '''Return domain name with trailing '.' root label.'''
    if not _has_root_label(name):
        return name + '.'
    return name


def _find_zone_id(name):
    '''Get zone id from name.'''
    zones = _get_zones()
    name = _add_root_label(name)
    for zone in zones:
        if zone['Name'] == name:
            return zone['Id']
    return None


def _get_rrset(zone_id):
    client = boto3.client('route53')
    '''Retrun Resource Record Set for a zone.'''
    ret = client.list_resource_record_sets(HostedZoneId=zone_id)
    return ret['ResourceRecordSets']


def _rrset_format(rr):
    '''Format a resource record item.'''
    if rr.get('AliasTarget'):
        info = "AliasTarget: {} [{}]".format(
            rr['AliasTarget']['DNSName'],
            rr['AliasTarget']['EvaluateTargetHealth'])
        ttl = ''
    else:
        info = rr['ResourceRecords'].pop()['Value']
        if len(rr['ResourceRecords']):
            for _ in rr['ResourceRecords']:
                info += '\n{:66}{}'.format('', _['Value'])
        ttl = rr['TTL']
    return "{:50}{:6}{:<10}{:<}".format(
        rr['Name'],
        rr['Type'],
        ttl,
        info)


def _pprint_rrset(rrset):
    '''Pretty print a resource record set.'''
    rrtypes = {}
    for rr in rrset:
        if not rrtypes.get(rr['Type']):
            rrtypes[rr['Type']] = []
        rrtypes[rr['Type']].append(rr)

    PRINT_ORDER = ['SOA', 'NS', 'A', 'CNAME', 'PTR', 'AAAA', 'SPF', 'SRV', 'TXT']
    for _type in PRINT_ORDER:
        if _type in rrtypes:
            for _ in rrtypes[_type]:
                print(_rrset_format(_))


def print_rrset(args):
    '''Print resource record set for a zone to the console.'''
    zid = _find_zone_id(args.zone)
    if zid:
        _pprint_rrset(_get_rrset(zid))
    else:
        print("Could not find zone {0}".format(args.zone))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    sp_list = subparsers.add_parser('list')
    sp_list.set_defaults(func=ap_parse_list)

    args, remain = parser.parse_known_args()
    args.func(remain)
