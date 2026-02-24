#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from pathlib import Path
from shlex import quote
from typing import Any

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_mk_saprouter_files(conf: dict[str, Any]) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("mk_saprouter"), interval=conf.get("interval"))

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=_get_mk_saprouter_config(conf),
        target=Path("saprouter.cfg"),
        include_header=True,
    )


def _get_mk_saprouter_config(conf: dict[str, Any]) -> list[str]:
    return [
        "SAPROUTER_USER=%s" % quote(conf["user"]),
        "SAPGENPSE_PATH=%s" % quote(conf["path"]),
    ]


register.bakery_plugin(
    name="mk_saprouter",
    files_function=get_mk_saprouter_files,
)
