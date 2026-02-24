#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_netstat_files(conf: dict[str, int]) -> FileGenerator:
    for base_os in (OS.LINUX, OS.AIX):
        yield Plugin(
            base_os=base_os,
            source=Path(f"netstat.{base_os}"),
            target=Path("netstat"),
            interval=conf.get("interval"),
        )

    yield Plugin(
        base_os=OS.WINDOWS,
        source=Path("netstat_an.bat"),
        interval=conf.get("interval"),
        asynchronous=True,
    )


register.bakery_plugin(
    name="netstat",
    files_function=get_netstat_files,
)
