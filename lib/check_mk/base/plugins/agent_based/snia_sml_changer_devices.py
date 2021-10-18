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

# Example output
# .1.3.6.1.4.1.14851.3.1.11.2.1.1.1 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.11.2.1.1.2 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.11.2.1.2.1 = STRING: "50 05 07 63 0F 12 21 01"
# .1.3.6.1.4.1.14851.3.1.11.2.1.2.2 = STRING: "50 05 07 63 0F 12 21 11"
# .1.3.6.1.4.1.14851.3.1.11.2.1.3.1 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.11.2.1.3.2 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.11.2.1.4.1 = STRING: "Logical_Library: TSM"
# .1.3.6.1.4.1.14851.3.1.11.2.1.4.2 = STRING: "Logical_Library: LIB0020"
# .1.3.6.1.4.1.14851.3.1.11.2.1.5.1 = STRING: "TSM"
# .1.3.6.1.4.1.14851.3.1.11.2.1.5.2 = STRING: "LIB0020"
# .1.3.6.1.4.1.14851.3.1.11.2.1.6.1 = STRING: "Library partition is assigned 12 drives and up to 500 cartridges."
# .1.3.6.1.4.1.14851.3.1.11.2.1.6.2 = STRING: "Library partition is assigned 6 drives and up to 500 cartridges."
# .1.3.6.1.4.1.14851.3.1.11.2.1.8.1 = INTEGER: 3
# .1.3.6.1.4.1.14851.3.1.11.2.1.8.2 = INTEGER: 3
# .1.3.6.1.4.1.14851.3.1.11.2.1.9.1 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.11.2.1.9.2 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.11.2.1.10.1 = INTEGER: 0
# .1.3.6.1.4.1.14851.3.1.11.2.1.10.2 = INTEGER: 0

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


def get_snia_sml_changer_devices_flip_supported(value):
    return Result(state=State.OK, summary="Media flip supported: " + {
        "1": "true",
        "2": "false",
    }.get(value, "unimplemented"))


def parse_snia_sml_changer_devices(string_table):
    section = {}
    for index, *data in string_table[0]:
        section[index] = data
    return section


register.snmp_section(
    name="snia_sml_changer_devices",
    parse_function=parse_snia_sml_changer_devices,
    detect=contains(".1.3.6.1.2.1.1.1.0", ".1.3.6.1.4.1.2.6.182"),
    fetch=[
        SNMPTree(
          base=".1.3.6.1.4.1.14851.3.1.11.2.1",
          oids=[
              "1", # changerDeviceIndex
              "3", # changerDevice-MediaFlipSupported
              "4", # changerDevice-ElementName
              "8", # changerDevice-Availability
              "9", # changerDevice-OperationalStatus
          ]),
    ]
)


def discovery_snia_sml_changer_devices(section):
    for index in section:
        yield Service(item=index)


def check_snia_sml_changer_devices(item, section):
    data = section.get(item)
    if data is None:
        return

    (flip_supported, name, availability, opstatus) = data

    yield get_snia_sml_opstatus(opstatus)
    yield get_snia_sml_availability(availability)
    yield Result(
        state=State.OK,
        summary=f"Name: {name}"
    )
    yield get_snia_sml_changer_devices_flip_supported(flip_supported)


register.check_plugin(
    name="snia_sml_changer_devices",
    service_name="Changer device %s",
    discovery_function=discovery_snia_sml_changer_devices,
    check_function=check_snia_sml_changer_devices,
)

