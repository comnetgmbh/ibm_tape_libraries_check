#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

metric_info["cartridges"] = {
    "title" : _("Cleaning cartridges"),
    "unit"  : "count",
    "color" : "46/a",
}

perfometer_info.append({
    "type"          : "logarithmic",
    "metric"        : "cartridges",
    "half_value"    : 15,
    "exponent"      : 2
})
