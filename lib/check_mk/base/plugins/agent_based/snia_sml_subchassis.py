#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

# Example output (serial numbers replaced)
# .1.3.6.1.4.1.14851.3.1.4.10.1.1.1 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.4.10.1.1.2 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.4.10.1.1.3 = INTEGER: 3
# .1.3.6.1.4.1.14851.3.1.4.10.1.2.1 = STRING: "IBM"
# .1.3.6.1.4.1.14851.3.1.4.10.1.2.2 = STRING: "IBM"
# .1.3.6.1.4.1.14851.3.1.4.10.1.2.3 = STRING: "IBM"
# .1.3.6.1.4.1.14851.3.1.4.10.1.3.1 = STRING: "3584L23"
# .1.3.6.1.4.1.14851.3.1.4.10.1.3.2 = STRING: "3584D23"
# .1.3.6.1.4.1.14851.3.1.4.10.1.3.3 = STRING: "3584D23"
# .1.3.6.1.4.1.14851.3.1.4.10.1.4.1 = STRING: "X123456"
# .1.3.6.1.4.1.14851.3.1.4.10.1.4.2 = STRING: "X234567"
# .1.3.6.1.4.1.14851.3.1.4.10.1.4.3 = STRING: "X345678"
# .1.3.6.1.4.1.14851.3.1.4.10.1.5.1 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.4.10.1.5.2 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.4.10.1.5.3 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.4.10.1.6.1 = INTEGER: 0
# .1.3.6.1.4.1.14851.3.1.4.10.1.6.2 = INTEGER: 0
# .1.3.6.1.4.1.14851.3.1.4.10.1.6.3 = INTEGER: 0
# .1.3.6.1.4.1.14851.3.1.4.10.1.7.1 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.4.10.1.7.2 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.4.10.1.7.3 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.4.10.1.8.1 = STRING: "IBM 3584L23 X123456"
# .1.3.6.1.4.1.14851.3.1.4.10.1.8.2 = STRING: "IBM 3584D23 X234567"
# .1.3.6.1.4.1.14851.3.1.4.10.1.8.3 = STRING: "IBM 3584D23 X345678"
# .1.3.6.1.4.1.14851.3.1.4.10.1.9.1 = STRING: "3584L23 X123456"
# .1.3.6.1.4.1.14851.3.1.4.10.1.9.2 = STRING: "3584D23 X234567"
# .1.3.6.1.4.1.14851.3.1.4.10.1.9.3 = STRING: "3584D23 X345678"
# .1.3.6.1.4.1.14851.3.1.4.10.1.10.1 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.4.10.1.10.2 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.4.10.1.10.3 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.4.10.1.11.1 = INTEGER: 17
# .1.3.6.1.4.1.14851.3.1.4.10.1.11.2 = INTEGER: 18
# .1.3.6.1.4.1.14851.3.1.4.10.1.11.3 = INTEGER: 18

from .agent_based_api.v1 import (
    SNMPTree,
    register,
    Service,
    Result,
    State,
    all_of,
    contains,
)


from .utils.snia_sml import (
    get_snia_sml_opstatus,
    get_snia_sml_availability,
)


def get_snia_sml_subchassis_pkgtype(value):
    return Result(state=State.OK, summary='Type: ' + {
        '0':      'unknown',
        '17':     'mainSystemChassis',
        '18':     'expansionChassis',
        '19':     'subChassis',
        '32769':  'serviceBay',
    }.get(value, 'unimplemented'))


def parse_snia_sml_subchassis(string_table):
    section = {}
    for index, *data in string_table[0]:
        section[index] = data
    return section


register.snmp_section(
    name="snia_sml_subchassis",
    parse_function=parse_snia_sml_subchassis,
    detect=contains(".1.3.6.1.2.1.1.1.0", ".1.3.6.1.4.1.2.6.182"),
    fetch=[
        SNMPTree(
          base=".1.3.6.1.4.1.14851.3.1.4.10.1",
          oids=[
		"1",  # subChassisIndex
		"3",  # subChassis-Model
		"4",  # subChassis-SerialNumber
		"10", # subChassis-OperationalStatus
		"11", # subChassis-PackageType
          ]),
    ]
)


def discovery_snia_sml_subchassis(section):
    for index in section:
        yield Service(item=index)


def check_snia_sml_subchassis(item, section):
    data = section.get(item)
    if data is None:
        return

    (model, serial, opstatus, pkgtype ) = data

    yield get_snia_sml_opstatus(opstatus)
    yield Result(state=State.OK, summary='Model: {model}')
    yield get_snia_sml_subchassis_pkgtype(pkgtype)
    yield Result(state=State.OK, summary='S/N: {serial}')


register.check_plugin(
    name="snia_sml_subchassis",
    service_name="Subchassis %s",
    discovery_function=discovery_snia_sml_subchassis,
    check_function=check_snia_sml_subchassis,
)

