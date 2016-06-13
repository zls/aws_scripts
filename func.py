from __future__ import print_function

import boto3
import time
import sys

def has_root_label(dn):
    '''Check domain name has trailing '.' root label.'''
    if dn.endswith('.'):
        return True
    return False


def add_root_label(name):
    '''Return domain name with trailing '.' root label.'''
    if not has_root_label(name):
        return name + '.'
    return name


def append_domain(name, domain):
    '''Return a string with the domain name appended.'''
    domain = add_root_label(domain)
    if domain.startswith('.'):
        return name + domain
    else:
        return name + '.' + domain

def _change_insync(response):
    if response['ChangeInfo']['Status'] == 'INSYNC':
        return True
    else:
        return False


def change_insync(response, checks=7, interval=5):
    if _change_insync(response):
        return True
    client = boto3.client('route53')
    count = 0
    insync = False
    while count <= checks:
        resp = client.get_change(Id=response['ChangeInfo']['Id'])
        insync = _change_insync(resp)
        if insync:
            break
        count += 1
        time.sleep(interval)
    return insync
