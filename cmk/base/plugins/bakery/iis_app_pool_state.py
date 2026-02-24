#!/usr/bin/env python3
# Copyright (C) 2021 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_iis_app_pool_state_files(conf: bool) -> FileGenerator:
    if conf:
        yield Plugin(base_os=OS.WINDOWS, source=Path("iis_app_pool_state.ps1"))


register.bakery_plugin(
    name="iis_app_pool_state",
    files_function=get_iis_app_pool_state_files,
)
