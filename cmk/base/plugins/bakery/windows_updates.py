#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_windows_updates_files(conf: bool) -> FileGenerator:
    if conf:
        yield Plugin(
            base_os=OS.WINDOWS,
            source=Path("windows_updates.ps1"),
            interval=3600 * 4,
            timeout=60 * 10,
            asynchronous=True,
        )


register.bakery_plugin(
    name="windows_updates",
    files_function=get_windows_updates_files,
)
