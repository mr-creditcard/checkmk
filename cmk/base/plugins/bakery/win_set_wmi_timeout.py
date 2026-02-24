#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from .bakery_api.v1 import (
    register,
    WindowsConfigContent,
    WindowsConfigEntry,
    WindowsConfigGenerator,
)


def get_win_set_wmi_timeout_windows_config(conf: WindowsConfigContent) -> WindowsConfigGenerator:
    yield WindowsConfigEntry(path=["global", "wmi_timeout"], content=conf)


register.bakery_plugin(
    name="win_set_wmi_timeout",
    windows_config_function=get_win_set_wmi_timeout_windows_config,
)
