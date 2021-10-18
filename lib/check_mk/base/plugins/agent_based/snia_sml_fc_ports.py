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
# .1.3.6.1.4.1.14851.3.1.15.2.1.1.1 = INTEGER: 1
# .1.3.6.1.4.1.14851.3.1.15.2.1.2.1 = STRING: "500507630F522101"
# .1.3.6.1.4.1.14851.3.1.15.2.1.3.1 = STRING: "IBM     03592E07        000X123456 Port 0"
# .1.3.6.1.4.1.14851.3.1.15.2.1.4.1 = STRING: "IBM     03592E07        000X123456 Port 0"
# .1.3.6.1.4.1.14851.3.1.15.2.1.5.1 = STRING: "IBM     03592E07        000X123456 Port 0"
# .1.3.6.1.4.1.14851.3.1.15.2.1.6.1 = INTEGER: 2
# .1.3.6.1.4.1.14851.3.1.15.2.1.7.1 = STRING: "500507630F522101"
# .1.3.6.1.4.1.14851.3.1.15.2.1.8.1 = INTEGER: 1

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
)


def parse_snia_sml_fc_ports(string_table):
    section = {}
    for index, *data in string_table[0]:
        section[index] = data
    return section


register.snmp_section(
    name="snia_sml_fc_ports",
    parse_function=parse_snia_sml_fc_ports,
    detect=contains(".1.3.6.1.2.1.1.1.0", ".1.3.6.1.4.1.2.6.182"),
    fetch=[
        SNMPTree(
          base=".1.3.6.1.4.1.14851.3.1.15.2.1",
          oids=[
              "1", # fCPortIndex
              "6", # fCPortController-OperationalStatus
              "7", # fCPort-PermanentAddress
              "8", # fCPort-Realizes-scsiProtocolControllerIndex
          ]),
    ]
)


def discovery_snia_sml_fc_ports(section):
    for index in section:
        yield Service(item=index)


def check_snia_sml_fc_ports(item, section):
    data = section.get(item)
    if data is None:
        return

    (opstatus, address, scsi_controller) = data

    yield get_snia_sml_opstatus(opstatus)
    yield Result(
        state=State.OK,
        summary=f"Worldwide port name: {address}, SCSI Controller: {scsi_controller}"
    )


register.check_plugin(
    name="snia_sml_fc_ports",
    service_name="FC Port %s",
    discovery_function=discovery_snia_sml_fc_ports,
    check_function=check_snia_sml_fc_ports,
)

