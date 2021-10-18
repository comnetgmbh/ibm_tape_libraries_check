#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2018             mk@mathias-kettner.de |
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

def get_snia_sml_availability(value):
    result = {
        "1":  (2, 'other'),
        "2":  (1, 'unknown'),
        "3":  (0, 'runningFullPower'),
        "4":  (1, 'warning'),
        "5":  (0, 'inTest'),
        "6":  (0, 'notApplicable'),
        "7":  (2, 'powerOff'),
        "8":  (2, 'offLine'),
        "9":  (0, 'offDuty'),
        "10": (1, 'degraded'),
        "11": (1, 'notInstalled'),
        "12": (2, 'installError'),
        "13": (2, 'powerSaveUnknown'),
        "14": (0, 'powerSaveLowPowerMode'),
        "15": (0, 'powerSaveStandby'),
        "16": (0, 'powerCycle'),
        "17": (1, 'powerSaveWarning'),
        "18": (1, 'paused'),
        "19": (1, 'notReady'),
        "20": (2, 'notConfigured'),
        "21": (0, 'quiesced'),
    }.get(value, (3, 'unimplemented'))
    return Result(state=State(result[0]), summary='Availability: ' + result[1])


def get_snia_sml_opstatus(value):
    result = {
        "0":      (2, 'unknown'),
        "1":      (1, 'other'),
        "2":      (0, 'ok'),
        "3":      (1, 'degraded'),
        "4":      (1, 'stressed'),
        "5":      (1, 'predictiveFailure'),
        "6":      (2, 'error'),
        "7":      (2, 'non-RecoverableError'),
        "8":      (1, 'starting'),
        "9":      (1, 'stopping'),
        "10":     (2, 'stopped'),
        "11":     (1, 'inService'),
        "12":     (1, 'noContact'),
        "13":     (2, 'lostCommunication'),
        "14":     (1, 'aborted'),
        "15":     (1, 'dormant'),
        "16":     (1, 'supportingEntityInError'),
        "17":     (0, 'completed'),
        "18":     (0, 'powerMode'),
        "19":     (1, 'dMTFReserved'),
        "32768":  (1, 'vendorReserved'),
    }.get(value, (3, 'unimplemented'))
    return Result(state=State(result[0]), summary='Status: ' + result[1])
