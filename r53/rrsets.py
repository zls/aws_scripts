from __future__ import print_function

import boto3
import pprint as pretty_print

import zones

_FMT_SPEC = '{:50}{:6}{:<4}{:<10}{:<}'
_PRINT_ORDER = ['SOA', 'NS', 'A', 'CNAME', 'PTR', 'AAAA', 'SPF', 'SRV', 'TXT']
_HEADERS = ['Name', 'Type', 'Wt.', 'TTL', 'Value']


def get_rrset(zone_id):
    '''Return Resource Record Set for a zone.'''
    client = boto3.client('route53')
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
                info += '\n{:70}{}'.format('', _['Value'])
        ttl = rr['TTL']
    return _FMT_SPEC.format(
        rr['Name'],
        rr['Type'],
        rr.get('Weight', ''),
        ttl,
        info)


def _pprint_rrset(rrset):
    '''Pretty print a resource record set.'''
    rrtypes = {}
    for rr in rrset:
        if not rrtypes.get(rr['Type']):
            rrtypes[rr['Type']] = []
        rrtypes[rr['Type']].append(rr)

    print(_FMT_SPEC.format(*_HEADERS))
    for _type in _PRINT_ORDER:
        if _type in rrtypes:
            for _ in rrtypes[_type]:
                print(_rrset_format(_))


def pprint(zone, verbose):
    '''Print resource record set for a zone to the console.'''
    zid = zones.find_zone_id(zone)
    if zid:
        info = get_rrset(zid)
        if verbose:
            pretty_print.pprint(info)
        else:
            _pprint_rrset(info)
    else:
        print("Could not find zone {0}".format(zone))


def change_batch(chgs):
    cb = {}
    cb['Changes'] = chgs
    return cb


def apply_changebatch(zid, cb):
    '''Update route 53 zone.'''
    client = boto3.client('route53')
    try:
        resp = client.change_resource_record_sets(
            HostedZoneId=zid,
            ChangeBatch=cb)
    except Exception as err:
        print(cb)
        print(err)
    return resp
