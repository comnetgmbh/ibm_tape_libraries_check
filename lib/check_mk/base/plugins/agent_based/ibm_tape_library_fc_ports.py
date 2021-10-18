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
    exists,
    OIDEnd,
)


def parse_ibm_tape_library_fc_ports(string_table):
    section = {}
    ibm_fc_port_types = {
        '1' :   'nPort',
        '2' :   'nlPort',
        '3' :   'fPort',
        '4' :   'flPort',
        '5' :   'unknown',
    }

    ibm_fc_port_speed = {
        '1' :   'auto',
        '2' :   '1 Gbps',
        '3' :   '2 Gbps',
        '4' :   '4 Gbps',
        '5' :   '8 Gbps',
    }

    for index, port_type, wwpn, neg_speed in string_table:
        section.update({
            index : {
                'port_type' : ibm_fc_port_types.get(port_type, 'unknown'),
                'wwpn'      : wwpn,
                'neg_speed' : ibm_fc_port_speed.get(neg_speed, 'unknown'),
        }})
    return section


register.snmp_section(
    name="ibm_tape_library_fc_ports",
    parse_function=parse_ibm_tape_library_fc_ports,
    detect=all_of(exists(".1.3.6.1.4.1.3764.1.10.10.1.1.0"), contains(".1.3.6.1.2.1.1.1.0", ".1.3.6.1.4.1.8072.3.2.10")),
    fetch=[
        SNMPTree(
          base=".1.3.6.1.4.1.3764.1.10.10.15.1.1",
          oids=[
              OIDEnd(),
              '2',    #fcPortType
              '4',    #fcPortWWPortName
              '8',    #fcPortNegotiatedSpeed
          ]),
    ]
)


def discovery_ibm_tape_library_fc_ports(section):
    for index in section:
        yield Service(item=index)


def check_ibm_tape_library_fc_ports(item, section):
    data = section.get(item)
    if data is None:
        return

    yield Result(state=State.OK, summary='Port type: %s, Worldwide port name: %s, Negotiated speed: %s' % \
                (data['port_type'], data['wwpn'], data['neg_speed']))



register.check_plugin(
    name="ibm_tape_library_fc_ports",
    service_name="FC Port %s",
    discovery_function=discovery_ibm_tape_library_fc_ports,
    check_function=check_ibm_tape_library_fc_ports,
)

