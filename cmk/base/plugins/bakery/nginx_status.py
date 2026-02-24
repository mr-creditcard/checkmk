#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from pathlib import Path
from pprint import pformat
from typing import Any

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_nginx_status_files(conf: Any) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("nginx_status.py"))

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=_get_nginx_status_config(conf),
        target=Path("nginx_status.cfg"),
        include_header=True,
    )


def _get_nginx_status_config(conf: Any) -> list[str]:
    if conf[0] == "static":
        return ["servers = %s" % pformat(conf[1])]
    return ["ssl_ports = %r" % conf[1]]


register.bakery_plugin(
    name="nginx_status",
    files_function=get_nginx_status_files,
)
