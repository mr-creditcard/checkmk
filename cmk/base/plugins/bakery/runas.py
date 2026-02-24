#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, PluginConfig, register


def get_runas_files(conf: list[tuple[str, str, str]]) -> FileGenerator:
    yield PluginConfig(
        base_os=OS.LINUX,
        lines=_get_runas_config(conf),
        target=Path("runas.cfg"),
        include_header=True,
    )


def _get_runas_config(conf: list[tuple[str, str, str]]) -> list[str]:
    return [f"{what:<8} {user or '-':<16} {path}" for what, user, path in conf]


register.bakery_plugin(
    name="runas",
    files_function=get_runas_files,
)
