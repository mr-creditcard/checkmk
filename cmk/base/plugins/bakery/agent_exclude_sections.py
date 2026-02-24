#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterable
from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, PluginConfig, register


def get_agent_exclude_sections_files(conf: dict[str, list[str]] | None) -> FileGenerator:
    if not conf:
        return
    yield PluginConfig(
        base_os=OS.LINUX,
        lines=list(get_agent_exclude_section_lines(conf["sections"])),
        target=Path("exclude_sections.cfg"),
        include_header=True,
    )


def get_agent_exclude_section_lines(excluded_sections_list: list[str]) -> Iterable[str]:
    exclude_name = "MK_SKIP_%s=yes"
    for section_name in excluded_sections_list:
        yield exclude_name % section_name.upper()


register.bakery_plugin(
    name="agent_exclude_sections",
    files_function=get_agent_exclude_sections_files,
)
