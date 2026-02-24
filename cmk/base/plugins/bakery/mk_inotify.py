#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# mypy: disable-error-code="type-arg"

from collections.abc import Iterable, Sequence
from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_mk_inotify_files(conf: Sequence) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("mk_inotify.py"))

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=list(_get_mk_inotify_config(conf)),
        target=Path("mk_inotify.cfg"),
        include_header=True,
    )


def _get_mk_inotify_config(conf: Sequence) -> Iterable[str]:
    heartbeat_timeout, stats_interval, stats_messages, stats_retention, file_cfg = conf

    yield from [
        "[global]",
        "heartbeat_timeout=%d" % heartbeat_timeout,
        "write_interval=%d" % stats_interval,
        "max_messages_per_interval=%d" % stats_messages,
        "stats_retention=%d" % stats_retention,
        "",
    ]

    for entry in file_cfg:
        if len(entry) == 2:  # a folder
            yield "[%s]" % entry[0]
        else:
            yield "[{}|{}]".format(entry[0], "|".join(entry[1]))

        operations = entry[-1]
        for operation in operations:
            yield "%s=1" % operation


register.bakery_plugin(
    name="mk_inotify",
    files_function=get_mk_inotify_files,
)
