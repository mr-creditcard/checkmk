#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Iterable
from pathlib import Path
from shlex import quote

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_dnsclient_files(conf: Iterable[str] | None) -> FileGenerator:
    for o_s in (OS.LINUX, OS.SOLARIS, OS.AIX):
        yield Plugin(base_os=o_s, source=Path("dnsclient"))

    if conf is not None:
        for o_s in (OS.LINUX, OS.SOLARIS, OS.AIX):
            yield PluginConfig(
                base_os=o_s,
                lines=_get_dnsclient_config_lines(conf),
                target=Path("dnsclient.cfg"),
                include_header=True,
            )


def _get_dnsclient_config_lines(conf: Iterable[str]) -> list[str]:
    return [
        "# Hostnames to test resolver with",
        "HOSTADDRESSES=%s" % quote(" ".join(conf)),
    ]


register.bakery_plugin(
    name="dnsclient",
    files_function=get_dnsclient_files,
)
