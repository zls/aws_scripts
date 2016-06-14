from __future__ import print_function

import sys

import click
import pprint

import zones
import rrsets
import func

CTX_SETTINGS = {'help_option_names': ['-h', '--help']}

@click.group(context_settings=CTX_SETTINGS)
def cmd_cli():
    pass


@cmd_cli.group(name='set', context_settings=CTX_SETTINGS)
def cmd_set():
    pass


@cmd_set.command(name='weight', context_settings=CTX_SETTINGS)
@click.option('--verbose', '-v', is_flag=True)
@click.option('--dry-run', '-n', is_flag=True)
@click.option('--append-domain', '-a')
@click.option('--append-to-set-id', '-s')
@click.option('--name-as-set-id-prefix', '-p', is_flag=True, default=False)
@click.argument('weight', type=click.INT)
@click.argument('zone')
@click.argument('name', metavar='<name|set_id>', nargs=-1)
def cmd_set_weight(**kwargs):
    chgs = []
    zid = zones.find_zone_id(kwargs['zone'])
    rrs = rrsets.get_rrset(zid)
    for name in kwargs['name']:
        if kwargs['name_as_set_id_prefix']:
            nam, sid = name, name
        else:
            nam, sid = name.split('|')
        if kwargs['append_domain']:
            nam = func.append_domain(nam, kwargs['append_domain'])
        if kwargs['append_to_set_id']:
            sid += kwargs['append_to_set_id']
        nam = func.add_root_label(nam)
        for rr in rrs:
            if rr['Name'] == nam and rr['SetIdentifier'] == sid:
                rr['Weight'] = kwargs['weight']
                chgs.append({'Action': 'UPSERT', 'ResourceRecordSet': rr})
    if chgs:
        cb = rrsets.change_batch(chgs)
        if kwargs['verbose'] or kwargs['dry_run']:
            pprint.pprint(cb)
        if kwargs['dry_run']:
            print('Dry run only, exiting now.')
            sys.exit(0)
        resp = rrsets.apply_changebatch(zid, cb)
        if not func.change_insync(resp):
            print("Changes are still not insync, please verify")
            sys.exit(1)
        else:
            print("All changes have been applied")
            sys.exit(0)


@cmd_cli.group(name='list', context_settings=CTX_SETTINGS)
def cmd_list():
    pass


@cmd_list.command(name='zones', context_settings=CTX_SETTINGS)
def cmd_list_zones():
    zones.pprint()


@cmd_list.command(name='rrsets', context_settings=CTX_SETTINGS)
@click.option('--verbose', '-v', is_flag=True)
@click.argument('zone')
def cmd_list_rrset(verbose, zone):
    rrsets.pprint(zone, verbose)

if __name__ == '__main__':
    cmd_cli()
