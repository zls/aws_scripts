from __future__ import print_function

import boto3

import zones


def _get_rrset(zone_id):
    '''Retrun Resource Record Set for a zone.'''
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


def pprint(args):
    '''Print resource record set for a zone to the console.'''
    zid = zones.find_zone_id(args.zone)
    if zid:
        _pprint_rrset(_get_rrset(zid))
    else:
        print("Could not find zone {0}".format(args.zone))
