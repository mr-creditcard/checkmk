#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# mypy: disable-error-code="type-arg"

from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Literal, TypedDict

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register

PLUGIN_ONLY = "plugin_only"
WITH_CONFIGURATION = "with_configuration"


class MkFilestatsConfig(TypedDict, total=False):
    deployment: None | Literal["plugin_only", "with_configuration"]
    DEFAULT: Mapping
    subgroups_delimiter: str
    sections: Sequence[Mapping]


def get_mk_filestats_files(conf: MkFilestatsConfig) -> FileGenerator:
    if (deployment := conf.get("deployment")) is None:
        return

    for base_os in (OS.LINUX, OS.SOLARIS):
        yield Plugin(base_os=base_os, source=Path("mk_filestats.py"))

    if deployment == PLUGIN_ONLY:
        return

    sections = conf.get("sections", [])
    default = conf.get("DEFAULT", {})
    if not (default or sections):
        return
    lines = list(
        _get_mk_filestats_config(
            sections,
            default,
            conf.get("subgroups_delimiter", "@"),
        )
    )

    for base_os in (OS.LINUX, OS.SOLARIS):
        yield PluginConfig(
            base_os=base_os,
            lines=lines,
            target=Path("filestats.cfg"),
            include_header=True,
        )


def _get_mk_filestats_config(
    sections: Sequence[Mapping],
    default: Mapping,
    subgroups_delimiter: str = "@",
) -> Iterable[str]:
    yield "[DEFAULT]"
    yield "subgroups_delimiter: %s" % subgroups_delimiter
    for option in default.items():
        if option[0] == "grouping":
            yield from _parse_grouping_options(
                "DEFAULT",
                subgroups_delimiter,
                option[1],
            )
            continue
        yield "%s: %s" % option

    yield ""

    for section in sections:
        yield "[%s]" % section["name"]
        grouping_options = None
        for option in section.items():
            if option[0] == "grouping":
                grouping_options = option[1]
                continue
            if option[0] != "name":
                yield "%s: %s" % option

        if grouping_options:
            yield from _parse_grouping_options(
                section["name"],
                subgroups_delimiter,
                grouping_options,
            )

        yield ""


def _parse_grouping_options(
    section_name: str,
    subgroups_delimiter: str,
    grouping_options: list[tuple],
) -> Iterable[str]:
    for group_name, (option_type, rule) in grouping_options:
        # write out each grouping option as a separate section to config file
        # in order to make it more easily configurable for users who create
        # config files manually
        yield ""
        yield f"[{section_name}{subgroups_delimiter}{group_name}]"
        yield f"grouping_{option_type}: {rule}"


register.bakery_plugin(
    name="mk_filestats",
    files_function=get_mk_filestats_files,
)
