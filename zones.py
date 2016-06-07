from __future__ import print_function

import boto3

import func

def find_zone_id(name):
    '''Return zone id from name.'''
    zones = get_zones()
    name = func.add_root_label(name)
    for zone in zones:
        if zone['Name'] == name:
            return zone['Id']
    return None


def get_zones():
    '''Return a list of AWS R53 Hosted Zones.'''
    client = boto3.client('route53')
    ret = client.list_hosted_zones()
    return ret['HostedZones']


def pprint(args):
    '''Print all zones to console.'''
    for zone in get_zones():
        print(zone['Name'], zone['Id'])
