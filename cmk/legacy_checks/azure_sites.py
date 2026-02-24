#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# mypy: disable-error-code="no-untyped-def"


import time
from collections.abc import Mapping

from cmk.agent_based.legacy.v0_unstable import check_levels, LegacyCheckDefinition, LegacyResult
from cmk.agent_based.v2 import (
    get_rate,
    get_value_store,
    IgnoreResultsError,
    render,
    Service,
)
from cmk.plugins.azure.lib import (
    get_service_labels_from_resource_tags,
    iter_resource_attributes,
    parse_resources,
    Resource,
)

check_info = {}

_AZURE_SITES_METRICS = (  # metric_key, cmk_key, display_name, use_rate_flag
    ("total_CpuTime", "cpu_time_percent", "CPU time", True),
    ("total_AverageResponseTime", "avg_response_time", "Average response time", False),
    ("total_Http5xx", "error_rate", "Rate of server errors", True),
)

_AZURE_METRIC_FMT = {
    "count": lambda n: "%d" % n,
    "percent": render.percent,
    "bytes": render.bytes,
    "bytes_per_second": render.iobandwidth,
    "seconds": lambda s: "%.2f s" % s,
    "milli_seconds": lambda ms: "%d ms" % (ms * 1000),
    "milliseconds": lambda ms: "%d ms" % (ms * 1000),
}


def _get_data_or_go_stale[D](item: str, section: Mapping[str, D]) -> D:
    if resource := section.get(item):
        return resource
    raise IgnoreResultsError("Data not present at the moment")


def _check_azure_metric(
    resource: Resource,
    metric_key: str,
    cmk_key: str,
    display_name: str,
    levels: tuple[float, float] | None = None,
    levels_lower: tuple[float, float] | None = None,
    use_rate: bool = False,
) -> None | LegacyResult:
    metric = resource.metrics.get(metric_key)
    if metric is None:
        return None

    if use_rate:
        countername = f"{resource.id}.{metric_key}"
        value = get_rate(
            get_value_store(), countername, time.time(), metric.value, raise_overflow=True
        )
        unit = "%s_rate" % metric.unit
    else:
        value = metric.value
        unit = metric.unit

    # not sure if we can trust the types here.
    if value is None:  # type: ignore[comparison-overlap]
        return 3, "Metric %s is 'None'" % display_name, []  # type: ignore[unreachable]

    # convert to SI-unit
    if unit in ("milli_seconds", "milliseconds"):
        value /= 1000.0
    elif unit == "seconds_rate":
        # we got seconds, but we computed the rate -> seconds per second:
        # how long happend something / time period = percent of the time
        # e.g. CPU time: how much percent of of the time was the CPU busy.
        value *= 100.0
        unit = "percent"

    return check_levels(
        value,
        cmk_key,
        (levels or (None, None)) + (levels_lower or (None, None)),
        infoname=display_name,
        human_readable_func=_AZURE_METRIC_FMT.get(unit, lambda x: f"{x}"),
        boundaries=(0, None),
    )


def check_azure_sites(item, params, section):
    resource = _get_data_or_go_stale(item, section)
    for key, cmk_key, displ, use_rate in _AZURE_SITES_METRICS:
        levels = params.get("%s_levels" % cmk_key, (None, None))
        mcheck = _check_azure_metric(
            resource, key, cmk_key, displ, levels=levels, use_rate=use_rate
        )
        if mcheck:
            yield mcheck

    for kv_pair in iter_resource_attributes(resource):
        yield 0, "%s: %s" % kv_pair


def discover_azure_sites(section):
    yield from (
        Service(item=item, labels=get_service_labels_from_resource_tags(resource.tags))
        for item, resource in section.items()
    )


check_info["azure_sites"] = LegacyCheckDefinition(
    name="azure_sites",
    parse_function=parse_resources,
    service_name="Site %s",
    discovery_function=discover_azure_sites,
    check_function=check_azure_sites,
    check_ruleset_name="webserver",
    check_default_parameters={
        # https://www.nngroup.com/articles/response-times-3-important-limits/
        "avg_response_time_levels": (1.0, 10.0),
        # https://www.unigma.com/2016/07/11/best-practices-for-monitoring-microsoft-azure/
        "error_rate_levels": (0.01, 0.04),
        "cpu_time_percent_levels": (85.0, 95.0),
    },
)
