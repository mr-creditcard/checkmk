#!/usr/bin/env python3
# Copyright (C) 2022 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_nvidia_smi_files(conf: dict[str, str]) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("nvidia_smi"))
    yield Plugin(base_os=OS.WINDOWS, source=Path("nvidia_smi.ps1"))
    yield PluginConfig(
        base_os=OS.WINDOWS,
        lines=_get_config_lines(conf),
        target=Path("nvidia_smi_cfg.ps1"),
        include_header=True,
    )


def _get_config_lines(conf: dict[str, str]) -> list[str]:
    return [f"${key} = '{value}'" for key, value in conf.items()]


register.bakery_plugin(
    name="nvidia_smi",
    files_function=get_nvidia_smi_files,
)
