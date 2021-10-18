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

# Example output (reduced to one media device, serial number replaced)
# .1.3.6.1.4.1.14851.3.1.6.2.1.1.1 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.6.2.1.2.1 = INTEGER: 3
# .1.3.6.1.4.1.14851.3.1.6.2.1.3.1 = STRING: "IBM     03592E07        000X123456"
# .1.3.6.1.4.1.14851.3.1.6.2.1.4.1 = STRING: "deprecated"
# .1.3.6.1.4.1.14851.3.1.6.2.1.5.1 = INTEGER: 3
# .1.3.6.1.4.1.14851.3.1.6.2.1.6.1 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.6.2.1.7.1 = Hex-STRING: 00 00 00 00 00 00 1A 74
# .1.3.6.1.4.1.14851.3.1.6.2.1.8.1 = STRING: "50 05 07 63 0F 12 21 01"
# .1.3.6.1.4.1.14851.3.1.6.2.1.9.1 = Hex-STRING: 00 00 00 00 00 00 6B D9
# .1.3.6.1.4.1.14851.3.1.6.2.1.10.1 = Hex-STRING: 00 00 00 00 00 00 6B D9
# .1.3.6.1.4.1.14851.3.1.6.2.1.11.1 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.6.2.1.12.1 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.6.2.1.13.1 = INTEGER: 1

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


def get_snia_sml_media_devices_need_cleaning(value):
    result = {
        '0': (2, 'unknown'),
        '1': (0, 'true'), # Cleaning is an automated process so it should always be OK
        '2': (0, 'false'),
    }.get(value, (3, 'unimplemented'))
    return Result(state=State(result[0]), summary='Need cleaning: ' + result[1])


def get_snia_sml_media_devices_object_type(value):
    return Result(state=State.OK, summary='Type: ' + {
        '0': 'unknown',
        '1': 'wormDrive',
        '2': 'magnetoOpticalDrive',
        '3': 'tapeDrive',
        '4': 'dvdDrive',
        '5': 'cdromDrive',
    }.get(value, 'unimplemented'))


def parse_snia_sml_media_devices(string_table):
    section = {}
    for index, *data in string_table[0]:
        section[index] = data
    return section


register.snmp_section(
    name="snia_sml_media_devices",
    parse_function=parse_snia_sml_media_devices,
    detect=contains(".1.3.6.1.2.1.1.1.0", ".1.3.6.1.4.1.2.6.182"),
    fetch=[
        SNMPTree(
          base=".1.3.6.1.4.1.14851.3.1.6.2.1",
          oids=[
              "1",  # mediaAccessDeviceIndex
              "2",  # mediaAccessDeviceObjectType
              "5",  # mediaAccessDevice-Availability
              "6",  # mediaAccessDevice-NeedsCleaning
              "11", # mediaAccessDevice-OperationalStatus
          ]),
    ]
)


def discovery_snia_sml_media_devices(section):
    for index in section:
        yield Service(item=index)


def check_snia_sml_media_devices(item, section):
    data = section.get(item)
    if data is None:
        return

    (object_type, availability, need_cleaning, opstatus) = data

    yield get_snia_sml_opstatus(opstatus)
    yield get_snia_sml_availability(availability)
    yield get_snia_sml_media_devices_object_type(object_type)
    yield get_snia_sml_media_devices_need_cleaning(need_cleaning)



register.check_plugin(
    name="snia_sml_media_devices",
    service_name="Drive %s",
    discovery_function=discovery_snia_sml_media_devices,
    check_function=check_snia_sml_media_devices,
)

