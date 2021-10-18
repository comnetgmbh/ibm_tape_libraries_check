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
# storageMediaLocation-PhysicalMedia-CleanerMedia
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.1 2
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.2 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.3 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.4 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.5 2
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.6 2
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.7 2
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.8 2
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.9 2
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.10 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.11 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.12 2
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.13 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.14 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.15 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.16 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.17 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.18 0
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.19 1
# .1.3.6.1.4.1.14851.3.1.13.3.1.17.20 0

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

# A value of 1 means there is a cleaning cartridge. Value 2 means there is another cartridge type. Value 0 means there is no cartridge at all.

snia_sml_cleaningcartridges_default_levels = {
    'levels': (7, 5),
}


def parse_snia_sml_cleaningcartridges(string_table):
    return string_table


register.snmp_section(
    name="snia_sml_cleaningcartridges",
    parse_function=parse_snia_sml_cleaningcartridges,
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


def discovery_snia_sml_cleaningcartridges(section):
    if len(section) > 0:
        yield Service(item=index)


def check_snia_sml_cleaningcartridges(params, section):
    for i in range(0, len(section)):
        state = section[i][0]
        if state == '1':
            total_cleaning_cartridges += 1

    yield Metric('cartridges', total_cleaning_cartridges, levels=(warn, crit))
    message = 'Total cleaning cartridges: %s' % total_cleaning_cartridges
    notice = ' (warn/crit at %d/%d)' % (warn, crit)
    if crit and total_cleaning_cartridges <= crit:
        yield Result(state=State.CRIT, summary=message, notice=notice)
    elif warn and total_cleaning_cartridges <= warn:
        yield Result(state=State.WARN, summary=message, notice=notice)
    else:
        yield Result(state=State.OK, summary=message, notice=notice)


register.check_plugin(
    name="snia_sml_cleaningcartridges",
    service_name="Cleaning Cartridges",
    discovery_function=discovery_snia_sml_cleaningcartridges,
    check_function=check_snia_sml_cleaningcartridges,
    check_ruleset_name="cleaning_cartridges",
    check_default_parameters=snia_sml_cleaningcartridges_default_levels,
)

