from __future__ import print_function

import click

import zones
import rrsets

@click.group()
def cmd_cli():
    pass

@cmd_cli.group(name='set')
def cmd_set():
    pass

@cmd_set.command(name='weight')
@click.option('--append-domain', '-a')
@click.argument('weight', type=click.INT)
@click.argument('zone')
@click.argument('names', nargs=-1)
def cmd_set_weight():
    pass

@cmd_cli.group(name='list')
def cmd_list():
    pass

@cmd_list.command(name='zones')
def cmd_list_zones():
    zones.pprint()

@cmd_list.command(name='rrsets')
@click.argument('zone')
def cmd_list_rrset(zone):
    rrsets.pprint(zone)

if __name__ == '__main__':
    cmd_cli()
