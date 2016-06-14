from __future__ import print_function

import sys

import click
import pprint

import zones
import rrsets
import func

EXIT_OK = 0
EXIT_PENDING = 1
EXIT_BAD_OPT = 10

CTX_SETTINGS = {'help_option_names': ['-h', '--help']}

@click.group(context_settings=CTX_SETTINGS)
def cmd_cli():
    pass


@cmd_cli.group(name='set', context_settings=CTX_SETTINGS)
def cmd_set():
    pass


@cmd_set.command(name='weight', context_settings=CTX_SETTINGS)
@click.option('--verbose', '-v', is_flag=True, help='Print out change batch')
@click.option('--dry-run', '-n', is_flag=True, help='Do not apply change batch, implies -v')
@click.option('--append-domain', '-a', help='Append domain name to RR names')
@click.option('--use-zone-name', '-z', is_flag=True, help='Append zone name to RR names')
@click.option('--append-to-set-id', '-s', help='Append value to SetIdentifiers')
@click.option('--name-as-set-id-prefix', '-p', is_flag=True, default=False, help='Use the RR name value as the SetIdentifier')
@click.argument('weight', type=click.INT)
@click.argument('zone')
@click.argument('name', metavar='NAME [NAME...]', nargs=-1)
def cmd_set_weight(**kwargs):
    '''
    Arguments:

    \b
        weight: The value to set the weight to.
        zone:   AWS Hosted Zone that record is found in.
        name:   The name of the resource record (RR) to operate on. Use a pipe
                character '|' to separate the NAME|SET_ID portions.
                Ex. 'www.example.com|www-frontlb01'

    Example:

        r53 set weight -pz -s '-frontlb01' 0 example.com www api

    '''
    chgs = []
    zid = zones.find_zone_id(kwargs['zone'])
    rrs = rrsets.get_rrset(zid)
    for name in kwargs['name']:

        if kwargs['name_as_set_id_prefix']:
            nam, sid = name, name
        else:
            nam, sid = name.split('|')

        if kwargs['append_domain'] and kwargs['use_zone_name']:
            click.echo('ERROR: --append-domain and --use-zone-name are mutually exclusive options.',
                       err=True)
            sys.exit(EXIT_BAD_OPT)
        elif kwargs['append_domain']:
            nam = func.append_domain(nam, kwargs['append_domain'])
        elif kwargs['use_zone_name']:
            nam = func.append_domain(nam, kwargs['zone'])

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
            click.echo('Dry run only, exiting now.')
            sys.exit(EXIT_OK)

        resp = rrsets.apply_changebatch(zid, cb)
        if not func.change_insync(resp):
            click.echo('Changes are still not insync, please verify', err=True)
            sys.exit(EXIT_PENDING)
        else:
            click.echo('All changes have been applied')
            sys.exit(EXIT_OK)


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
