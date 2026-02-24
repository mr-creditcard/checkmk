#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_winperf_if_files(conf: str) -> FileGenerator:
    if conf == "ps1":
        yield Plugin(base_os=OS.WINDOWS, source=Path("windows_if.ps1"))
        return
    if conf == "bat":
        yield Plugin(base_os=OS.WINDOWS, source=Path("wmic_if.bat"))


register.bakery_plugin(
    name="winperf_if",
    files_function=get_winperf_if_files,
)
