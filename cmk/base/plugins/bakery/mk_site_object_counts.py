#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_mk_site_object_counts_files(conf: dict[str, Any]) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("mk_site_object_counts"))

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=list(_get_mk_site_object_counts_config(conf)),
        target=Path("site_object_counts.cfg"),
        include_header=True,
    )


def _get_mk_site_object_counts_config(conf: dict[str, Any]) -> Iterable[str]:
    for title in ["TAGS", "SERVICE_CHECK_COMMANDS"]:
        try:
            yield "{}={}".format(title, " ".join(conf[title.lower()]))
        except KeyError:
            pass

    sites = []
    for sitename, tags, service_check_commands in conf.get("sites", []):
        sites.append(sitename)
        for title, keys in [("TAGS", tags), ("SERVICE_CHECK_COMMANDS", service_check_commands)]:
            if keys:
                yield "{}_{}={}".format(title, sitename, " ".join(keys))
    if sites:
        yield "SITES=%s" % " ".join(sites)


register.bakery_plugin(
    name="mk_site_object_counts",
    files_function=get_mk_site_object_counts_files,
)
