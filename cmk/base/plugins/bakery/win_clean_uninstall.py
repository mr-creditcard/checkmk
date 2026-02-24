#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from typing import Any

from .bakery_api.v1 import register, WindowsConfigGenerator, WindowsSystemConfigEntry


def get_win_clean_uninstall_windows_config(conf: Any) -> WindowsConfigGenerator:
    yield WindowsSystemConfigEntry(name="cleanup_uninstall", content=conf)


register.bakery_plugin(
    name="win_clean_uninstall",
    windows_config_function=get_win_clean_uninstall_windows_config,
)
