#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_apache_status_files(conf: list[str]) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("apache_status.py"))

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=get_apache_status_lines(conf),
        target=Path("apache_status.cfg"),
        include_header=True,
    )


def get_apache_status_lines(conf: list[str]) -> list[str]:
    if conf[0] == "static":
        return ["servers = %r" % conf[1]]
    return ["ssl_ports = %r" % conf[1]]


register.bakery_plugin(
    name="apache_status",
    files_function=get_apache_status_files,
)
