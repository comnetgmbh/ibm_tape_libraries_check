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
#.1.3.6.1.4.1.3764.1.10.10.12.1.0 1
#.1.3.6.1.4.1.3764.1.10.10.12.2.0 1
#.1.3.6.1.4.1.3764.1.10.10.12.3.0 1
#.1.3.6.1.4.1.3764.1.10.10.12.4.0 1
#.1.3.6.1.4.1.3764.1.10.10.12.5.0 1
#.1.3.6.1.4.1.3764.1.10.10.12.6.0 1
#.1.3.6.1.4.1.3764.1.10.10.12.7.0 1

from .agent_based_api.v1 import (
    SNMPTree,
    register,
    Service,
    Result,
    State,
    all_of,
    contains,
    exists,
    OIDEnd,
)


def parse_ibm_tape_library_system(string_table):
    section = {}
    map_subsystem_status = {
        '1' :   (0, 'good'),
        '2' :   (2, 'failed'),
        '3' :   (1, 'degraded'),
        '4' :   (1, 'warning'),
        '5' :   (0, 'informational'),
        '6' :   (3, 'unknown'),
        '7' :   (2, 'invalid'),
    }
    parsed = {}
    for index, subsystem in enumerate(['Power', 'Cooling', 'Control', 'Connectivity', 'Robotics', 'Media', 'Drive']):
        section.update({subsystem: map_subsystem_status.get(info[0][index], (3, 'unknown'))})
    return section


register.snmp_section(
    name="ibm_tape_library_system",
    parse_function=parse_ibm_tape_library_system,
    detect=all_of(exists(".1.3.6.1.4.1.3764.1.10.10.1.1.0"), contains(".1.3.6.1.2.1.1.1.0", ".1.3.6.1.4.1.8072.3.2.10")),
    fetch=[
        SNMPTree(
          base=".1.3.6.1.4.1.3764.1.10.10.12",
          oids=[
		'1',    #powerStatus
		'2',    #coolingStatus
		'3',    #coolingStatus
		'4',    #connectivityStatus
		'5',    #roboticsStatus
		'6',    #mediaStatus
		'7',    #driveStatus
          ]),
    ]
)


def discovery_ibm_tape_library_system(section):
    for subsystem in section.keys():
        yield Service(item=subsystem)


def check_ibm_tape_library_system(item, section):
    if section is None:
        return

    status, statustext = parsed.get(item)
    yield Result(state=State(status), summary=statustext)



register.check_plugin(
    name="ibm_tape_library_system",
    service_name="%s status",
    discovery_function=discovery_ibm_tape_library_system,
    check_function=check_ibm_tape_library_system,
)






