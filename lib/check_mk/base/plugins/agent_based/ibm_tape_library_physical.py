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
#.1.3.6.1.4.1.3764.1.10.10.14.1.0 1
#.1.3.6.1.4.1.3764.1.10.10.14.2.0 2
#.1.3.6.1.4.1.3764.1.10.10.14.3.0 3

#.
#  .--Physical Library---------------------------------------------------------------.
#  |    ____  _               _           _   _     _ _                              |
#  |   |  _ \| |__  _   _ ___(_) ___ __ _| | | |   (_) |__  _ __ __ _ _ __ _   _     |
#  |   | |_) | '_ \| | | / __| |/ __/ _` | | | |   | | '_ \| '__/ _` | '__| | | |    |
#  |   |  __/| | | | |_| \__ \ | (_| (_| | | | |___| | |_) | | | (_| | |  | |_| |    |
#  |   |_|   |_| |_|\__, |___/_|\___\__,_|_| |_____|_|_.__/|_|  \__,_|_|   \__, |    |
#  |                |___/                                                  |___/     |
#  +---------------------------------------------------------------------------------+
#  |                                  main check                                     |
#  '---------------------------------------------------------------------------------'

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


def parse_ibm_tape_library_physical(string_table):
    section = {}
    map_online_state = {
            '1' :   (0, 'online'),
            '2' :   (1, 'online pending'),
            '3' :   (2, 'offline'),
            '4' :   (1, 'offline pending'),
            '5' :   (1, 'shutdown pending'),
    }

    map_door_status = {
            '1' :   (1, 'Library door: open'),
            '2' :   (0, 'Library door: closed'),
            '3' :   (3, 'Library door: unknown'),
    }

    map_ie_door_status = {
            '1' :   (1, 'Import export door: opened'),
            '2' :   (0, 'Import export door: closed and locked'),
            '3' :   (0, 'Import export door: closed and unlocked'),
    }

    online_status, door_status, ie_door_status = string_table[0]
    section.update({
        'online_status'     :   map_online_state.get(online_status, (3, 'unknown')),
        'door_status'       :   map_door_status.get(door_status, (3, 'unknown')),
        'ie_door_status'    :   map_ie_door_status.get(ie_door_status, (3, 'unknown')),
    })
    return section


register.snmp_section(
    name="ibm_tape_library_physical",
    parse_function=parse_ibm_tape_library_physical,
    detect=all_of(exists(".1.3.6.1.4.1.3764.1.10.10.1.1.0"), contains(".1.3.6.1.2.1.1.1.0", ".1.3.6.1.4.1.8072.3.2.10")),
    fetch=[
        SNMPTree(
          base=".1.3.6.1.4.1.3764.1.10.10.14",
          oids=[
              '1',    #physicalLibraryState
              '2',    #aggregatedMainDoorStatus
              '3',    #aggregatedIEDoorStatus
          ]),
    ]
)


def discovery_ibm_tape_library_physical(section):
    if section:
        yield Service()


def check_ibm_tape_library_physical(section):
    if section is None:
        return

    status, statustext = parsed['online_status']
    yield Result(state=State(status), summary=statustext)



register.check_plugin(
    name="ibm_tape_library_physical",
    service_name="Online status",
    discovery_function=discovery_ibm_tape_library_physical,
    check_function=check_ibm_tape_library_physical,
)

#  .--doors-----------------------------------------------------------------------.
#  |                          _                                                   |
#  |                       __| | ___   ___  _ __ ___                              |
#  |                      / _` |/ _ \ / _ \| '__/ __|                             |
#  |                     | (_| | (_) | (_) | |  \__ \                             |
#  |                      \__,_|\___/ \___/|_|  |___/                             |
#  |                                                                              |
#  '------------------------------------------------------------------------------'

def check_ibm_tape_library_physical_doors(section):
    door_status, door_statustext = parsed['door_status']
    ie_door_status, ie_door_statustext = parsed['ie_door_status']
    yield Result(state=State(door_status), summary=door_statustext)
    yield Result(state=State(ie_door_status), summary=ie_door_statustext)

register.check_plugin(
    name="ibm_tape_library_physical_doors",
    service_name="Door status",
    discovery_function=discovery_ibm_tape_library_physical,
    check_function=check_ibm_tape_library_physical_doors,
)





