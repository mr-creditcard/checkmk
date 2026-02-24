#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
#
# Original author: thl-cmk[at]outlook[dot]com

from cmk.graphing.v1 import metrics, Title

metric_signal_power = metrics.Metric(
    name="signal_power",
    title=Title("Signal power"),
    unit=metrics.Unit(metrics.DecimalNotation("dBm")),
    color=metrics.Color.GREEN,
)
