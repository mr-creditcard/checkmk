#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from pathlib import Path
from typing import Any

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_win_dhcp_pools_files(conf: Any) -> FileGenerator:
    yield Plugin(base_os=OS.WINDOWS, source=Path("win_dhcp_pools.bat"))


register.bakery_plugin(
    name="win_dhcp_pools",
    files_function=get_win_dhcp_pools_files,
)
